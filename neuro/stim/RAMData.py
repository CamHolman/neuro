# General
import pandas as pd
import numpy as np
import os 
from glob import glob  
from joblib import Parallel, delayed

# Penn Mem
from cmlreaders import CMLReader, get_data_index
from ptsa.data.filters import ButterworthFilter
from ptsa.data.filters import MorletWaveletFilter
from ptsa.data.filters import ResampleFilter
from ptsa.data.timeseries import TimeSeries

def load_subject_data(task, isubject):
    subjects = load_subject_ids(task)
    idsubject = subjects.iloc[isubject]['subject']
    imontage = subjects.iloc[isubject]['montage']

    subject = RAMSubjectData(task, idsubject, imontage)
    return subject
    
class RAMSubjectData:
    """
    Class for loading RAM subject data to analyze PS3 theta burst stimulation
    """
    def __init__(self, task, subject, montage):
        # Arguments
        self.task    = task
        self.subject = subject
        self.montage = montage

        # Data
        self.events      = None
        self.electrodes  = None
        self.electrodes_bipolar = None
        self.stimulation = None

        # Signal
        self.eeg = None
    
    def load_metadata(self):
        self.load_events_info(as_df=True, remove_no_eeg = True)
        self.load_electrode_info(bipolar = False)
        self.load_electrode_bipolar_info()
        self.load_stimulation_info(on_off = 'OFF')

    def load_events_info(self, as_df = True, remove_no_eeg = True):
        print(f'Loading events for subject {self.subject}, task {self.task}, montage {self.montage}')
        self.events = load_events_info(self.subject, self.task, self.montage, as_df, remove_no_eeg)
        print ('Done')

    def stimulation_events(self):
        pass

    def load_electrode_info(self, bipolar = False):
        print(f'Loading electrodes for subject {self.subject}, task {self.task}, montage {self.montage}')
        self.electrodes = load_electrode_info(self.subject, self.montage, bipolar)
        print ('Done')

    def load_electrode_bipolar_info(self):
        self.electrodes_bipolar = load_electrode_info(self.subject, self.montage, bipolar=True)

    def load_stimulation_info(self, on_off = 'OFF'):
        print(f'Loading stimulation info for subject {self.subject}, task {self.task}, montage {self.montage}')
        self.stimulation = load_stimulation_info(self.events, self.electrodes_bipolar, on_off)
        print('Done')

    def load_raw_eeg(self):
        self.eeg = load_raw_eeg (self.task,self.subject, 0, self.electrodes)
    
    def load_events_eeg(self, events = None, rel_start_ms = None, rel_stop_ms=None, buf_ms=0, elec_scheme=None, noise_freq=[58., 62.],
             resample_freq=None, pass_band=None, use_mirror_buf=False, demean=False, do_average_ref=False):
        
        if events is None:
            events = self.events
        if rel_start_ms is None:
            rel_start_ms = -500
        if rel_stop_ms is None:
            rel_stop_ms = 1500
        if elec_scheme is None:
            elec_scheme = self.electrodes

        self.eeg = load_events_eeg(events, rel_start_ms, rel_stop_ms, buf_ms, elec_scheme, noise_freq,
             resample_freq, pass_band, use_mirror_buf, demean, do_average_ref)

def load_ram_group_data(task):
    """
    Create RAMGroupData object for task
    """
    subjects = load_subject_ids(task)
    return RAMGroupData(task, subjects_and_montages=subjects)


