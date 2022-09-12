import dataclasses
from dataclasses import dataclass, field 


from neuro.components import *

@dataclass(kw_only=True)
class NavigationBehavior:
    # Positions
    x : list = field(default_factory=list, metadata={'info': 'Player x position'})
    y : list = field(default_factory=list, metadata={'info': 'Player y position'})

@dataclass(kw_only=True)
class MemoryBehavior:
    

@dataclass(kw_only=True)
class Behavior:
    navigation: NavigationBehavior = None
    memory: MemoryBehavior = None
    pass




@dataclass(kw_only=True):
class TreasureHuntBehavior(Behavior):
    # Positions

    # 

