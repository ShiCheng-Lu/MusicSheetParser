from common.label import Label
from common.music import Bar, Staff
from processor.note_processor import NoteProcessor
import math
import processor.staff_utils

class BarProcessor(Bar):
    def __init__(self, section: Label, staff: Staff):
        super().__init__(section.bbox, section.name)
        self.section = section
        self.parent_staff = staff
        self.notes: list[NoteProcessor] = []
        self.labels: list[Label] = []

        if self.parent_staff.clef == None:
            self.parent_staff.clef = Label([0, 0, 0, 0], "clefF")
    
    def process(self):
        self.labels.sort(key=lambda x: x.x_min)

        mods: list[Label] = []
        for label in self.labels:
            if 'notehead' in label.name:
                # make noteheads a little larger for better modifier detection
                size_offset = (label.x_max - label.x_min) * 0.1 # extend by 5%
                label.x_min -= size_offset
                label.x_max += size_offset
                self.notes.append(NoteProcessor(label, self, self.parent_staff))
            elif 'rest' in label.name:
                self.notes.append(NoteProcessor(label, self, self.parent_staff))
            elif 'clef' in label.name:
                self.parent_staff.clef = label
            elif 'accidental' in label.name:
                # accidentals apply to the entire bar
                label.x_max = math.inf
                mods.append(label)
            elif 'augmentationDot' in label.name:
                # offset augmentationDot left to overlap the note
                size_offset = (label.x_max - label.x_min) * 2
                label.x_min -= size_offset
                label.x_max -= size_offset
                mods.append(label)
            elif 'key' in label.name:
                # add key to staff
                match label.name:
                    case 'keyFlat':
                        key = -1
                    case 'keySharp':
                        key = 1
                    case 'keyNatural':
                        key = 0
                    case _:
                        continue # keyboardPedalPad, ignored
                pitch = processor.staff_utils.pitch_from_pos(self.parent_staff, label)
                self.parent_staff.keys[pitch % 7] = key
            else:
                mods.append(label)
        
        for mod in mods:
            mod_orig = mod
            for note in self.notes:
                mod = mod_orig
                if mod_orig.name == 'beam':
                    mod = mod_orig.copy()
                    if mod.y_min > note.y_max:
                        mod.move(self.parent_staff.height / 8, 0)
                    elif mod.y_max < note.y_min:
                        mod.move(-self.parent_staff.height / 8, 0)
                    mod.y_min = 0
                    mod.y_max = math.inf
                
                if 'flag' in mod_orig.name:
                    mod = mod_orig.copy()
                    if mod.y_min < note.y_min:
                        mod.move(- self.parent_staff.height / 8, 0)
                    mod.y_min = 0
                    mod.y_max = math.inf

                if mod.intersects(note):
                    note.modify(mod)
        
        for note in self.notes:
            note.complete()
    
    def validate(self, duration):
        for note in self.notes:
            pass

        pass