class RAMGroupData:
    def __init__(self, task, subject_ids = None, montage_ids = None, subjects_and_montages = None):
        # Arguments
        self.task = task
        self.subject_ids = subject_ids
        self.montage_ids = montage_ids

        if isinstance(subjects_and_montages, pd.DataFrame):
            self.subject_ids = list(subjects_and_montages['subject'])
            self.montage_ids = list(subjects_and_montages['montage'])

        # Data
        self.subjects = None
        self.electrodes = None
        self.stimulation = None

        # Errors
        self.subject_errors = None

        # Options

    def load_subjects(self):
        # Parallelize load
        def load_subject(task, subject_id, montage_id):
            try:
                subject = RAMSubjectData(task, subject_id, montage_id)
                subject.load_events_info()
                subject.load_electrode_info()
                subject.load_stimulation_info()
            except Exception as e:
                subject = f'Subject {subject_id}, Montage {montage_id} | Error: {e}'
            return subject
        
        self.subjects = Parallel(n_jobs = 12, verbose = 5, backend='loky') \
            (delayed(load_subject)(self.task, subject, montage) 
            for subject, montage in zip(self.subject_ids, self.montage_ids))

        errors = [] 
        for subject in self.subjects:
            if type (subject) == str:
                errors.append(subject)
        
        print ('\n\nErrors occured loading these Subjects:')
        for error in errors:
            print('\t', error)
            self.subjects.remove(error)
        self.subject_errors = errors
        

    def group_electrode_info(self):
        subject_elec_dfs = []
        for s in self.subjects:
            subject_id = s.subject
            elec_info = s.electrodes.copy(deep=False)
            elec_info['subject'] = subject_id
            subject_elec_dfs.append(elec_info)
        self.electrodes = pd.concat(subject_elec_dfs)
    
    def group_stimulation_info(self):
        subject_stim_dfs = []
        for s in self.subjects:
            subject_id = s.subject
            stim_info = s.stimulation.copy(deep=False)
            stim_info['subject'] = subject_id
            subject_stim_dfs.append(stim_info)
        self.stimulation = pd.concat(subject_stim_dfs)

    
            

#---------------------
# RAM Load Functions

# Get the R1 index dataframe 
try:
    r1_data = get_data_index("r1")
except KeyError:
    print('r1 protocol file not found')

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
        locs = tuple(locs)

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




def load_electrode_info(subject, montage=0, bipolar=False):
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


## -- EEG LOADERS -- 

def load_raw_eeg(task, subject, session, elec_scheme):
    """
    Returns MNE... 
    """

    return CMLReader (subject = subject, experiment = task, session = session).load_eeg(scheme = elec_scheme).to_ptsa()


