class PersonDetect:
    def __init__(self, lm_list=None, label="NORMAL", sensitivity=0, shoplifting_continous_count=0, pre_label = "NORMAL"):
        self.lm_list = lm_list if lm_list is not None else []
        self.label = label
        self.sensitivity = sensitivity
        self.shoplifting_continous_count = shoplifting_continous_count
        self.pre_label = pre_label
    
    def updatePreLabel(self):
        self.pre_label = self.label
    
    def add_lm(self, c_lm):
        self.lm_list.append(c_lm)