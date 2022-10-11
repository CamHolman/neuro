"""
RAM Loading Functions.

Aggregate information aquired during the RAM Project (Restoring Active Memory - DARPA). Info is loaded
from CMLReaders (Computational Memory Lab - Univeristy of Pensylvania). Functions include:

load_subject_ids(task)
load_events_info(task, subject, montage)
load_electrode_info(subject, montage)
laod_stimulation_info(events_df, electrodes_df)
load_eeg()
load_events_eeg()


"""
from cmlreaders import CMLReader, get_data_index
import pandas as pd
import numpy as np
import os 
from glob import glob 
from joblib import Parallel, delayed

# Get RAM Index for CMLReaders
try:
    r1_data = get_data_index("r1")
except KeyError:
    print('r1 protocol file not found')


# -- Functions -- 
def load_subject_ids(task):
    """Returns a DataFrame with columns 'subject' and 'montage' listing participants in a given experiment.

    Parameters
    ----------
    task: str
        The experiment name (ex: TH1, FR1, ...).

    Returns
    -------
    pandas.DataFrame
        A DataFrame of all subjects who performed the task.
    """

    # if this is RAM task, load the subject/montage directly from the r1 database
    task = task.replace('RAM_', '')
    if task in r1_data.experiment.unique():
        df = r1_data[r1_data['experiment'] == task][['subject', 'montage']].drop_duplicates().reset_index(drop=True)

    # otherwise, need to look for *events.mat files in '/data/events/task
    else:
        subj_list = []
        mont_list = []
        subjs = glob(os.path.join('/data/events/', task, '*_events.mat'))
        subjs = [os.path.split(f.replace('_events.mat', ''))[1] for f in subjs]
        subjs.sort()
        for subj in subjs:
            m = 0
            if '_' in subj:
                subj_split = subj.split('_')
                if len(subj_split[-1]) == 1:
                    m = int(subj_split[-1])
                    subj = subj[:-2]
            subj_list.append(subj)
            mont_list.append(m)
        df = pd.DataFrame({'subject': np.array(subj_list, dtype=object), 'montage': np.array(mont_list, dtype=int)})
    return df


def load_events_info(subject, task, montage, as_df=True, remove_no_eeg=False):
    """
    Returns a DataFrame of a subjects Events (label, time, metadata, ...) 
    Event labels can include: 
        'WORD'     : word presentation, stimulation
        'STIM_ON'  : stimulation started
        'STIM_OFF' : stimulation ended
        ...


    Parameters
    ----------
    task: str
        The experiment name (ex: RAM_TH1, RAM_FR1, ...).
    subject: str
        The subject code
    montage: int
        The montage number for the subject
    as_df: bool
        If true, the events will returned as a pandas.DataFrame, otherwise a numpy.recarray
    remove_no_eeg: bool
        If true, an events with missing 'eegfile' info will be removed. Recommended when you are doing EEG analyses

    Returns
    -------
    pandas.DataFrame
        A DataFrame of of the events
    """
    # Format
    task = task.replace('RAM_', '')

    # Get sessions
    inds = (r1_data['subject'] == subject) & (r1_data['experiment'] == task) & (r1_data['montage'] == int(montage))
    sessions = r1_data[inds]['session'].unique()

    # Load Events
    events = pd.concat([CMLReader(subject=subject, experiment=task, session=session).load('events')
                        for session in sessions])

    # Options
    if remove_no_eeg:
        events = events[events.eegfile.apply(len) > 0]
    if not as_df:
        events = events.to_records(index=False)
    
    return events