def load_events_eeg(events, rel_start_ms, rel_stop_ms, buf_ms=0, elec_scheme=None, noise_freq=[58., 62.],
             resample_freq=None, pass_band=None, use_mirror_buf=False, demean=False, do_average_ref=False):
    """
    Returns an EEG TimeSeries object.

    Parameters
    ----------
    events: pandas.DataFrame
        An events dataframe that contains eegoffset and eegfile fields
    rel_start_ms: int
        Initial time (in ms), relative to the onset of each event
    rel_stop_ms: int
        End time (in ms), relative to the onset of each event
    buf_ms:
        Amount of time (in ms) of buffer to add to both the begining and end of the time interval
    elec_scheme: pandas.DataFrame
        A dataframe of electrode information, returned by load_elec_info(). If the column 'contact' is in the dataframe,
        monopolar electrodes will be loads. If the columns 'contact_1' and 'contact_2' are in the df, bipolar will be
        loaded. You may pass in a subset of rows to only load data for electrodes in those rows.

        If you do not enter an elec_scheme, all monopolar channels will be loaded (but they will not be labeled with
        correct channel tags). Entering a scheme is recommended.
    noise_freq: list
        Stop filter will be applied to the given range. Default=(58. 62)
    resample_freq: float
        Sampling rate to resample to after loading eeg.
    pass_band: list
        If given, the eeg will be band pass filtered in the given range.
    use_mirror_buf: bool
        If True, the buffer will be data taken from within the rel_start_ms to rel_stop_ms interval,
        mirrored and prepended and appended to the timeseries. If False, data outside the rel_start_ms and rel_stop_ms
        interval will be read.
    demean: bool
        If True, will subject the mean voltage between rel_start_ms and rel_stop_ms from each channel
    do_average_ref: bool
        If True, will compute the average reference based on the mean voltage across channels

    Returns
    -------
    TimeSeries
        EEG timeseries object with dimensions channels x events x time (or bipolar_pairs x events x time)

        NOTE: The EEG data is returned with time buffer included. If you included a buffer and want to remove it,
              you may use the .remove_buffer() method. EXTRA NOTE: INPUT SECONDS FOR REMOVING BUFFER, NOT MS!!

    """

    # check if monopolar is possible for this subject
    if 'contact' in elec_scheme:
        eegfile = np.unique(events.eegfile)[0]
        if os.path.splitext(eegfile)[1] == '.h5':
            eegfile = f'/protocols/r1/subjects/{events.iloc[0].subject}/experiments/{events.iloc[0].experiment}/sessions/{events.iloc[0].session}/ephys/current_processed/noreref/{eegfile}'
            with h5py.File(eegfile, 'r') as f:
                if not np.array(f['monopolar_possible'])[0] == 1:
                    print('Monopolar referencing not possible for {}'.format(events.iloc[0].subject))
                    return

    # add buffer is using
    if (buf_ms is not None) and not use_mirror_buf:
        actual_start = rel_start_ms - buf_ms
        actual_stop = rel_stop_ms + buf_ms
    else:
        actual_start = rel_start_ms
        actual_stop = rel_stop_ms

    # load eeg
    eeg = CMLReader(subject=events.iloc[0].subject).load_eeg(events, rel_start=actual_start, rel_stop=actual_stop,
                                                             scheme=elec_scheme).to_ptsa()

    # now auto cast to float32 to help with memory issues with high sample rate data
    eeg.data = eeg.data.astype('float32')

    # baseline correct subracting the mean within the baseline time range
    if demean:
        eeg = eeg.baseline_corrected([rel_start_ms, rel_stop_ms])

    # compute average reference by subracting the mean across channels
    if do_average_ref:
        eeg = eeg - eeg.mean(dim='channel')

    # add mirror buffer if using. PTSA is expecting this to be in seconds.
    if use_mirror_buf:
        eeg = eeg.add_mirror_buffer(buf_ms / 1000.)

    # filter line noise
    if noise_freq is not None:
        #if isinstance(noise_freq[0], float):
        #    noise_freq = [noise_freq]

        b_filter = ButterworthFilter(freq_range = noise_freq, filt_type ='stop', order = 4)
        for this_chan in range(eeg.shape[1]):
            this_eeg = eeg[:, this_chan:this_chan+1]
            filtered_eeg = b_filter.filter(timeseries = this_eeg)
            eeg[:, this_chan:this_chan+1] = filtered_eeg
                

    # resample if desired. Note: can be a bit slow especially if have a lot of eeg data
    if resample_freq is not None:
        eeg_resamp = []
        for this_chan in range(eeg.shape[1]):
            r_filter = ResampleFilter(eeg[:, this_chan:this_chan + 1], resample_freq)
            eeg_resamp.append(r_filter.filter())
        coords = {x: eeg[x] for x in eeg.coords.keys()}
        coords['time'] = eeg_resamp[0]['time']
        coords['samplerate'] = resample_freq
        dims = eeg.dims
        eeg = TimeSeries.create(np.concatenate(eeg_resamp, axis=1), resample_freq, coords=coords,
                                dims=dims)

    # do band pass if desired.
    if pass_band is not None:
        eeg = band_pass_eeg(eeg, pass_band)

    # reorder dims to make events first
    eeg = make_events_first_dim(eeg)
    return eeg


def make_events_first_dim(ts, event_dim_str='event'):
    """
    Transposes a TimeSeries object to have the events dimension first. Returns transposed object.

    Parameters
    ----------
    ts: TimeSeries
        A PTSA TimeSeries object
    event_dim_str: str
        the name of the event dimension

    Returns
    -------
    TimeSeries
        A transposed version of the orginal timeseries
    """

    # if events is already the first dim, do nothing
    if ts.dims[0] == event_dim_str:
        return ts

    # make sure events is the first dim because I think it is better that way
    ev_dim = np.where(np.array(ts.dims) == event_dim_str)[0]
    new_dim_order = np.hstack([ev_dim, np.setdiff1d(range(ts.ndim), ev_dim)])
    ts = ts.transpose(*np.array(ts.dims)[new_dim_order])
    return ts


