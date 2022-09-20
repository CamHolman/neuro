
# External
from dataclasses import dataclass, field
from abc import abstractmethod
import pynwb 

# Local
from neuro.io.load_nwb import *

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


# -- NWB -- 

# import pynwb

# @dataclass(kw_only = True)
# class _NWBIO:
    
#     nwb : pynwb.file.NWBFile = None
#     filepath : str = ''
    


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

    def save(self):
        return super().save()

    def load_external(self):
        return super().load_external()

    def compute(self):
        return super().compute()

