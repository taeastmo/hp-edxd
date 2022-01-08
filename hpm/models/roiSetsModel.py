
from hpm.models.mcaModel import McaROI
import copy
class RoiModel():
    def __init__(self):

        self.rois = []
        self.file_rois = []
        self.roi_sets = {}

    def add_roi( self, roi):
        self._add_roi(roi)
        

    def add_rois( self, rois):
        for r in rois:
            self._add_roi(r)

    def get_sets(self):

        rois = self. rois + self. file_rois
        labels = {}
        for r in rois:
            label = r.label.split(' ')[0]
            if not label in labels:
                labels[label]=True
        
        for set in labels:
            if set in self.roi_sets:
                labels[set]= self.roi_sets[set]
        
        return labels

    def edit_roi_name(self, ind, name):
        roi = self.display_rois[ind]
        roi.label = name
        self.roi_sets =  self.get_sets()

    def clear_rois(self):
        self.__init__()

    def get_rois(self):
        return self.rois

    def clear_file_rois(self):
        self.file_rois = []


    def add_file_rois(self, rois):
        
        for r in rois:
            new = True
            for fr in self.file_rois:
                if r == fr:
                    new = False
            if new:
                self.file_rois.append(r)
                label = r.label.split(' ')[0]
                if not label in self.roi_sets:
                    self.roi_sets[label]=True
                
        
    def set_file_rois(self, rois):
        self.file_rois = []
        self.add_file_rois(rois)

    def set_rois(self, rois):
        self.__init__()
        self.add_rois(rois)
        
    def _add_roi(self, roi):
        self.rois.append(roi)
        label = roi.label.split(' ')[0]
        if not label in self.roi_sets:
            self.roi_sets[label]=True

    def change_roi_set_use(self, name, use):
        self.roi_sets[name] = use

    def get_rois_for_use(self):

        file_rois = self.file_rois
        rois = self.rois + self.file_rois
        rois_out = []
        for r in rois:
            label = r.label.split(' ')[0]
            if self.roi_sets[label]:
                rois_out.append(r)
        # Sort ROIs.  This sorts by left channel.
        self.display_rois = copy.copy(rois_out)
        self.display_rois.sort()
        return self.display_rois
    
    def delete_roi(self, index):
        """
        This procedure deletes the specified region-of-interest from the model.

        Inputs:
            index:  The index of the ROI to be deleted, range 0 to len(mca.rois)
            

        """
        roi = self.display_rois[index]
        
        
        for r in self.rois:
            if r == roi:
                ind = self.rois.index(r)
                self.rois.remove(self.rois[ind])
                break
        for r in self.file_rois:
            if r == roi:
                ind = self.file_rois.index(r)
                self.file_rois.remove(self.file_rois[ind])
                break
        del self.display_rois[index]
        
        self.roi_sets =  self.get_sets()

class RoiSet():
    def __init__(self):

        self.roi_set = []


