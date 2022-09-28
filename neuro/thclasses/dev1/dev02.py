

class Session:
    def __init__(self, nwbfile):
        self.nwb = nwbfile
        

class HeadDirectionCell:
    """
    """
    def __init__(self, nwbfile, uix):
        self.nwb = nwbfile
        self.uix = uix

        self.subject = self.nwb.subject.subject_id
        self.session = self.nwb.session_id

    def load_data(self):
        self.spikes = self.nwb.units.