def load_electrode_info(subject, montage=0, bipolar=True):

    """
    Loads electrode info for subject from CML
    original author: Jonathan Miller

    Parameters
    ----------
    subject: str
        subject code
    montage: int
        montage number
    bipolar: bool
        whether to return electrode info for bipolar or monopolar electrode configuration

    Returns
    -------
    pandas.DataFrame
        A DataFrame of of the electrode information

    """

    ############################################################
    # custom loading functions for different types of old data #
    # this code used to be so much nicer before this :(        #
    ############################################################
    def load_loc_from_subject_tal_file(tal_path):
        """
        Load a subject's talaraich matlab file.
        """
        elec_raw = loadmat(tal_path, squeeze_me=True)
        elec_raw = elec_raw[np.setdiff1d(list(elec_raw.keys()), ['__header__', '__version__', '__globals__'])[0]]

        # sume of the data is in subarrays, flatten it, and make dataframe. Eeessh
        # also rename some of the fields/columns
        # make average surface dataframe
        surf_data = []
        exclude = []
        if 'avgSurf' in elec_raw.dtype.names:
            avg_surf = pd.concat([pd.DataFrame(index=[i], data=e) for (i, e) in enumerate(elec_raw['avgSurf'])],
                                 sort=False)
            avg_surf = avg_surf.rename(columns={x: 'avg.{}'.format(x) for x in avg_surf.columns})
            surf_data.append(avg_surf)
            exclude.append('avgSurf')

        # make indiv surface dataframe
        if 'indivSurf' in elec_raw.dtype.names:
            ind_surf = pd.concat([pd.DataFrame(index=[i], data=e) for (i, e) in enumerate(elec_raw['indivSurf'])],
                                 sort=False)
            ind_surf = ind_surf.rename(columns={x: 'ind.{}'.format(x) for x in ind_surf.columns})
            surf_data.append(ind_surf)
            exclude.append('indivSurf')

        # concat them, excluding the original subarrays
        elec_df = pd.DataFrame.from_records(elec_raw, exclude=exclude)
        elec_df = pd.concat([elec_df] + surf_data, axis='columns')

        # add new columns for contacts, named the same as the json version
        if bipolar:
            elec_df['contact_1'], elec_df['contact_2'] = np.stack(elec_df['channel'], -1)
            elec_df.drop(columns='channel')
        return elec_df

    def load_loc_from_tal_GM_file(subj_mont):
        """
        Load master data file of older subject talairach info and return just this subject
        """
        tal_master_data = loadmat('/data/eeg/tal/allTalLocs_GM.mat', squeeze_me=True)['events']
        subj_tal = tal_master_data[tal_master_data['subject'] == subj_mont]
        return pd.DataFrame(subj_tal)

    def add_jacksheet_label(subj_mont):
        """
        Load the subject jacksheet in order to get the electrode labels
        """
        jacksheet_df = []
        f = os.path.join('/data/eeg', subj_mont, 'docs', 'jacksheet.txt')
        if os.path.exists(f):
            jacksheet_df = pd.read_table(f, header=None, names=['channel', 'label'], sep=' ')
            jacksheet_df['channel'] = jacksheet_df['channel'].astype(object)
        return jacksheet_df

    def add_depth_info(subj_mont):
        """
        Load the 'depth_el_info.txt' file in order to get depth elec localizations
        """
        depth_df = []
        f = os.path.join('/data/eeg', subj_mont, 'docs', 'depth_el_info.txt')
        if os.path.exists(f):
            contacts = []
            locs = []

            # can't just read it in with pandas bc they use spaces as a column sep as well as in values wtf
            with open(f, 'r') as depth_info:
                for line in depth_info:
                    line_split = line.split()

                    # formatting of these files is not very consistent
                    if len(line_split) > 2:

                        # this is a weak check, but make sure we can cast the first entry to an int
                        try:
                            contact = int(line_split[0])
                            contacts.append(contact)
                            locs.append(' '.join(line_split[2:]))
                        except ValueError:
                            pass
            depth_df = pd.DataFrame(data=[contacts, locs]).T
            depth_df.columns = ['channel', 'locs']
        return depth_df

    def add_neuroad_info(subj_mont):
        return

    #######################################
    # electrode loading logic begins here #
    #######################################

    # check if this subject/montage is in r1. If it is, use cmlreaders to load it. Easy.
    if np.any((r1_data['subject'] == subject) & (r1_data['montage'] == montage)):
        elec_df = CMLReader(subject=subject, montage=montage).load('pairs' if bipolar else 'contacts')

    # if not in r1 protocol, annoying, there are multiple possible locations for matlab data
    else:

        # Option 1: the subject as a talLoc.mat file within their own 'tal' directory
        subj_mont = subject
        if int(montage) != 0:
            subj_mont = subject + '_' + str(montage)
        file_str = '_bipol' if bipolar else '_monopol'
        tal_path = os.path.join('/data/eeg', subj_mont, 'tal', subj_mont + '_talLocs_database' + file_str + '.mat')

        if os.path.exists(tal_path):
            elec_df = load_loc_from_subject_tal_file(tal_path)

        # Option 2: there is no subject specific file, look in the older aggregate file. Lot's of steps.
        else:
            if bipolar:
                print('Bipolar not supported for {}.'.format(subject))
                return

            # load subject specific data from master file
            elec_df = load_loc_from_tal_GM_file(subj_mont)

            # add electrode type column
            e_type = np.array(['S'] * elec_df.shape[0])
            e_type[np.in1d(elec_df.montage, ['hipp', 'inf'])] = 'D'
            elec_df['type'] = e_type

            # add labels from jacksheet
            jacksheet_df = add_jacksheet_label(subj_mont)
            if isinstance(jacksheet_df, pd.DataFrame):
                elec_df = pd.merge(elec_df, jacksheet_df, on='channel', how='inner', left_index=False,
                                   right_index=False)

            # add depth_el_info (depth electrode localization)
            depth_el_info_df = add_depth_info(subj_mont)
            if isinstance(depth_el_info_df, pd.DataFrame):
                elec_df = pd.merge(elec_df, depth_el_info_df, on='channel', how='outer', left_index=False,
                                   right_index=False)

                # to do
                # also attempt to load additional information from the "neurorad_localization.txt" file, if exists

        # relabel some more columns to be consistent
        elec_df = elec_df.rename(columns={'channel': 'contact',
                                          'tagName': 'label',
                                          'eType': 'type'})

        if 'label' not in elec_df:
            elec_df['label'] = elec_df['contact'].apply(lambda x: 'elec_' + str(x))

    return elec_df


