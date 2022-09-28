"""
comp3 data 

"""


from dataclasses import dataclass, field 




@dataclass(kw_only=True)
class Subject:
    id    : str = field(default_factory=str)  #unique id
    ix    : int = field(default_factory=int)  #numbered id 
    name  : str = field(default_factory=str)
    age   : int = field(default_factory=int)
    sex   : str = field(default_factory=str)
    notes : str = field(default_factory=str)
    recording_location : str  = field(default_factory=str)

@dataclass(kw_only=True)
class Session:
    id : str = ''

    # Data
    session_start_time : float = 0.0
    session_stop_time  : float = 0.0
    epoch_start_times  : list  = field(default_factory=list)
    epoch_stop_times   : list  = field(default_factory=list)

    @property
    def session_length(self):
        return self.session_stop_time - self.session_start_time
    @property
    def epoch_lengths(self):
        return self.epoch_stop_times - self.epoch_start_times
    @property
    def epoch_length(self):
        return sum(self.epoch_lengths)

        
@dataclass(kw_only=True)
class TreasureHuntSession(Session):
    """
    Class to represent each session of treasure hunt...
    """
    # Task info 
    task_name    : str   = 'TreasureHunt'
    task_version : float = 0.0

    # Treasure Hunt Epochs
    navigation_start_times : list = field(default_factory=list, metadata={'info': 'Start times of navigation epochs', 'units' : 'seconds'})
    navigation_stop_times : list = field(default_factory=list, metadata={'info': 'Stop times of navigation epochs', 'units' : 'seconds' })

    def __post_init__(self):
        self.load_navigation_epochs()
        super().__post_init__()
    
    def load_navigation_epochs(self):
        """ Load navigation periods as epochs of intertest"""
        self.epoch_start_times = self.navigation_start_times
        self.epoch_stop_times  = self.navigation_stop_times


@dataclass(kw_only=True)
class Navigation:
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
class TreasureHuntData:
    subject = None
    session = None
    navigation = None
    headdirection = None
    stimuli = None
    memory = None





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

    