from ptsa.data.filters import MorletWaveletFilter

class EEGAnalysis:
    def __init__(self, data):
        self.data = data

    
    def bandpass_eeg(self):
        pass

    def filter_loise(self):
        pass


class StimulationAnalysis(EEGAnalysis):
    def __init__(self, data):
        super().__init__(data)
    

    def load_stimulation_events_eeg(self):
        events = self.data.events
        stimulation_events = events[events['type'] == 'STIM_OFF']
        self.data.load_events_eeg(
            events = stimulation_events,
            rel_start_ms = -500,
            rel_stop_ms = 2000
            )

    
        
    

        