def clean_electrodes(elec_info, elec_column1='stein.region', elec_column2='ind.region',
                                 x_coord_column='ind.x', roi_dict=None):
        """

        Given that we often want to look at effecfs based on brain region, this will take a subject's electrode info
        and bin it into broad ROIs based on lobe and hemisphere. In the project's terminology, `elec_column1` should
        usually be the 'loc_tag' information.

        Parameters
        ----------
        elec_column1: str
            DataFrame column to use for localization info.
        elec_column2: str
            Additional secondary DataFrame column to use.
        x_coord_column: str
            Column specifying the x-coordinate of each electrode. Used to determine left vs right hemisphere.
            Positive values are right hemisphere.
        roi_dict: dict
            A mapping of elec_column1/elec_column2 values to broader ROIs. If not given, the default will be used:

            {'Hipp': ['Left CA1', 'Left CA2', 'Left CA3', 'Left DG', 'Left Sub', 'Right CA1', 'Right CA2',
                                 'Right CA3', 'Right DG', 'Right Sub'],
             'MTL': ['Left PRC', 'Right PRC', 'Right EC', 'Right PHC', 'Left EC', 'Left PHC'],
             'Frontal': ['parsopercularis', 'parsorbitalis', 'parstriangularis', 'caudalmiddlefrontal',
                                    'rostralmiddlefrontal', 'superiorfrontal'],
            'Temporal': ['superiortemporal', 'middletemporal', 'inferiortemporal'],
            'Parietal': ['inferiorparietal', 'supramarginal', 'superiorparietal', 'precuneus'],
            'Occipital' ['lateraloccipital', 'lingual', 'cuneus', 'pericalcarine']}


        Returns
        -------
        A pandas.DataFrame with columns 'region' and 'hemi'.

        """

        # Region Labels
        rls = [
            'stein.region',
            'ind.region',
            'avg.region',
            'mni.region',
            'tal.region',
            'vox.region',
            'wb.region',
            'das.region'
        ]
        
        # smoosh the columns together, with the first column taking precedence
        regions = elec_info[rls[0]].fillna(
            elec_info[rls[1]]).fillna(
            elec_info[rls[2]]).fillna(
            elec_info[rls[3]]).fillna(
            elec_info[rls[4]]).fillna(
            elec_info[rls[5]]).fillna(
            elec_info[rls[6]]).fillna(
            elec_info[rls[7]]).fillna(
            value='')

        # if no dictionary is providing, use this
        if roi_dict is None:
            roi_dict = {'Hipp': ['Left CA1', 'Left CA2', 'Left CA3', 'Right CA1', 'Right CA2',
                                 'Right CA3'],
                        'DG': ['Left DG', 'Right DG'],
                        'Sub': ['Left Sub', 'Right Sub'],
                        'EC': ['Right EC', 'Left EC'],
                        'HippFormation': ['Left CA1', 'Left CA2', 'Left CA3', 'Right CA1', 'Right CA2',
                                          'Right CA3', 'Left DG', 'Right DG', 'Left Sub', 'Right Sub'],
                        'MTL': ['Left PRC', 'Right PRC', 'Right EC', 'Right PHC', 'Left EC', 'Left PHC'],
                        'IFG': ['parsopercularis', 'parsorbitalis', 'parstriangularis'],  # This may contain Broca's Area
                        'MFG': ['caudalmiddlefrontal', 'rostralmiddlefrontal'],  # This may contrain DLPFC
                        'SFG': ['superiorfrontal'],
                        'Frontal': ['parsopercularis', 'parsorbitalis', 'parstriangularis', 'caudalmiddlefrontal',
                                    'rostralmiddlefrontal', 'superiorfrontal'],
                        'Temporal': ['superiortemporal', 'middletemporal', 'inferiortemporal'],
                        'Parietal': ['inferiorparietal', 'supramarginal', 'superiorparietal', 'precuneus'],
                        'Occipital': ['lateraloccipital', 'lingual', 'cuneus', 'pericalcarine']}

        # get ROI for each electrode. THIS GETS THE FIRST, IF IT IS IN MULTIPLE SOMEHOW
        elec_region_list = [''] * len(regions)
        for e, elec_region in enumerate(regions):
            for roi in roi_dict.keys():
                if elec_region in roi_dict[roi]:
                    elec_region_list[e] = roi
                    continue

        # get hemisphere
        elec_hemi_list = np.array(['right'] * len(regions))
        elec_hemi_list[elec_info[x_coord_column] < 0] = 'left'

        # make new DF
        region_df = elec_info[['label']].copy()
        region_df['region'] = elec_region_list
        region_df['hemi'] = elec_hemi_list

        return region_df


