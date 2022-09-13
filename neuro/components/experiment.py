
from neuro.components import * 
import neuro



class Experiment:
    def __init__(self, id = None, io = None):
        self.id = id
        self.io = io

        def __post_init__(self):
            self.load_data()

    def load_data(self):
        self.io.load()

class nwbExperiment(Experiment):
    def __init__(self, id = None, nwb = None):
        if type(nwb) ==  neuro.components.io.NWBIO:
            super().__init__(id, io = nwb)
        else:
            super().__init__(id, io = NWBIO(nwb))

        self.subject = None
        self.session = None

    def populate(self):
        self.subject = Subject(id = io.subject_id)
        self.session = Session(
            id = io.session_id,
            session_start_time = 0.0,
            session_stop_time = io.nwb.trials['stop_time'][-1],
            epoch_start_times = io.nwb.trials['navigation_start'][:],
            epoch_stop_times = io.nwb.trials['navigation_stop'][:]
        )
        
class nwbSingleUnitExperiment(nwbExperiment):
    def __init__(self, id = None, nwb = None):
        super().__init__(id, nwb)

        self.neuron = None

    def populate(self):
        super().populate()
        self.neuron = None


