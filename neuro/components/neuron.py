from dataclasses import dataclass, field
import numpy as np

from neuro.utils.subset_data import data, subset_epoch_data, subset_epoch_events
from neuro.components.neuron_utils import compute_firing_rate_over_time, compute_epochs_firing_rates_over_time

from neuro.components import *
from neuro.components.session import Session 
from neuro.components.subject import Subject
from neuro.components.io import DataIO


# -NEURON BASE- 
@dataclass(kw_only=True)
class Neuron:
    """
    BaseDataclass for single unit neuron level information

    Atributes
    ---------
    id : str 
        unique identifier
    ix : int
        numbered identifier
    subject: object
        Subject class instance
    recording : object
        NeuralRecording class instance 
    electrode : object
        Electrode class instance 
    contact:
        ElectrodeContact class instance
    
    spikes: 1D arr
        spike times in sec
    """
    # ID
    id : str = field(default_factory=str)
    ix : int = field(default_factory=int)
    
    # Data
    spikes : list = field(default_factory=list)
    
    # Relations
    io      : DataIO  = None
    subject : Subject = None
    session : Session = None
    
    #recording : NeuralRecording  = None
    #electrode : Electrode        = None
    #contact   : ElectrodeContact = None

    # -- Session Level -- 
    @property
    def spike_count(self):
        return len(self.spikes)

    @property
    def firing_rate(self, start = None, stop = None):
        return self.spike_count / self.session.recording_length 

    @property
    def firing_rate_over_time(self, start_time = None, stop_time = None, window = 1, step = 0.1):
        start_time = self.session.session_start_time if start_time is None else start_time
        stop_time = self.session.session_stop_time if stop_time is None else stop_time
        frs, times = compute_firing_rate_over_time(self.spikes, start_time, stop_time, window, step)
        return frs, times

    
    # -- Epoch Level --
    @property 
    def epoch_spikes(self, epoch_start_times = None, epoch_stop_times = None):
        if not epoch_start_times or epoch_stop_times:
            epoch_start_times = self.session.epoch_start_times
            epoch_stop_times = self.session.epoch_stop_times
        return subset_epoch_events(self.spikes, epoch_start_times, epoch_stop_times)

    @property
    def epoch_spike_count(self):
        return len(self.epoch_spikes)

    @property
    def epoch_firing_rate(self):
        return self.epoch_spike_count / self.session.epoch_length

    @property 
    def epoch_firing_rate_over_time(self):

    
    





# # -- NEURON TYPES --
# @dataclass(kw_only=True)
# class HeadDirectionNeuron (Neuron):
    
#     # HD Data
#     hd_occupancy : list = field(default_factory=list, metadata={'info': 'Seconds spent in each bin', 'unit':'seconds'})
#     hd_times     : list = field(default_factory=list, metadata={'info': 'Times at which head direction was recorded', 'unit':'seconds'})
#     hd_degrees   : list = field(default_factory=list, metadata={'info': 'Recorded head directions, matched to hd_times', 'unit':'degrees'})
    
#     # Config
#     binsize    : int  = 1
#     smooth     : bool = True
#     windowsize : int  = 23
    
#     def compute_occupancy(self):
#             # get ms timepoints in seconds during epochs of interest
#             timepoints = subset_epoch_times(np.arange(np.ceil(session.session_length*1e3))/1e3, self.session.epoch_start_times, self.session.epoch_stop_times)
#             head_directions = compute_head_directions(timepoints, self.hd_times, self.hd_degrees)
#             self.occupancy = compute_head_direction_histogram(head_directions, self.binsize, self.windowsize)


# # class __HeadDirectionNeuron(_HeadDirectionNeuron, Neuron):
# #     def __init__(self, **kwargs):
# #         super().__init__(**{k: v for k, v in kwargs.items()
# #                             if k in _HeadDirectionNeuron.__dataclass_fields__.keys()})
# #         Neuron.__init__(self, **{k: v for k, v in kwargs.items()
# #                             if k not in _HeadDirectionNeuron.__dataclass_fields__.keys()})

        
        
    
            
     