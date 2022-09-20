
from neuro.components import * 
import neuro



class Experiment:
    def __init__(self, id = None, io = None):
        self.id = id

        # Components
        self.io = io

        def __post_init__(self):
            self.load_data()

    def load_data(self):
        self.io.load()

class nwbExperiment(Experiment):
    def __init__(self, id = None, nwb = None, task = 'TreasureHunt'):

        # NWB file or NWBIO class
        if type(nwb) ==  neuro.components.io.NWBIO:
            super().__init__(id, io = nwb)
        else:
            super().__init__(id, io = NWBIO(nwb))

        # Components 
        self.subject = None
        self.session = None

    def populate(self):
        self.subject = Subject(id = io.subject_id)

        # Task Specific Session Data
        if self.task == 'TreasureHunt' or self.task == 'TH':
            self.session = TreasureHuntSession(
                id = io.session_id,
                task_name = self.task,
                session_start_time = 0.0,
                session_stop_time = io.nwb.trials['stop_time'][-1],
                navigation_start_times = io.nwb.trials['navigation_start'][:],
                navigation_stop_times = io.nwb.trials['navigation_stop'][:]
            )
        else:
            self.session = Session(
                id = io.session_id,
                session_start_time = 0.0,
                session_stop_time = io.nwb.trials['stop_time'][-1],
                epoch_start_times = io.nwb.trials['navigation_start'][:],
                epoch_stop_times = io.nwb.trials['navigation_stop'][:]
            )
        

class nwbSingleUnitExperiment(nwbExperiment):
    def __init__(self, id = None, nwb = None, unit_ix = None):
        super().__init__(id, nwb)

        self.unit_ix = unit_ix
        
        # Components
        self.neuron = None

    def populate(self):
        super().populate()
        self.neuron = Neuron(
            # ID
            id = self.subject.id + self.session.id + f'__unit{self.unit_ix}',
            ix = self.unit_ix,
            
            # Data
            spikes = self.io.nwb.get_unit_spike_times(self.unit_ix),
            
            # Relations
            io = self.io,
            subject = self.subject,
            session = self.session
        )

    


