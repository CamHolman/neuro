"""
comp3 version
"""

# External
from dataclasses import dataclass, field
from abc import abstractmethod
import pynwb 

# Local
from neuro.io.load_nwb import *
from neuro.comp3.data import * 
from neuro.neuron.Neuron import Neuron


class DataIO:
    """ 
    Bass class for DataIO
    """

    def __init__(self, file = ''):
        self.file = file

    @abstractmethod 
    def load(self):
        pass

    @abstractmethod
    def save(self):
        pass
    
    @abstractmethod
    def load_external(self):
        pass

    @abstractmethod
    def compute(self):
        pass 


class NWBIO(DataIO):
    """
    NWB Data handler
    """
    def __init__(self, nwb = None):
        
        # -- Atributes --
        self.nwb = nwb
        self.nwbfilepath = None

        # Metadata
        self.subject_id = None
        self.session_id = None        
        
        # -- Post -- 
        # Given: NWB File Path
        if type(self.nwb) != pynwb.file.NWBFile:
            self.nwbfilepath = self.nwb
            self.nwb = None

        # Load Data
        if self.nwbfilepath and not self.nwb:
            self.load()
        else:
            self._nwb_get_metadata()

    def load(self):
        """
        Loads nwb file with fuzzy matching. If file is already loaded
        ask the user if they want to relaod. 
        """
        # Check if nwbfile already loaded and ask to reload
        if self.nwb:
            while True:
                UI = input (f'NWB file is already loaded. \
                \n\n This is the current session_id: \t{self.nwb.session_id} \
                \n This is the new filepath: \t\t{self.nwbfilepath} \
                \n\n Would you like to reload? (y/n)')
                if UI == 'y' or UI == 'n':
                    break
                else:
                    print ('Invalid Input: respond y or n')
            if UI == 'n':
                print ('NWB file not loaded')
            elif UI == 'y':
                self.nwb = load_nwb(self.nwbfilepath)
                self._nwb_get_metadata()
                print ('NWB file sucessfully reloaded')
        # Else just load 
        else:
            self.nwb = load_nwb(self.nwbfilepath)
            self._nwb_get_metadata()
            
    def _nwb_get_metadata(self):
        # Populate metadata from NWB file
        print ('getting metadata')
        self.subject_id = self.nwb.subject.subject_id
        self.session_id = self.nwb.session_id

    def extract_data(self, task_id = 'TreasureHunt'):
        if self.task_id == 'TreasureHunt':
            self.data = self._extract_data_treasure_hunt(self.nwb)
        elif self.task_id == 'CityBlock':
            pass
        else:
            raise ValueError(self.task_id)
    
    def extract_signal(self, signal_id = 'SingleUnit'):
        if self.signal_id == 'SingleUnit':
            self.signal = 
            
def nwb_extract_data_treasure_hunt(nwb = None):
   
    # Components
    subject = Subject(id = nwb.subject.subject_id) 
    session = TreasureHuntSession(
        id = nwb.session_id,
        session_start_time = 0.0,
        session_stop_time = nwb.trials['stop_time'][-1],
        navigation_start_times = nwb.trials['navigation_start'][:],
        navigation_stop_times = nwb.trials['navigation_stop'][:]
    )
    navigation = Navigation(
        xy    = nwb.acquisition['position']['player_position'].data[:],
        times = nwb.acquisition['position']['player_position'].timestamps[:]
    )
    headdireciton = HeadDirection(
        degrees = nwb.acquisition['heading']['direction'].data[:],
        times   = nwb.acquisition['heading']['direction'].timestamps[:]
    )
    stimuli = Stimuli()
    memory = Memory()

    # Combine
    data = TreasureHuntData()
    data.subject = subject
    data.session = session
    data.navigation = navigation
    data.headdirection = headdireciton
    data.stimuli = stimuli
    data.memory = memory

    return data 



    def _extract_signal_single_unit(self, nwb = None, unit_ix = 0):

        subject_id = nwb
        
        neuron = Neuron(
            
        )
    


