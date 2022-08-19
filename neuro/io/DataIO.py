"""
Base class for data IO

This is configured for input from NWB files, can be modified as needed
"""

from neuro.settings import io as SIO
from neuro.io.load_nwb import *


class NWBIO(object):
    def __init__(self, filepath = None, nwbfile = None):
        def __init__ (self, filepath = None, nwbfile = None):
        
        # Given
        self.filepath = filepath
        self.nwbfile = nwbfile
        
        # Extracted
        self.subject    = 'run self.nwb_get_data() to populate'

    def nwb_load(self):
        
        # Check if nwbfile already loaded and ask to reload
        if self.nwbfile != None:
            while True:
                UI = input (f'NWB file is already loaded. \
                \n\n This is the current session_id: \t{self.nwbfile.session_id} \
                \n This is the new filepath: \t\t{self.filepath} \
                \n\n Would you like to reload? (y/n)')
                if UI == 'y' or UI == 'n':
                    break
                else:
                    print ('Invalid Input: respond y or n')
            if UI == 'n':
                print ('NWB file not loaded')
            elif UI == 'y':
                self.nwbfile = load_nwb(self.filepath)
                self._nwb_get_data()
                print ('NWB file sucessfully reloaded')
        
        # Else just load 
        else:
            self.nwbfile = load_nwb(self.filepath)
            self._nwb_get_data()

    def _nwb_get_data(self):
        # Populate metadata from NWB file
        self.subject = self.nwbfile.subject.subject_id
        self.session = self.nwbfile.session_id
        self.n_trials = len(self.nwbfile.trials)
        self.n_units = len(self.nwbfile.units)


class DataIO(NWBIO):
    def __init__ (self, filepath = None, datatype = 'nwb'):
        
        # Given
        self.filepath = filepath
        self.datatype = datatype

        # Extracted
        self.subject    = 'run self.nwb_get_data() to populate'

    def data_load(self):
        if self.datatype = 'nwb':
            print ('Data type set to "nwb" \nLoading NWB File...')
            self.nwb_load(self.filepath)
            self._nwb_get_data()


class Session(DataIO):
    def __init__(self, filepath = None, nwbfile = None):
        
        # Given
        self.filepath = filepath
        self.nwbfile = nwbfile
        
        # Extracted
        self.subject    = 'run self.nwb_get_data() to populate'
        self.session    = 'run self.nwb_get_data() to populate'
        self.n_trials   = 'run self.nwb_get_data() to populate'
        self.n_units    = 'run self.nwb_get_data() to populate'

    def nwb_get_data_sess(self):
        # Populate metadata from NWB file
        print('Session version')
        self.subject = self.nwbfile.subject.subject_id
        self.session = self.nwbfile.session_id
        self.n_trials = len(self.nwbfile.trials)
        self.n_units = len(self.nwbfile.units)

class TreasureHuntSession(Session):
    def __init__:



class Subject(DataIO):
    def __init__ (self):
        self.newsubject = 'new'
    
            

