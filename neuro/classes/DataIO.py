"""
Base class for data IO

This is configured for input from NWB files, can be modified as needed
"""

from neuro.settings import settings_io as SIO
from neuro.io import load_nwb as LNWB

class DataIO(object):
    def __init__ (self, filepath = None, nwbfile = None):
        self.filepath = filepath
        self.nwbfile = nwbfile

    def load_nwb(self):
        if self.nwbfile != None:
            
            # Check if file given and ask to reload
            while True:
                UI = input ('NWB file is already loaded. Would you like to reload? (y/n)')
                if UI == 'y' or UI == 'n':
                    break
                else:
                    print ('Invalid Input: respond y or n')

            # Reload or Don't
            if UI == 'n':
                print ('NWB file not loaded')
            elif UI == 'y':
                self.nwbfile = LNWB(self.filepath)
                print ('NWB file sucessfully reloaded')
        
            