def bin_electrodes_by_region(elec_info, elec_column1='stein.region', elec_column2='ind.region',
                                 x_coord_column='ind.x', roi_dict=None):
        """

        Given that we often want to look at effecfs based on brain region, this will take a subject's electrode info
        and bin it into broad ROIs based on lobe and hemisphere. In the project's terminology, `elec_column1` should
        usually be the 'loc_tag' information.

        Parameters
        ----------
        elec_column1: str
            DataFrame column to use for localization info.
        elec_column2: str
            Additional secondary DataFrame column to use.
        x_coord_column: str
            Column specifying the x-coordinate of each electrode. Used to determine left vs right hemisphere.
            Positive values are right hemisphere.
        roi_dict: dict
            A mapping of elec_column1/elec_column2 values to broader ROIs. If not given, the default will be used:

            {'Hipp': ['Left CA1', 'Left CA2', 'Left CA3', 'Left DG', 'Left Sub', 'Right CA1', 'Right CA2',
                                 'Right CA3', 'Right DG', 'Right Sub'],
             'MTL': ['Left PRC', 'Right PRC', 'Right EC', 'Right PHC', 'Left EC', 'Left PHC'],
             'Frontal': ['parsopercularis', 'parsorbitalis', 'parstriangularis', 'caudalmiddlefrontal',
                                    'rostralmiddlefrontal', 'superiorfrontal'],
            'Temporal': ['superiortemporal', 'middletemporal', 'inferiortemporal'],
            'Parietal': ['inferiorparietal', 'supramarginal', 'superiorparietal', 'precuneus'],
            'Occipital' ['lateraloccipital', 'lingual', 'cuneus', 'pericalcarine']}


        Returns
        -------
        A pandas.DataFrame with columns 'region' and 'hemi'.

        """

        # smoosh the columns together, with the first column taking precedence
        regions = elec_info[elec_column1].fillna(elec_info[elec_column2]).fillna(value='')

        # if no dictionary is providing, use this
        if roi_dict is None:
            roi_dict = {'Hipp': ['Left CA1', 'Left CA2', 'Left CA3', 'Left DG', 'Left Sub', 'Right CA1', 'Right CA2',
                                 'Right CA3', 'Right DG', 'Right Sub'],
                        'MTL': ['Left PRC', 'Right PRC', 'Right EC', 'Right PHC', 'Left EC', 'Left PHC'],
                        'Frontal': ['parsopercularis', 'parsorbitalis', 'parstriangularis', 'caudalmiddlefrontal',
                                    'rostralmiddlefrontal', 'superiorfrontal'],
                        'Temporal': ['superiortemporal', 'middletemporal', 'inferiortemporal'],
                        'Parietal': ['inferiorparietal', 'supramarginal', 'superiorparietal', 'precuneus'],
                        'Occipital': ['lateraloccipital', 'lingual', 'cuneus', 'pericalcarine']}

        # get ROI for each electrode. THIS GETS THE FIRST, IF IT IS IN MULTIPLE SOMEHOW
        elec_region_list = [''] * len(regions)
        for e, elec_region in enumerate(regions):
            for roi in roi_dict.keys():
                if elec_region in roi_dict[roi]:
                    elec_region_list[e] = roi
                    continue

        # get hemisphere
        elec_hemi_list = np.array(['right'] * len(regions))
        elec_hemi_list[elec_info[x_coord_column] < 0] = 'left'

        # make new DF
        region_df = elec_info[['label']].copy()
        region_df['region'] = elec_region_list
        region_df['hemi'] = elec_hemi_list

        return region_df