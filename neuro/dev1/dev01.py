


"""
Space for building 1

"""
import dataclasses
from dataclasses import dataclass, field
from typing import Any, List


# -SUBJECT- 
@dataclass
class Task:
    name: str
    version: int
    

class TaskTreasureHunt(Task):
    pass
TH = TaskTreasureHunt #alias

class TaskCityBlock(Task):
    pass


@dataclass(kw_only=True)
class SubjectData:
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

    # Data 
    data_folder        : str  = dataclasses.field(default_factory=str)
    recording_location : str  = dataclasses.field(default_factory=str)
    electrodes         : list = dataclasses.field(default_factory=list) #list of electrode objects

    # Enforce attribute type on init
    def __post_init__(self):
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                raise ValueError(f'Expected {field.name} to be {field.type}, '
                                f'got {repr(value)}')



class Subject(SubjectData):
    """
    Base Class for Subject
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    

# -ELECTRODE-
@dataclass(kw_only=True)
class ElectrodeData:
    """
    BaseDataClass for electrode level information
    """
    # ID 
    id             : str  = dataclasses.field(default_factory=str)
    ix             : int  = dataclasses.field(default_factory=int)
    electrode_type : str  = dataclasses.field(default_factory=str)
    literature     : list = dataclasses.field(default_factory=list)  # source literature DOIs

    # Enforce attribute type on init
    def __post_init__(self):
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                raise ValueError(f'Expected {field.name} to be {field.type}, '
                                f'got {repr(value)}')



@dataclass(kw_only=True)
class ElectrodeBenkheFriedData(ElectrodeData):
    """
    subDataClass for Benkhe-Fried
    """
    # Macro
    macro_contacts_num : int  = 8
    macro_contacts     : list = dataclasses.field(default_factory=list)
    macro_reference    : str  = dataclasses.field(default_factory=str)
    
    # Micro 
    micro_contacts_num : int  = 8
    micro_contacts     : list = dataclasses.field(default_factory=list)
    micro_reference    : str  = dataclasses.field(default_factory= str)

    # Enforce attribute type on init
    def __post_init__(self):
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                raise ValueError(f'Expected {field.name} to be {field.type}, '
                                f'got {repr(value)}')


class ElectrodeBenkheFried(ElectrodeBenkheFriedData):
    """
    Electrode Class for Benkhe-Fried
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

EBF =  ElectrodeBenkheFried  #alias



# -CONTACT- 
@dataclass
class ElectrodeContactData:
    """
    BaseDataclass for electrode contacts
    """
    # ID
    id           : str    = dataclasses.field(default_factory=str)
    electrode    : object = dataclasses.field(default_factory=
    contact_type : str    = dataclasses.field(default_factory=str)

    # Data
    surface_area : float = 0.0


@dataclass
class MicroContactData(ElectrodeContactData):
    """
    subDataClass for micro contacts
    """
    


# -NEURON-
@dataclass 
class UnitData:
    """
    Dataclass for single unit neuron level information
    """
    

class Neuron:
    """
    Class for Neuron
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.neuron_

class NeuronHeadDirection(Neuron):
    pass



########################

## DATA CLASS KWARGS..
# https://stackoverflow.com/questions/55099243/python3-dataclass-with-kwargsasterisk

# from dataclasses import dataclass
# from inspect import signature


# @dataclass
# class Container:
#     user_id: int
#     body: str

#     @classmethod
#     def from_kwargs(cls, **kwargs):
#         # fetch the constructor's signature
#         cls_fields = {field for field in signature(cls).parameters}

#         # split the kwargs into native ones and new ones
#         native_args, new_args = {}, {}
#         for name, val in kwargs.items():
#             if name in cls_fields:
#                 native_args[name] = val
#             else:
#                 new_args[name] = val

#         # use the native ones to create the class ...
#         ret = cls(**native_args)

#         # ... and add the new ones by hand
#         for new_name, new_val in new_args.items():
#             setattr(ret, new_name, new_val)
#         return ret