def load_stimulation_info(events_df, electrodes_df, on_off = 'OFF'):
    """
    Returns a DataFrame of sitmulation events and metadata (time, location, stim_params, ...)
    
    Parameters
    ----------
    events_info : Events DataFrame
        -> load_events_info()
    electrodes_info : Electrode DataFrame
        -> load_electrode_info()
    on_off : str
        Choose whether to filter by 'STIM_ON' or 'STIM_OFF' 
        Options: ['OFF', 'ON', 'BOTH']
    """
    # ON or OFF
    if on_off.upper() ==  'OFF':
        stim_events = events_df[events_df['type'] == 'STIM_OFF']
    elif on_off.upper() == 'ON':
        stim_events = events_df[events_df['type'] == 'STIM_OFF']
    else:
        stim_events = events_df[events_df['type'].isin(['STIM_ON', 'STIM_OFF'])]

    # Parralelized - Get stim data
    def load_single_stim(ievent, event, electrodes_df):
        # Get stim event data
        stim_params = event['stim_params'][0]
        eegoffset = event['eegoffset']
        mstime = event['mstime']

        # Get bipolar label
        anode = stim_params['anode_label']
        cathode = stim_params['cathode_label']
        bilabel = anode+'-'+cathode    
        
        # Get electrode & location data 
        electrode = electrodes_df[electrodes_df['label'] == bilabel]
        locs = []
        for colname in electrode.columns:
            if 'region' in colname:
                loc = electrode[colname].values[0]
                if type(loc) == str:
                    locs.append(loc)
        x, y, z = electrode['avg.x'].values[0], electrode['avg.y'].values[0], electrode['avg.z'].values[0]                   
        hemi = 'left' if x<0 else 'right'

        # Save
        res = {
            'electrode' : bilabel,
            'location' : locs,
            'hemi' : hemi,
            'x' : x,
            'y' : y,
            'z' : z,
            'event_index' : ievent,
            'event_name' : 'STIM_OFF',
            'mstime' : mstime,
            'eegoffset' : eegoffset
        }
        res.update(stim_params)
        return res

    res = Parallel(n_jobs = 12, verbose = 5)(delayed(load_single_stim)(ievent, event, electrodes_df) 
                                                     for ievent, event in stim_events.iterrows())

    # Make DF and return
    stim_df = pd.DataFrame()
    for stim_dict in res:
        stim_df = stim_df.append(stim_dict, ignore_index = True)
    return stim_df


def load_eeg(task, subject, session, elec_scheme):
    """
    Returns MNE... 
    """

    return CMLReader (subject = subject, experiment = task, session = session).load_eeg(scheme = elec_scheme)

