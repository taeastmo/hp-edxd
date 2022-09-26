class epicsMCA(MCA):
 
    def __init__(self, *args,  **kwargs):
        super().__init__()

    def get_rois(self):
        rois = []
        #gets rois from detector
        super().set_rois(rois, source='detector')

    def set_rois(self, rois, energy=0, detector = 0, source='controller'):
        super().set_rois(rois, source=source)

    def add_roi(self, roi, energy=0, detector = 0, source='controller'):
        super().add_roi(roi, energy, detector)
        self.set_rois(self.rois[detector],source=source)
        
    def add_rois(self, rois, energy=0, detector = 0, source='controller'):
        super().add_rois(rois, source=source)
        self.set_rois(self.rois[detector], source=source)

    def delete_roi(self, index, detector = 0):
        super().delete_roi(index, detector)
        self.set_rois(self.rois[detector])

    def clear_rois(self, source):
        self.set_rois([],source=source)
