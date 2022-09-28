"""
Base class for data IO

This is configured for input from NWB files, can be modified as needed
"""

from neuro.settings import io as SIO
from neuro.io.load_nwb import *


class NWBIO(object):
    """
    A dendrite 
    """
    def __init__(self, filepath = None, nwbfile = None):

        # Given
        self.nwbpath = filepath
        self.nwbfile = nwbfile

        # Extracted
        msg = 'run self.nwb_get_metadata() to populate'
        self.subject    = msg

    def nwb_load(self):
        """
        Loads nwb file with fuzzy matching. If file is already loaded
        ask the user if they want to relaod. 
        """
        # Check if nwbfile already loaded and ask to reload
        if self.nwbfile != None:
            while True:
                UI = input (f'NWB file is already loaded. \
                \n\n This is the current session_id: \t{self.nwbfile.session_id} \
                \n This is the new filepath: \t\t{self.nwbpath} \
                \n\n Would you like to reload? (y/n)')
                if UI == 'y' or UI == 'n':
                    break
                else:
                    print ('Invalid Input: respond y or n')
            if UI == 'n':
                print ('NWB file not loaded')
            elif UI == 'y':
                self.nwbfile = load_nwb(self.nwbpath)
                self._nwb_get_metadata()
                print ('NWB file sucessfully reloaded')
        # Else just load 
        else:
            self.nwbfile = load_nwb(self.nwbpath)
            self._nwb_get_metadata()

    def _nwb_get_metadata(self):
        # Populate metadata from NWB file
        self.subject = self.nwbfile.subject.subject_id



class DataIO(NWBIO):
    """
    The Soma. Take data from any source. 

    Build class for each data source ... pass here .. pass on 
    """
    def __init__ (self, filepath = None):

        # Args
        self.filepath = filepath
        
        # Other
        self.datatype = os.path.split(os.path.basename(self.filepath))[-1] 
        self.subject    = 'run self.nwb_get_data() to populate'

    def data_load(self):
        if self.datatype = 'nwb':
            print ('Data type set to "nwb" \nLoading NWB File...')
            self.nwb_load(self.filepath)
            self._nwb_get_metadata()
        else:
            print (f'Unknown datatype: {self.datatype}')

    def add_beahvioral_data(self, behavior_filepath = None, task = 'THO'):
        pass 



class Session(DataIO):
    """
    Axon hillock 
    """
    def __init__(self, filepath = None, nwbfile = None):
        
        # Given
        self.filepath = filepath
        self.nwbfile = nwbfile
        
        # Extracted
        msg = 'run self.nwb_get_data() to populate'
        self.subject    = msg
        self.session    = msg
        self.n_trials   = msg
        self.n_units    = msg

    def _nwb_get_metadata(self):
        # Populate metadata from NWB file
        print('Session version')
        self.subject    = self.nwbfile.subject.subject_id
        self.session    = self.nwbfile.session_id
        self.n_trials   = len(self.nwbfile.trials)
        self.n_units    = len(self.nwbfile.units)

    def _nwb_file_get_session_data()


class Task(object)
    def __init__(self):
        self.task_name = 

class TreasureHuntTask(Task):
    """
    Astrocyte 
    """
    def __init__(self, version = ''):
        self.version = version
    
    def _get_navigation_start_and_end_times(self):

        



class TreasureHuntSession(Session, TreasureHuntTask):
    """
    A synapse
    """
    def __init__(self):
        self.


class Neuron()



class Subject(DataIO):
    """
    Pyramidal neuron
    """
    def __init__ (self, subject = '', sessions = []):
        self.subject = subject
        self.sessions = sessions
    
    

    
            

