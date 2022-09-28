


"""
Space for building 1

useful: https://python.astrotech.io/intermediate/dataclass/metadata.html
    see 4.9.4 for type enforcement


    https://kplauritzen.dk/2021/08/11/convert-dataclasss-np-array.html
    returning array tuple

    https://stackoverflow.com/questions/67100439/what-is-field-metadata-used-for-in-python-dataclasses
    external metadata for fields

"""
import dataclasses
from dataclasses import dataclass, field
from importlib.resources import path
from typing import Any, List


# -TASK-
@dataclass(kw_only=True)
class Task:
    name: str
    version: int
    

#class TaskTreasureHunt(Task):
#    def __init__(self, **kwargs):
#        super().__init__(**kwargs)
#    pass

#TH = TaskTreasureHunt #alias

@dataclass(kw_only=True)
class Session(Task):
    session_start_time : float = 0.0
    session_end_time : float = 0.0


@dataclass(kwonly=True)
class TreasureHunt(Task, Session):
    """
    Class to represent each session of treasure hunt...
    """
    navigation_start_times : list = field(default_factory=list, metadata={'info': 'Start times of navigation epochs', 'units' : 'seconds'})
    navigation_stop_times : list = field(default_factory=list, metadata={'info': 'Stop times of navigation epochs', 'units' : 'seconds' })


    

class TaskCityBlock(Task):
    pass


# -SUBJECT- 
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
    Class for Subject
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

class Electrode(ElectrodeData):
    """
    Class for Electrode
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@dataclass(kw_only=True)
class ElectrodeBenkheFriedData(Electrode):
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
@dataclass(kw_only=True)
class ElectrodeContactData:
    """
    BaseDataclass for electrode contacts
    """
    # ID
    id           : str       = dataclasses.field(default_factory=str)
    contact_type : str       = dataclasses.field(default_factory=str)
    electrode    : Electrode = None                                      # On Electrode 
    subject      : Subject   = None                                      # In Subject

    # Data 
    surface_area : float     = dataclasses.field(default_factory=float)

    # Enforce attribute type on init
    def __post_init__(self):
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                raise ValueError(f'Expected {field.name} to be {field.type}, '
                                f'got {repr(value)}')


class ElectrodeContact(ElectrodeContactData):
    """
    Class for Electrode Contact
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


# --Microcontact--
@dataclass(kw_only=True)
class MicroContactData(ElectrodeContactData):
    """
    subDataClass for micro contacts
    """
    pass 


# -RECORDING-
@dataclass(kw_only=True)
class NeuralRecordingData:
    """
    Dataclass for each recording
    """
    id        : str              = dataclasses.field(default_factory=str)
    ix        : int              = dataclasses.field(default_factory=int)
    contact   : ElectrodeContact = None
    electrode : Electrode        = None
    subject   : Subject          = None
    
    # Data Location
    recording_file_path : str    = dataclasses.field(default_factory=str)

    # Raw Data
    raw_data : Any = None
    
    # Meta Data
    tstart : float = dataclasses.field(default_factory=float, metadata={'unit': 'sec'})
    length : float = dataclasses.field(default_factory=float, metadata={'unit': 'sec'})



class NeuralRecording(NeuralRecordingData):
    """
    Class for Neural Recordings
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    @property
    def recording_length(self):
        return len(self.raw_data)


# -NEURON-
@dataclass(kw_only=True)
class NeuronData:
    """
    BaseDataclass for single unit neuron level information

    Atributes
    ---------
    id : str 
        unique identifier
    ix : int
        numbered identifier
    subject: object
        Subject class instance
    recording : object
        NeuralRecording class instance 
    electrode : object
        Electrode class instance 
    contact:
        ElectrodeContact class instance
    
    spikes: 1D arr
        spike times in sec
    """

    id        : str              = dataclasses.field(default_factory=str)
    ix        : int              = dataclasses.field(default_factory=int)
    subject   : Subject          = None
    recording : NeuralRecording  = None
    electrode : Electrode        = None
    contact   : ElectrodeContact = None

    # Data
    spiketrain : list = dataclasses.field(default_factory=list)



class Neuron(NeuronData):
    """
    Class for Neuron
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def spike_count(self):
        return len(self.spike_train)

    @property
    def firing_rate(self):
        return self.spike_count / self.recording.recording_length 


# ## maybe too much 
# @dataclass
# class SpikeTrainData:
#     """
#     BaseDC for spike trains
#     """
#     id        : str              = dataclasses.field(default_factory=str)
#     ix        : int              = dataclasses.field(default_factory=int)
#     recording : NeuralRecording  = None
#     contact   : ElectrodeContact = None
#     electrode : Electrode        = None
#     subject   : Subject          = None
    
#     #Data
    


# -- Neuron Types --
@dataclass(kw_only=True)
class _HeadDirectionNeuron:
    # HD Data
    hd_occupancy : list = field(default_factory=list, metadata={'info': 'Seconds spent in each bin', 'unit':'seconds'})
    hd_times     : list = field(default_factory=list, metadata={'info': 'Times at which head direction was recorded', 'unit':'seconds'})
    hd_degrees   : list = field(default_factory=list, metadata={'info': 'Recorded head directions, matched to hd_times', 'unit':'degrees'})
    
    # Session & Epoch data - define epochs relevant to HD
    session_start_time : float = 0.0
    session_stop_time : float = 0.0 
    epoch_start_times : list = field(default_factory=list, metadata={'info': 'Start times of epochs of interest', 'unit':'seconds'})
    epoch_stop_times : list = field(default_factory=list, metadata={'info': 'Stop times of epochs of interest', 'unit':'seconds'})


    def __post_init__(self):
        if self.hd_occupancy == []:
            self.compute_occupancy()

    def compute_occupancy(self):
        pass


class HeadDirectionNeuron(_HeadDirectionNeuron, Neuron, Session):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
 



        # https://stackoverflow.com/questions/3277367/how-does-pythons-super-work-with-multiple-inheritance
    


def create_HDA(nwbfile):
    


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