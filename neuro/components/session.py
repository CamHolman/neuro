
from dataclasses import dataclass,field


# @dataclass(kw_only=True)
# class Task:
#     task_name : str = ''
#     task_version : float = 0.0


@dataclass(kw_only=True)
class Session:
    id : str = ''
    session_start_time : float = 0.0
    session_stop_time : float = 0.0
    session_length : float = 0.0
    
    epoch_start_times : list  = field(default_factory=list)
    epoch_stop_times  : list  = field(default_factory=list)


    def __post_init__(self):
        self.session_length = self.session_stop_time - self.session_start_time

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
    #task_name : str = 'Treasure Hunt'
    #task_version : float = field(default= 1.0)
    #blank : str = 'wnweofin'

    # Treasure Hunt Epochs
    navigation_start_times : list = field(default_factory=list, metadata={'info': 'Start times of navigation epochs', 'units' : 'seconds'})
    navigation_stop_times : list = field(default_factory=list, metadata={'info': 'Stop times of navigation epochs', 'units' : 'seconds' })


    player_position : list = field(default_factory=list)

    def __post_init__(self):
        self.load_navigation_epochs()
        super().__post_init__()

    
    def load_navigation_epochs(self):
        """ Load navigation periods as epochs of intertest"""
        self.epoch_start_times = self.navigation_start_times
        self.epoch_stop_times  = self.navigation_stop_times

     

    