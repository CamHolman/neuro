
import neuro
#from neuro.components import * 

from neuro.components.io import NWBIO
from neuro.components.subject import Subject 
from neuro.components.session import Session, TreasureHuntSession
from neuro.components.neuron import Neuron
from neuro.components.behavior import Behavior, NavigationBehavior, HeadDirectionBehavior, MemoryBehavior


class Experiment:
    def __init__(self, id = None, task = None, io = None):
        self.id = id
        self.task = task

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
            super().__init__(id, task, io = nwb)
        else:
            super().__init__(id, task, io = NWBIO(nwb))


        # Components 
        self.subject = None
        self.session = None
        self.behavior = None

    def populate(self):
        self.subject = Subject(id = self.io.subject_id)

        # Task Specific Session Data
        if self.task == 'TreasureHunt' or self.task == 'TH':
            self.session = TreasureHuntSession(
                id = self.io.session_id,
                #task_name = self.task,
                session_start_time = 0.0,
                session_stop_time = self.io.nwb.trials['stop_time'][-1],
                navigation_start_times = self.io.nwb.trials['navigation_start'][:],
                navigation_stop_times = self.io.nwb.trials['navigation_stop'][:]
            )
        else:
            self.session = Session(
                id = self.io.session_id,
                session_start_time = 0.0,
                session_stop_time = self.io.nwb.trials['stop_time'][-1],
                epoch_start_times = self.io.nwb.trials['navigation_start'][:],
                epoch_stop_times = self.io.nwb.trials['navigation_stop'][:]
            )

        # Behavior
        self.behavior = Behavior(
            navigation = NavigationBehavior(
                xy = self.io.nwb.acquisition['position']['player_position'].data[:],
                times = self.io.nwb.acquisition['position']['player_position'].timestamps[:]
            ),
            head_direciton = HeadDirectionBehavior(
                degrees = self.io.nwb.acquisition['heading']['direction'].data[:],
                times = self.io.nwb.acquisition['heading']['direction'].timestamps[:]
            ),
            memory = None
        )




class nwbSingleUnitExperiment(nwbExperiment):
    def __init__(self, id = None, nwb = None, unit_ix = None):
        super().__init__(id, nwb)

        self.unit_ix = unit_ix
        
        # Components
        self.neuron = None

        # Options
        self.running_single = True

    def populate(self):
        super().populate()
        self.neuron = Neuron(
            # ID
            id = f'{self.subject.id}__{self.session.id}__unit{self.unit_ix}',
            ix = self.unit_ix,
            
            # Data
            spikes = self.io.nwb.units.get_unit_spike_times(self.unit_ix),
            
            # Relations
            exp = self,
            io = self.io,
            subject = self.subject,
            session = self.session
        )

class nwbMultiUnitExperiment(nwbExperiment):
    def __init__(self, id = None, nwb = None):
        super().__init__(id, nwb)

        # Data
        self.neuron_count = len (self.io.nwb.units)

        # Components
        self.neurons = None

        # Options
        self.restrict_unit_ix_range = True
        self.unit_ix_range = [0,10] 

    def populate(self):
        # Pupulate session level data
        super().populate()

    def collect_neurons(self):
        # Set Range
        if self.restrict_unit_ix_range:
            uix_range = range(self.unit_ix_range[0], self.unit_ix_range[1])
        else:
            uix_range = range(self.neuron_count)

        # Collect Neurons
        for uix in uix_range:
            neuron = Neuron(
                id = f'{self.subject.id}__{self.session.id}__unit{self.unit_ix}',
                ix = uix,
                spikes = self.io.nwb.units.get_unit_spike_times(uix),
                exp = self,
                io = self.io,
                subject = self.subject,
                session = self.session
            )
            self.neurons.append(neuron)
        
class SubjectEEGExperiment(Experiment):
    def __init__(self, subject, task, montage):
        pass

    


class HeadDirectionAnalysis:
    def __init__(self, IO, Neuron, Session, HeadDirectionBehavior):
        self.io = IO
        self.neuron = Neuron
        self.session = Session
        self.headdirection = HeadDirectionBehavior
        
        self.occupancy = self.headdirection.occupancy

    def compute_occupancy(self):
        pass

    def run(self):
        pass
        





