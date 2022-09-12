

from dataclasses import dataclass, field

from abc import abstractmethod
#from re import X


class DataIO:
    """ 
    Bass class for DataIO
    """

    def __init__(self, file = ''):
        self.file = file

    @abstractmethod # TODO: or @abstractclassmethod?
    def load(self):
        pass

    def save(self):
        pass
    
    def load_external(self):
        pass

    def compute(self):
        pass 


# -- NWB -- 

import pynwb

@dataclass(kw_only = True)
class _NWBIO:
    
    nwb : pynwb.file.NWBFile = None
    filepath : str = ''
    


class NWBIO(_NWBIO, DataIO):
    """
    NWB Data handler
    """
    def __init__(self, **kwargs):
        mro = self.__class__.__mro__
        print (mro)

        for ix, superclass in enumerate(mro[1:]):
            print (superclass)
            
    

