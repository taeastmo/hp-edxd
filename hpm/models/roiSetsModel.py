
from hpm.models.mcaModel import McaROI

class RoiModel():
    def __init__(self):

        self.sets = {}
        self.file_rois = []

    def add_roi_set( self, label, rois):

        self.sets[label] = rois
        

class RoiSet():
    def __init__(self):

        self.roi_set = []


