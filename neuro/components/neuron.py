from dataclasses import dataclass, field

from neuro.components import *

from neuro.components.session import Session 

# -NEURON BASE- 
@dataclass(kw_only=True)
class _Neuron:
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
    
    id        : str              = field(default_factory=str)
    ix        : int              = field(default_factory=int)
    session   : Session          = None
    
    #subject   : Subject          = None
    #recording : NeuralRecording  = None
    #electrode : Electrode        = None
    #contact   : ElectrodeContact = None

    # Data
    spikes : list = field(default_factory=list)
    
    #def __post_init__():
    #    super().__init__(**kwargs)



class Neuron(_Neuron):
    """
    Class for Neuron
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def spike_count(self):
        return len(self.spike_train)

    @property
    def firing_rate(self):
        return self.spike_count / self.recording.recording_length 


# -- NEURON TYPES --
@dataclass(kw_only=True)
class _HeadDirectionNeuron:
    
    # HD Data
    hd_occupancy : list = field(default_factory=list, metadata={'info': 'Seconds spent in each bin', 'unit':'seconds'})
    hd_times     : list = field(default_factory=list, metadata={'info': 'Times at which head direction was recorded', 'unit':'seconds'})
    hd_degrees   : list = field(default_factory=list, metadata={'info': 'Recorded head directions, matched to hd_times', 'unit':'degrees'})
    
    # Config
    binsize :int = 1
    smooth = True
    windowsize = 23
    
    
    #def __post_init__():
    #    super().__init__(**kwargs) 


class HeadDirectionNeuron(_HeadDirectionNeuron, Neuron):
    def __init__(self, **kwargs):
        super().__init__(**{k: v for k, v in kwargs.items()
                            if k in _HeadDirectionNeuron.__dataclass_fields__.keys()})
        Neuron.__init__(self, **{k: v for k, v in kwargs.items()
                            if k not in _HeadDirectionNeuron.__dataclass_fields__.keys()})

        
        
    def compute_occupancy(self):
            # get ms timepoints in seconds during epochs of interest
            timepoints = subset_epoch_times(np.arange(np.ceil(session.session_length*1e3))/1e3, self.session.epoch_start_times, self.session.epoch_stop_times)
            head_directions = compute_head_directions(timepoints, self.hd_times, self.hd_degrees)
            self.occupancy = compute_head_direction_histogram(head_directions, self.binsize, self.windowsize)
            
     