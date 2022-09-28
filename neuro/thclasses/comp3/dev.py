
from dataclasses import dataclass, field
import numpy as np


from neuro.comp3.io import NWBIO




class SSSExperiment:
    """
    Single Subject Session Experiment
    Determines correct data loading scheme, organizes components
    """

    def __init__(self, subject_id, montage_id, task_id, source_id, analysis_id, filepath):
        self.subject_id = subject_id
        self.task_id = task_id
        self.montage_id = montage_id
        self.source_id = source_id
        self.analysis_id = analysis_id
        self.filepath = filepath


        # Components
        self.io = None
        self.data = None
        self.signal = None
        self.analysis = None

    
    def load_io(self):
        if self.source_id == 'NWB':
            self.io = NWBIO(nwb = self.filepath)
        elif self.source_id == 'RAM':
            print('RAM load not implemented')
            self.io = None
        else:
            raise ValueError(self.source_id)

    def load_data(self):
        self.io.extract_data(self.task_id)
        self.data = self.io.data
        
    def load_signal(self):
        self.signal = self.io.extract_signal()



