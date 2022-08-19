# Imports
import os
import glob
from pynwb import NWBHDF5IO
from thefuzz import process      # Levenshtein distancce fuzzy string matching

# Settings
from neuro.settings import io as SIO 


def load_nwb(filepath, verbose = True):
    """ 
    Load NWB file from filepath

    WIP - may implement py-lev natively

    PARAMETERS
    ----------
    filepath : str
        Path to NWB file
        
        Note: if the file is in the default data directory (specified in 
        neuro.settings.settings_io.py), then you can input a string that 
        is similar to your file to search. 
    
    RETURNS
    -------
    nwb_file: .nwb
        NWB file containing data for the given TASK + SUBJ + SESSION
    """

    # Try to load file
    try:
        io = NWBHDF5IO(str(filepath), 'r')
        nwbfile = io.read()

    # Else find closest match
    except:
        file_dir = os.path.dirname(filepath)
        file_name = os.path.basename(filepath)
        file_ext = os.path.split(file_name)[1] 

        # Load dir from settings if not given
        if file_dir == '':
            file_dir = SIO.DIR_DATA
            if verbose:
                print('Data folder not given \t | Data folder from neuro.settings.io: \t {} \n'.format(file_dir))
        
        # Add .nwb if not given
        if file_ext == '':
            file_name = file_name + '.nwb' 

        # Find files
        files = glob.glob(file_dir +'*.nwb')
        closest_file = process.extractOne(file_name, files)

        # If match score 100 then return
        if closest_file[1] == 100:
            file_path = closest_file[0]
            io = NWBHDF5IO(file_path, 'r')
            nwbfile = io.read()
            
        # Else use levenshtein distance
        else:
            if verbose:
                print ('Could not find exact match. Looking for closest match... \n')
                print('These are the NWB files in your data folder:')
                files.sort()
                print(*files, '\n', sep='\n')
                print('This file was found to have the closest match:')
                print (closest_file[0])
                print('Match Score = {} \n'.format(closest_file[1]))

                print ('These are all the match scores')
                allf = process.extract(file_name, files)
                print(len(allf))
                print (*allf, '\n', sep='\n')

            # Ask user if they want to load file
            while True:
                UI = input ('Would you like to load this file (y/n):')
                if UI.isalpha():
                    break
                else: #invalid
                    print('Invalid Input. Respond y or n.')
            if UI == 'y':
                print ('Great, loading the file...')
                file_path = closest_file[0]
                io = NWBHDF5IO(file_path, 'r')
                nwbfile = io.read()
            elif UI == 'n':
                print ('Oh no! Please try again')
                return
            print('Loaded File: \t\t {}'.format(file_path))

    return nwbfile