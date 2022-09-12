
from dataclasses import dataclass,field


@dataclass(kw_only=True)
class Task:
    name: str = ''
    version: float = 0.0


@dataclass(kw_only=True)
class Session:
    id : str = ''
    session_start_time : float = 0.0
    session_stop_time : float = 0.0
    session_length : float = 0.0
    
    epoch_start_times : list = field(default_factory=list)
    epoch_stop_times : list = field(default_factory=list)
    
    def __post_init__(self):
        self.session_length = self.session_stop_time - self.session_start_time
    
    
@dataclass(kw_only=True)
class TreasureHuntSession(Task, Session):
    """
    Class to represent each session of treasure hunt...
    """

    navigation_start_times : list = field(default_factory=list, metadata={'info': 'Start times of navigation epochs', 'units' : 'seconds'})
    navigation_stop_times : list = field(default_factory=list, metadata={'info': 'Stop times of navigation epochs', 'units' : 'seconds' })


    player_position : list = field(default_factory=list)

    
    def load_navigation_epochs(self):
        """ Load navigation periods as epochs of intertest"""
        self.epoch_start_times = self.navigation_start_times
        self.epoch_stop_times  = self.navigation_stop_times

     

    