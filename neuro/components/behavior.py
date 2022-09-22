import dataclasses
from dataclasses import dataclass, field 


from neuro.components import *



@dataclass(kw_only=True)
class NavigationBehavior:
    # Positions
    xy    : list = field(default_factory=list, metadata={'info': 'Player x,y position'})
    times : list = field(default_factory=list, metadata={'info': 'times when position is recorded', 'units': 'sec'})


@dataclass(kw_only=True)
class HeadDirectionBehavior:
    degrees   : list = field(default_factory=list, metadata={'info': 'Player head direction', 'units': 'degrees'})
    times     : list = field(default_factory=list, metadata={'info': 'times when HD is recorded', 'units': 'sec'})
    occupancy : list = field(default = None, metadata={'info': 'time spent in each bin', 'units': 'sec'})


@dataclass(kw_only=True)
class Stimuli:
    stimuli                    : list  = field(default_factory=list, metadata={'info': 'presented stimuli'})
    stimuli_presentation_times : list  = field(default_factory=list, metadata={'info': 'times when stimuli are presented', 'units': 'sec'})
    recall_presentation_times  : list  = field(default_factory=list, metadata={'info': 'times when stimuli are presented', 'units': 'sec'})

@dataclass(kw_only=True)
class MemoryBehavior:
    stimuli                    : Stimuli  = None
    recalled_stimuli           : list = field(default_factory=list, metadata={'info': 'boolean list recalled or not; index corresponds with stimuli', 'units': 'bool'})
    recall_times               : list = field(default_factory=list, metadata={'info': 'time of recall response', 'units': 'sec'})
                                                                                        


@dataclass(kw_only=True)
class Behavior:
    navigation     : NavigationBehavior    = None
    head_direction : HeadDirectionBehavior = None
    memory         : MemoryBehavior        = None
    stimuli        : Stimuli               = None
    


@dataclass(kw_only=True)
class TreasureHuntBehavior(Behavior):
    # Positions

    # 
    pass
