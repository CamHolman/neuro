from dataclasses import dataclass


class NWBexperiment:
    def __init__(self, nwb, config):
        self.nwb = nwb
        self.config = config


@dataclass
class _DataHeadDirectionCell:
    pass


class HeadDirectionCell(NWBexperiment):
    def __init__(self, nwb, config, unit_ix, occupancy = []):
        NWBexperiment.__init__(nwb, config)
        self.subject = self.nwb.subject.subject_id
        self.session = self.nwb.session_id
        
        # Unit Data
        self.unit_ix = unit_ix
        self.spikes  = self.nwb.units.get_unit_start_times(unit_ix)

        # Behavioral Data
        self.occupancy = occupancy

        # Task Data 
        self.


        # Default Experiment Congifuration
        self.


    @property
    def spike_count(self):
        return len(self.spikes)

    def compute_occupancy(self):
        

        
