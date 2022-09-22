import dataclasses
from dataclasses import dataclass, field 
from pynwb.file import NWBFile


#from neuro.components.io import NWBIO
from neuro.components.subject import Subject
from neuro.components.session import TreasureHuntSession


@dataclass(kw_only=True)
class Navigation:
    # Positions
    xy    : list = field(default_factory=list, metadata={'info': 'Player x,y position'})
    times : list = field(default_factory=list, metadata={'info': 'times when position is recorded', 'units': 'sec'})


@dataclass(kw_only=True)
class HeadDirection:
    degrees   : list = field(default_factory=list, metadata={'info': 'Player head direction', 'units': 'degrees'})
    times     : list = field(default_factory=list, metadata={'info': 'times when HD is recorded', 'units': 'sec'})
    occupancy : list = field(default = None, metadata={'info': 'time spent in each bin', 'units': 'sec'})


@dataclass(kw_only=True)
class Stimuli:
    stimuli                    : list  = field(default_factory=list, metadata={'info': 'presented stimuli'})
    stimuli_presentation_times : list  = field(default_factory=list, metadata={'info': 'times when stimuli are presented', 'units': 'sec'})
    recall_presentation_times  : list  = field(default_factory=list, metadata={'info': 'times when stimuli are presented', 'units': 'sec'})

@dataclass(kw_only=True)
class Memory:
    recalled_stimuli           : list = field(default_factory=list, metadata={'info': 'boolean list recalled or not; index corresponds with stimuli', 'units': 'bool'})
    recall_times               : list = field(default_factory=list, metadata={'info': 'time of recall response', 'units': 'sec'})
                                                                                        


@dataclass(kw_only=True)
class Behavior:
    navigation     : Navigation    = None
    head_direction : HeadDirection = None
    memory         : Memory        = None
    stimuli        : Stimuli       = None
    

@dataclass(kw_only=True)
class TreasureHuntData:
    # Relations
    io = None

    # NWB file (required)
    nwb = None

    def populate(self):
        if self.io:
            nwb = self.io.nwb
        elif nwb:
            nwb = self.nwb
        else:
            print ('give io or nwb file')
            return 
        
        # Subject
        self.subject = Subject(id = nwb.subject.subject_id)
        
        # Session 
        self.session = TreasureHuntSession(
            id = nwb.session_id,
            session_start_time = 0.0,
            session_stop_time = nwb.trials['stop_time'][-1],
            navigation_start_times = nwb.trials['navigation_start'][:],
            navigation_stop_times = nwb.trials['navigation_stop'][:]
        )

        # Navigation 
        self.navigation = Navigation(
            xy    = nwb.acquisition['position']['player_position'].data[:],
            times = nwb.acquisition['position']['player_position'].timestamps[:]
        )
        
        # Head Direction
        self.headdireciton = HeadDirection(
            degrees = nwb.acquisition['heading']['direction'].data[:],
            times   = nwb.acquisition['heading']['direction'].timestamps[:]
        )

        # Stimuli
        self.stimuli = Stimuli()
        # Memory
        self.memory = Memory()

# @dataclass(kw_only=True)
# class TreasureHuntData:
#     # Relations
#     io = None
    

#     # NWB file (required)
#     nwb : NWBFile = None

    
#     # Subject
#     subject = Subject(id = nwb.subject_id)
    
#     # Session 
#     session = TreasureHuntSession(
#         id = nwb.session_id,
#         session_start_time = 0.0,
#         session_stop_time = nwb.trials['stop_time'][-1],
#         navigation_start_times = nwb.trials['navigation_start'][:],
#         navigation_stop_times = nwb.trials['navigation_stop'][:]
#     )

#     # Navigation 
#     navigation = Navigation(
#         xy    = nwb.acquisition['position']['player_position'].data[:],
#         times = nwb.acquisition['position']['player_position'].timestamps[:]
#     )
    
#     # Head Direction
#     headdireciton = HeadDirection(
#         degrees = nwb.acquisition['heading']['direction'].data[:],
#         times   = nwb.acquisition['heading']['direction'].timestamps[:]
#     )

#     # Stimuli
#     stimuli = Stimuli()
#     # Memory
#     memory = Memory()

class TaskDataHandler:
    def __init__(self, task_id):
        self.task_id = task_id
        self._tasks = {
            'TreasureHunt' : TreasureHuntData,
            'CityBlock'    : None
        }
    
    def choose_task(self):
        task = self._tasks.get(self.task_id)
        if not task:
            return ValueError(self.task_id)
        return task

    