from common.label import Bbox, Label
from common.music import Bar, Staff
from processor.note_processor import NoteProcessor
import math

class BarProcessor(Bar):
    def __init__(self, section: Label, staff: Staff, labels: list[Label]):
        super().__init__(section.bbox, section.name)
        self.section = section
        self.parent_staff = staff
        self.notes: list[NoteProcessor] = []
        self.labels = labels

    # def rel_position(self, bbox: Bbox):
    #     '''
    #     get the relative position of a bbox based on the center of the bbox and the staff
    #     '''
    #     center = (bbox.y_min + bbox.y_max) / 2
    #     staff_center = (self.staff.y_max + self.staff.y_min) / 2
    #     rel_position = round((staff_center - center) / (self.staff.height / 8))
    #     return int(rel_position)
        # default to clefF
        if self.parent_staff.clef == None:
            self.parent_staff.clef = Label([0, 0, 0, 0], "clefF")

    def process(self):
        mods: list[Label] = []
        for label in self.labels:
            if 'notehead' in label.name:
                # make noteheads a little larger for better modifier detection
                size_offset = (label.x_max - label.x_min) * 0.05 # extend by 5%
                label.x_min -= size_offset
                label.x_max += size_offset
                self.notes.append(NoteProcessor(label, self.parent_staff.clef, self.parent_staff))
            elif 'rest' in label.name:
                self.notes.append(NoteProcessor(label, self.parent_staff.clef, self.parent_staff))
            elif 'clef' in label.name:
                self.parent_staff.clef = label
            elif 'accidental' in label.name:
                # offset accidentals right to overlap them into the note they are modifying
                size_offset = (label.x_max - label.x_min)
                label.x_min += size_offset
                label.x_max += size_offset
                mods.append(label)
            elif 'augmentationDot' in label.name:
                # offset augmentationDot left to overlap the note
                size_offset = (label.x_max - label.x_min) * 2
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
                if mod.intersects(note):
                    note.modify(mod)
        
        for note in self.notes:
            note.complete()
    
    def validate(self, duration):
        for note in self.notes:
            pass

        pass

