import re
from common.music import Note, TONE_MAP
from common.label import Label

class NoteProcessor(Note):
    def __init__(self, label: Label, clef: Label, staff: Label):
        super().__init__(label.bbox, label.name)

        self.modifiers: list[Label] = []
        self.clef = clef
        self.staff = staff

    def _rel_position(self, notehead: Label):
        note_center = (notehead.y_min + notehead.y_max) / 2

        # use whether note in inspace to more accurately determine relative position
        # if 'InSpace' in notehead.name:
        #     rel_position = round((self.staff_center - note_center - self.offset_size) / (self.offset_size * 2)) * 2 + 1
        # else:
        #     rel_position = round((self.staff_center - note_center) / (self.offset_size * 2)) * 2
        
        rel_position = round((self.staff_center - note_center) / self.offset_size)

        return int(rel_position)

    def _get_semitone(self, notehead: Label):
        self.pitch = self._rel_position(notehead)
        # offset rel_position to number of lines from A4 (tuned at 440Hz)
        match self.clef.name:
            case 'clefG': # treble clef
                self.pitch += 1
            case 'clefCAlto':
                self.pitch -= 5
            case 'clefCTenor':
                self.pitch -= 7
            case 'clefF': # base clef
                self.pitch -= 11

        # offset = self.staff_offsets[rel_position % 7]
        self.modifier = 0
        # apply any flat/sharp modifiers
        notehead_size = notehead.y_max - notehead.y_min
        for modifier in self.modifiers:
            mod_y = (modifier.y_max + modifier.y_min) / 2
            if 'Flat' in modifier.name:
                mod_y = (mod_y + modifier.y_max) / 2
            if mod_y < notehead.y_min + notehead_size / 4 or mod_y > notehead.y_max - notehead_size / 4:
                continue

            if 'Natural' in modifier.name:
                self.modifier = 0
            elif 'DoubleSharp' in modifier.name:
                self.modifier = 2
            elif 'Sharp' in modifier.name:
                self.modifier = 1
            elif 'DoubleFlat' in modifier.name:
                self.modifier = -2
            elif 'Flat' in modifier.name:
                self.modifier = -1
        

    def _get_pitch(self):
        if 'rest' in self.name:
            return

        self.staff_center = (self.staff.y_min + self.staff.y_max) / 2
        self.offset_size = (self.staff.y_max - self.staff.y_min) / 8

        self._get_semitone(self)

    def _get_duration(self):
        whole_note_len = 0.75 # because tempo was 3/4

        if 'DoubleWhole' in self.name:
            self.duration = 2 * whole_note_len
        elif 'Whole' in self.name:
            self.duration = 1 * whole_note_len
        elif 'Half' in self.name:
            self.duration = 0.5
        elif 'Quarter' in self.name:
            self.duration = 0.25
        elif 'rest' in self.name:
            num = re.search(r'\d+', self.name).group()
            self.duration = 1 / int(num)
        elif any('flag' in mod.name for mod in self.modifiers): 
            # noteheadBlack, duration determined by flag
            mod: str = next(mod.name for mod in self.modifiers if 'flag' in mod.name)
            num = re.search(r'\d+', mod).group()
            self.duration = 1 / int(num)
        else: 
            # noteheadBlack, duration determined by beam(s)
            beam_count = sum('beam' == mod.name for mod in self.modifiers)
            self.duration = 1 / (2 ** (beam_count + 2))

        if any(mod.name == "augmentationDot" for mod in self.modifiers):
            self.duration = self.duration * 1.5

    def modify(self, labels):
        if type(labels) is Label:
            labels = [labels]

        self.modifiers.extend(labels)

        return self
    
    def complete(self):
        self._get_pitch()
        self._get_duration()

        return self

    def __repr__(self):
        return f"{'rest' if self.pitch == None else TONE_MAP[self.pitch]} {self.duration}"
