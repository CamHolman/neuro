
import neuro 
from neuro.components.io import NWBIO
from neuro.comp2.data import TaskDataHandler

"""
Use NWB as data source for all...
"""



class Experiment:
    def __init__(self, id = None, io = None, task = None):
        self.id = id
        self.task = task

        # Components
        self.io = io


    def load_data(self):
        self.io.load()




class nwbExperiment(Experiment):
    def __init__(self, id = None, nwb = None, task = 'TreasureHunt'):

        # Handle NWB file or NWBIO class

        if type(nwb) == NWBIO:
            super().__init__(id, nwb, task)
        else:
            super().__init__(id, NWBIO(nwb), task)

        # Get data based on Task
        print (task)
        TaskData = TaskDataHandler(task).choose_task()
        data = TaskData(nwb = 5)
        

    



class nwbSingleUnitExperiment(nwbExperiment):
    def __init__(self, id = None, nwb = None, data = None): 
        pass


# from dataclasses import dataclass, field

# @dataclass(kw_only=True)
# class Experiment:
#     id = None
#     task = None
#     io = None
#     data = None

#     def __post_init__(self):
#         # Handle NWB file or NWBIO class
#         if type(self.io) is neuro.components.io.NWBIO:
#             super().__init__(id, io = nwb)
#         else:
#             super().__init__(id, io = NWBIO(nwb))

#         self.data = data if data else THData(self.io.nwb) 