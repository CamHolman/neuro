
from neuro.stim.RAMData import RAMSubjectData, RAMGroupData, get_subjects_and_montages

class SubjectExperiment:
    """
    A wrapper
    """
    def __init__(self, task, isubject, source_id, analysis_id):

        self.task=task
        self.isubject = isubject
        self.source_id = source_id
        self.analysis_is = analysis_id


        self.analysis = None
    
    def load_subject(self):
        

        self.data = RAMSubjectData(self.task, self.subject, self.montage)
        pass

    def save():
        pass

class GroupExperiment:
    """
    A group wrapper
    """
