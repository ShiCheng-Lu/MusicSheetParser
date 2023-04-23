from processor.note_processor import Note
import math
from common.label import Label
from common.music import Music
import processor.staff_utils as staff_utils
import operator
import cv2
from processor.section_processor import SectionProcessor

'''
Parser:
1. object detection with model
2. split by staff and bar
3. re-detect bars that are 'invalid' (optionally re-detect every bar)
4. output to manual editor
'''

class MusicParser(Music):
    def __init__(self, name):
        super().__init__()
        self.image = cv2.imread(name, cv2.IMREAD_GRAYSCALE)

        self.sections: list[SectionProcessor] = []
        self.labels: list[Label] = []

        self.staffs = staff_utils.get_staffs(self.image)
        for staff in self.staffs:
            staff.parent_music = self

        for section in staff_utils.section(self.image):
            section_staffs = []
            for staff in self.staffs:
                if staff.intersects(section):
                    section_staffs.append(staff)
            self.sections.append(SectionProcessor(section, section_staffs, self))

            if self.group == None:
                self.group = len(section_staffs)
    
    def process(self):
        for section in self.sections:
            section.process()
    
    def set_time_sig(self, time_sigs):
        # top left most time signature
        time_sig_num = min(time_sigs, key=lambda label: label.x_min + label.y_min)
        if time_sig_num.name == 'timeSigCommon':
            self.time_sig = [4, 4]
            return
        if time_sig_num.name == 'timeSigCutCommon':
            self.time_sig = [2, 2]
            return
        # top most directly below time_sig_num
        time_sig_den = max(time_sigs, key=lambda label: label.x_min + label.y_min)
        for time_sig in time_sigs:
            if time_sig == time_sig_num:
                continue
            if time_sig.x_min > time_sig_num.x_max or time_sig.x_max < time_sig_num.x_min:
                continue
            if time_sig_den == None or time_sig_den.y_min > time_sig.y_min:
                time_sig_den = time_sig

        self.time_sig[0] = int(time_sig_num.name[-1])
        self.time_sig[1] = int(time_sig_den.name[-1])
    
    @property
    def notes(self):
        notes = []
        for section in self.sections:
            notes.extend(section.notes)
        return notes

