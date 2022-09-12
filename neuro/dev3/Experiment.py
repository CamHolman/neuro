from dataclasses import dataclass, field
from keyword import kwlist

from neuro.components import *



@dataclass(kw_only=True)
class _Experiment:
    # ID
    id : str = 'experiment id' 
    ix : int = 'experiment index'

    # Data 
    data: DataIO = None
     
    # Components
    subject: Subject = None
    session: Session = None

    


class Experiment(_Experiment):
    """

    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    
    

    pass

@dataclass(kw_only=True)
class _SingleUnitExperiment:
    pass 

class SingleUnitExperiment(Experiment):
    pass



class HeadDirectionExperiment(SingleUnitExperiment):
    pass