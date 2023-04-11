import re
import music
from music import PITCH_MAP
from common import Label

class Note(music.Note):
    def _rel_position(self, notehead: Label):
        note_center = (notehead.y_min + notehead.y_max) / 2

        # use whether note in inspace to more accurately determine relative position
        if 'InSpace' in notehead.name:
            rel_position = round((self.staff_center - note_center - self.offset_size) / (self.offset_size * 2)) * 2 + 1
        else:
            rel_position = round((self.staff_center - note_center) / (self.offset_size * 2)) * 2
        
        return int(rel_position)

    def _get_semitone(self, notehead: Label):
        rel_position = self._rel_position(notehead)
        # offset rel_position to number of lines from A4 (tuned at 440Hz)
        match self.clef.name:
            case 'clefG': # treble clef
                rel_position += 1
            case 'clefCAlto':
                rel_position -= 5
            case 'clefCTenor':
                rel_position -= 7
            case 'clefF': # base clef
                rel_position -= 11
        
        # find number of half tones
        semitones = (rel_position // 7) * 12
        match rel_position % 7:
            case 0: semitones += 0
            case 1: semitones += 2
            case 2: semitones += 3
            case 3: semitones += 5
            case 4: semitones += 7
            case 5: semitones += 8
            case 6: semitones += 10

        # offset = self.staff_offsets[rel_position % 7]
        offset = 0
        # apply any flat/sharp modifiers
        notehead_size = notehead.y_max - notehead.y_min
        for modifier in self.modifiers:
            mod_y = (modifier.y_max + modifier.y_min) / 2
            if 'Flat' in modifier.name:
                mod_y = (mod_y + modifier.y_max) / 2
            if mod_y < notehead.y_min + notehead_size / 4 or mod_y > notehead.y_max - notehead_size / 4:
                continue

            if 'Natural' in modifier.name:
                offset = 0
            elif 'DoubleSharp' in modifier.name:
                offset = 2
            elif 'Sharp' in modifier.name:
                offset = 1
            elif 'DoubleFlat' in modifier.name:
                offset = -2
            elif 'Flat' in modifier.name:
                offset = -1
        semitones += offset
        
        return semitones

    def _get_pitch(self):
        
        if 'rest' in self.label.name:
            return

        self.staff_center = (self.staff.y_min + self.staff.y_max) / 2
        self.offset_size = (self.staff.y_max - self.staff.y_min) / 8

        self.pitch = self._get_semitone(self.label)

    def _get_duration(self):
        whole_note_len = 0.75 # because tempo was 3/4

        if 'DoubleWhole' in self.label.name:
            self.duration = 2 * whole_note_len
        elif 'Whole' in self.label.name:
            self.duration = 1 * whole_note_len
        elif 'Half' in self.label.name:
            self.duration = 0.5
        elif 'Quarter' in self.label.name:
            self.duration = 0.25
        elif 'rest' in self.label.name:
            num = re.search(r'\d+', self.label.name).group()
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

        augmentation = sum(mod.name == "augmentationdot" for mod in self.modifiers)
        self.duration = self.duration * (2 - (1 / 2) ** augmentation)


    def __init__(self, label: Label, clef: Label, staff: Label):
        self.label = label
        self.modifiers: list[Label] = []
        self.clef = clef
        self.staff = staff

        self.pitch = None
        self.duration = None
        self.start_time = None


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
        return f"{'rest' if self.pitch == None else PITCH_MAP[self.pitch]} {self.duration} {self.start_time}"
