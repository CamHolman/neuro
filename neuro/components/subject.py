import dataclasses
from dataclasses import dataclass, field

from neuro.components import *

# -SUBJECT- 
@dataclass(kw_only=True)
class Subject:
    """
    BaseDataclass for subject level information 
    """
    # ID    
    id    : str = dataclasses.field(default_factory=str)  #unique id
    ix    : int = dataclasses.field(default_factory=int)  #numbered id 
    name  : str = dataclasses.field(default_factory=str)
    age   : int = dataclasses.field(default_factory=int)
    sex   : str = dataclasses.field(default_factory=str)
    notes : str = dataclasses.field(default_factory=str)
    recording_location : str  = dataclasses.field(default_factory=str)


    # Data 
    data_folder : str = dataclasses.field(default_factory=str)
    

    # Relations
    electrodes : list = dataclasses.field(default_factory=list)  #list of electrode objects
    #behavior           : Behavior = None 
    

    # Enforce attribute type on init
    def __post_init__(self):
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                raise ValueError(f'Expected {field.name} to be {field.type}, '
                                f'got {repr(value)}')
    



# class Subject(_Subject):
#     """
#     Class for Subject
#     """
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)


