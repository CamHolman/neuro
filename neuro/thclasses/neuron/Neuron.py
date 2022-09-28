"""
Class object for neron
"""

from dataclasses import dataclass, field

from neuro.neuron.neuron_utils import *

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
    exp  = None
    data = None

    # -- Session Level -- 
    @property
    def spike_count(self):
        return len(self.spikes)

    @property
    def firing_rate(self, start = None, stop = None):
        return self.spike_count / self.data.session.session_length 

    @property
    def firing_rate_over_time(self, spikes = None, start_time = None, stop_time = None, window = 1, step = 0.1):
        spikes = self.spikes if spikes is None else spikes
        start_time = self.data.session.session_start_time if start_time is None else start_time
        stop_time = self.data.session.session_stop_time if stop_time is None else stop_time
        frs, times = compute_firing_rate_over_time(spikes, start_time, stop_time, window, step)
        return frs, times


    # -- Epoch Level --
    @property 
    def epoch_spikes(self, spikes = None, epoch_start_times = None, epoch_stop_times = None):
        spikes = self.spikes if spikes is None else spikes
        epoch_start_times = self.data.session.epoch_start_times if epoch_start_times is None else epoch_start_times
        epoch_stop_times = self.data.session.epoch_stop_times if epoch_stop_times is None else epoch_stop_times 
        return subset_epoch_events(self.spikes, epoch_start_times, epoch_stop_times)

    @property
    def epoch_spike_count(self):
        return len(self.epoch_spikes)

    @property
    def epoch_firing_rate(self):
        return self.epoch_spike_count / self.session.epoch_length

    @property 
    def epoch_firing_rate_over_time(self, spikes = None, epoch_start_times = None, epoch_stop_times = None, 
                                    window = 1, step = 0.1, return_means = False):
        spikes = self.spikes if spikes is None else spikes
        epoch_start_times = self.data.session.epoch_start_times if epoch_start_times is None else epoch_start_times
        epoch_stop_times = self.data.session.epoch_stop_times if epoch_stop_times is None else epoch_stop_times
        if return_means:
            frs, fr_means = compute_epochs_firing_rates_over_time(spikes, epoch_start_times, epoch_stop_times, window, step, True)
            return frs, fr_means
        else:
            frs = compute_epochs_firing_rates_over_time(spikes, epoch_start_times, epoch_stop_times, window, step, False)
            return frs 