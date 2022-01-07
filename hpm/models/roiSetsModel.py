
from hpm.models.mcaModel import McaROI
import copy
class RoiModel():
    def __init__(self):

        self.rois = []
        self.file_rois = []
        

    def add_roi( self, roi):
        self.rois.append(roi)

    def add_rois( self, rois):
        for r in rois:
            self.rois.append(r)

    def clear_rois(self):
        self.__init__()

    def get_rois(self):
        return self.rois

    def clear_file_rois(self):
        self.file_rois = []

    def add_file_rois(self, rois):
        if len(self.file_rois) == 0:
            self.file_rois = rois
        else:
            for r in rois:
                new = True
                for fr in self.file_rois:
                    if r == fr:
                        new = False
                if new:
                    self.file_rois.append(r)
        
    def set_file_rois(self, rois):
        self.file_rois = rois
        

    def get_rois_for_use(self):

        rois_out = self. rois + self. file_rois

        # Sort ROIs.  This sorts by left channel.
        self.display_rois = tempRois = copy.copy(rois_out)
        self.display_rois.sort()
        return self.display_rois
    
    def delete_roi(self, index):
        """
        This procedure deletes the specified region-of-interest from the model.

        Inputs:
            index:  The index of the ROI to be deleted, range 0 to len(mca.rois)
            

        """
        roi = self.display_rois[index]
        if roi in self.rois:
            ind = self.rois.index(roi)
            del self.rois[index]
        if roi in self.file_rois:
            ind = self.file_rois.index(roi)
            del self.file_rois[index]

class RoiSet():
    def __init__(self):

        self.roi_set = []


