
from hpm.models.mcaModel import McaROI
import copy




class RoiModel():
    def __init__(self):

        self.rois = {}
        self.file_rois = {}
        self.detector_rois = {}
        self.roi_sets = {}
        self.display_rois = {}

    def add_roi( self, roi, element =0):
        self._add_roi(roi, element)
        

    def add_rois( self, rois, element =0):
        for r in rois:
            self._add_roi(r, element)

    def get_sets(self, element =0):
        rois = []
        file_rois = []
        det_rois = []
        if element in self.rois:
            rois = self.rois[element]
        if element in self.file_rois:
            file_rois = self.file_rois[element]
        if element in self.detector_rois:
            det_rois = self.detector_rois[element]
        rois = rois + file_rois + det_rois

        labels = {}
        for r in rois:
            label = r.label.split(' ')[0]
            if not label in labels:
                labels[label]=True
        
        for set in labels:
            if set in self.roi_sets[element]:
                labels[set]= self.roi_sets[element][set]
        
        return labels

    def edit_roi_name(self, ind, name, element =0):
        roi = self.display_rois[element][ind]
        roi.label = name
        self.roi_sets[element] =  self.get_sets( element)

    def clear_rois(self, element =0):
        self.__init__()

    def get_rois(self, element =0):
        return self.rois[element]

    def clear_file_rois(self, element =0):
        self.file_rois[element] = []

    def clear_det_rois(self, element =0):
        self.detector_rois[element] = []


    def add_file_rois(self, rois, element =0):
        
        self._add_rois(rois,'file', element)

    def add_det_rois(self, rois, element =0):
        
        self._add_rois(rois,'detector', element)    

    def _add_rois(self, rois, type, element =0):
        R = None
        if type == 'file':
            R = self.file_rois[element]
        elif type == 'detector':
            R = self.detector_rois[element]
        if R != None:
            for r in rois:
                new = True
                for fr in R:
                    if r == fr:
                        new = False
                if new:
                    if element in self.rois:
                        self._delete_if_in_list(r, self.rois[element], element)
                    if element in self.file_rois:
                        self._delete_if_in_list(r, self.file_rois[element], element)
                    if element in self.detector_rois:
                        self._delete_if_in_list(r, self.detector_rois[element], element)
                    R.append(r)
                    label = r.label.split(' ')[0]
                    if not element in self.roi_sets:
                        self.roi_sets[element] = {}
                    if not label in self.roi_sets[element]:
                        self.roi_sets[element][label]=True    
                
        
    def set_file_rois(self, rois, element =0):
        self.file_rois[element] = []
        self.add_file_rois(rois, element)

    def set_det_rois(self, rois, element =0):
        self.detector_rois[element] = []
        self.add_det_rois(rois, element)

    def set_rois(self, rois, element =0):
        self.__init__()
        self.add_rois(rois, element)

    def _delete_if_in_list(self, roi, roi_list, element =0):
        # deletes rois with the same label unless the label is ''
        label = roi.label
        if label != '':
            current_rois = roi_list
            current_labels = {}
            if len(current_rois):
                for i, c_roi in enumerate(current_rois):
                    current_labels[c_roi.label] = i
            if label in current_labels:
                del roi_list[ current_labels[label]]
        
    def _add_roi(self, roi, element =0):
        if element in self.rois:
            self._delete_if_in_list(roi, self.rois[element], element)
        if element in self.file_rois:
            self._delete_if_in_list(roi, self.file_rois[element], element)
        if element in self.detector_rois:
            self._delete_if_in_list(roi, self.detector_rois[element], element)
        if not element in self.rois:
            self.rois[element] = []
        self.rois[element].append(roi)
        label = roi.label.split(' ')[0]
        if not element in self.roi_sets:
            self.roi_sets[element] = {}
        if not label in self.roi_sets[element]:
            self.roi_sets[element][label]=True

    def change_roi_set_use(self, name, use, element =0):
        self.roi_sets[element][name] = use

    def get_rois_for_use(self, element =0):

        rois = []
        file_rois = []
        det_rois = []
        if element in self.rois:
            rois = self.rois[element]
        if element in self.file_rois:
            file_rois = self.file_rois[element]
        if element in self.detector_rois:
            det_rois = self.detector_rois[element]
        rois = rois + file_rois + det_rois
        rois_out = []
        for r in rois:
            label = r.label.split(' ')[0]
            if self.roi_sets[element][label]:
                rois_out.append(r)
        # Sort ROIs.  This sorts by left channel.
        self.display_rois[element] = copy.copy(rois_out)
        self.display_rois[element].sort()
        return self.display_rois[element]

    def delete_roi_by_name(self, name, element =0):
        if len(name):
            
            for i, roi in enumerate(self.display_rois[element]):
                if roi.label == name:
                    self.delete_roi(i, element)
                    break

        
    def delete_roi(self, index, element =0):
        """
        This procedure deletes the specified region-of-interest from the model.

        Inputs:
            index:  The index of the ROI to be deleted, range 0 to len(mca.rois)
            

        """
        roi = self.display_rois[element][index]
        
        if element in self.rois:
            for r in self.rois[element]:
                if r == roi:
                    ind = self.rois[element].index(r)
                    self.rois[element].remove(self.rois[element][ind])
                    break
        if element in self.file_rois:
            for r in self.file_rois[element]:
                if r == roi:
                    ind = self.file_rois[element].index(r)
                    self.file_rois[element].remove(self.file_rois[element][ind])
                    break
        if element in self.detector_rois:
            for r in self.detector_rois[element]:
                if r == roi:
                    ind = self.detector_rois[element].index(r)
                    self.detector_rois[element].remove(self.detector_rois[element][ind])
                    break
        if element in self.display_rois:        
            del self.display_rois[element][index]
        
        self.roi_sets[element] =  self.get_sets( element)


