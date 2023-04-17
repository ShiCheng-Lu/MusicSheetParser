from common import Bbox, Label
from processor.note_processor import Note, Staff
import math

from common.note import Bar

class BarProcessor(Bar):
    def __init__(self, section: Label, staff: Staff, labels: list[Label]):
        self.section = section
        self.staff = staff
        self.notes: list[Note] = []
        self.labels = labels

    # def rel_position(self, bbox: Bbox):
    #     '''
    #     get the relative position of a bbox based on the center of the bbox and the staff
    #     '''
    #     center = (bbox.y_min + bbox.y_max) / 2
    #     staff_center = (self.staff.y_max + self.staff.y_min) / 2
    #     rel_position = round((staff_center - center) / (self.staff.height / 8))
    #     return int(rel_position)

    def process(self):
        mods: list[Label] = []
        for label in self.labels:
            if 'notehead' in label.name:
                # make noteheads a little larger for better modifier detection
                size_offset = (label.x_max - label.x_min) * 0.05 # extend by 5%
                label.x_min -= size_offset
                label.x_max += size_offset
                self.notes.append(Note(label, self.staff.clef, self.staff))
            elif 'rest' in label.name:
                self.notes.append(Note(label, self.staff.clef, self.staff))
            elif 'clef' in label.name:
                self.staff.clef = label
            elif 'accidental' in label.name:
                # offset accidentals right to overlap them into the note they are modifying
                size_offset = (label.x_max - label.x_min)
                label.x_min += size_offset
                label.x_max += size_offset
                mods.append(label)
            elif 'augmentationDot' in label.name:
                # offset augmentationDot left to overlap the note
                size_offset = (label.x_max - label.x_min)
                label.x_min -= size_offset
                label.x_max -= size_offset
                mods.append(label)
            elif 'key' in label.name:
                label.x_min = 0
                label.x_max = math.inf
                mods.append(label)
            elif any(mod_name in label.name for mod_name in ['flag', 'beam', 'slur', 'tie']):
                label.y_min = 0
                label.y_max = math.inf
                mods.append(label)
            else:
                mods.append(label)
        
        for mod in mods:
            for note in self.notes:
                if mod.intersects(note.label):
                    note.modify(mod)
        
        for note in self.notes:
            note.complete()
    
    def validate(self, duration):
        for note in self.notes:
            pass

        pass

