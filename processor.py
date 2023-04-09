import numpy as np
import re
import music
import math

class Label:
    def __init__(self, bbox=None, name=None, confidence=None, on_edge=False):
        self.bbox: list[float] = bbox
        self.name: str = name
        self.confidence: float = confidence
        self.on_edge: bool = on_edge
    
    def x_min(self):
        return self.bbox[0]
    
    def y_min(self):
        return self.bbox[1]
    
    def x_max(self):
        return self.bbox[2]
    
    def y_max(self):
        return self.bbox[3]
    
    def intersects(self, other) -> bool:
        return (self.x_max() >= other.x_min() and
                self.x_min() <= other.x_max() and
                self.y_max() >= other.y_min() and
                self.y_min() <= other.y_max())
    
    def intersection(self, other, result=None):
        if result == None:
            result = self
        elif self.confidence > other.confidence:
            result.name = self.name
            result.confidence = self.confidence
        else:
            result.name = other.name
            result.confidence = other.confidence
        
        result.bbox = [
            max(self.x_min(), other.x_min()),
            max(self.y_min(), other.y_min()),
            min(self.x_max(), other.x_max()),
            min(self.y_max(), other.y_max()),
        ]
        return result


    def union(self, other, result=None):
        if result == None:
            result = self
        elif self.confidence > other.confidence:
            result.name = self.name
            result.confidence = self.confidence
        else:
            result.name = other.name
            result.confidence = other.confidence

        result.bbox = [
            min(self.x_min(), other.x_min()),
            min(self.y_min(), other.y_min()),
            max(self.x_max(), other.x_max()),
            max(self.y_max(), other.y_max()),
        ]
        return result
    
    def copy(self, other=None):
        if other == None:
            other = Label(None, None, None)
        other.bbox = self.bbox.copy()
        other.name = self.name
        other.confidence = self.confidence
    
    def area(self):
        return (self.x_max() - self.x_min()) * (self.y_max() - self.y_min())
    
    def __repr__(self):
        return f"{self.name}"

pitchMap = [ # range: -48 to +39
    "A4", "Bb4", "B4", "C5", "Db5", "D5", "Eb5", "E5", "F5", "Gb5", "G5", "Ab5",
    "A5", "Bb5", "B5", "C6", "Db6", "D6", "Eb6", "E6", "F6", "Gb6", "G6", "Ab6",
    "A6", "Bb6", "B6", "C7", "Db7", "D7", "Eb7", "E7", "F7", "Gb7", "G7", "Ab7",
    "A7", "Bb7", "B7", # missing high C8 on standard piano
    # indexed negatively, these are lower than A4
    "A0", "Bb0", "B0", "C1", "Db1", "D1", "Eb1", "E1", "F1", "Gb1", "G1", "Ab1",
    "A1", "Bb1", "B1", "C2", "Db2", "D2", "Eb2", "E2", "F2", "Gb2", "G2", "Ab2",
    "A2", "Bb2", "B2", "C3", "Db3", "D3", "Eb3", "E3", "F3", "Gb3", "G3", "Ab3",
    "A3", "Bb3", "B3", "C4", "Db4", "D4", "Eb4", "E4", "F4", "Gb4", "G4", "Ab4",
]

class Note(music.Note):
    def _rel_position(self, notehead: Label):
        note_center = (notehead.y_min() + notehead.y_max()) / 2

        # use whether note in inspace to more accurately determine relative position
        if 'InSpace' in notehead.name:
            rel_position = np.round((self.staff_center - note_center - self.offset_size) / (self.offset_size * 2)) * 2 + 1
        else:
            rel_position = np.round((self.staff_center - note_center) / (self.offset_size * 2)) * 2
        
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
        semitones = np.floor_divide(rel_position, 7) * 12
        match rel_position % 7:
            case 0: semitones += 0
            case 1: semitones += 2
            case 2: semitones += 3
            case 3: semitones += 5
            case 4: semitones += 7
            case 5: semitones += 8
            case 6: semitones += 10

        # offset = self.staff_offsets[rel_position % 7]
        # # apply any flat/sharp modifiers
        # for modifier in self.modifiers:
        #     mod_y = (modifier.y_max() + modifier.y_min()) / 2
        #     if 'Flat' in modifier.name:
        #         mod_y = (mod_y + modifier.y_max()) / 2
        #     if mod_y < notehead.y_min() or mod_y > notehead.y_max() or modifier.x_min() > notehead.x_min():
        #         continue

        #     if 'Natural' in modifier.name:
        #         offset = 0
        #     elif 'DoubleSharp' in modifier.name:
        #         offset = 2
        #     elif 'Sharp' in modifier.name:
        #         offset = 1
        #     elif 'DoubleFlat' in modifier.name:
        #         offset = -2
        #     elif 'Flat' in modifier.name:
        #         offset = -1
        # semitones += offset
        
        return semitones

    def _get_pitch(self):
        
        if 'rest' in self.label.name:
            return

        self.staff_center = (self.staff.y_min() + self.staff.y_max()) / 2
        self.offset_size = (self.staff.y_max() - self.staff.y_min()) / 8

        self.pitch = self._get_semitone(self.label)

    def _get_duration(self):
        if 'DoubleWhole' in self.label.name:
            self.duration = 2
        elif 'Whole' in self.label.name:
            self.duration = 1
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

        # augmentation = sum(mod.name == "augmentationdot" for mod in self.modifiers)
        # self.duration = self.duration * (2 - (1 / 2) ** augmentation)

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

        return self

    def __repr__(self):
        return f"{'rest' if self.pitch == None else pitchMap[self.pitch]} {self.duration} {self.start_time}"

class NoteGroup:
    def __init__(self, note: Note):
        self.bbox: Label = note.label.copy()
        self.notes: list[Note] = []
    
    def add(self, note: Note):
        self.bbox.union(note.label)
        self.notes.append(note)

class MusicParser:
    def __init__(self, labels: list[Label]):
        self.labels = labels
        
        self._pre_process()
        self._split_labels_by_staffs()
        self._process_labels()
        self._complete_notes()

    def _pre_process(self):
        self.staffs: list[Label] = []
        for label in self.labels:
            
            # REMOVE: for testing only, TODO need to figure out a way to limit bad labels from sheet title
            if label.y_max() < 500:
                continue

            if label.name == 'staff':
                # merge any staffs that are intersecting
                for staff in self.staffs:
                    if staff.intersects(label):
                        staff.union(label)
                        break
                else:
                    self.staffs.append(label)
            
            # make noteheads a little larger for better modifier detection
            if 'notehead' in label.name:
                size_offset = (label.x_max() - label.x_min()) * 0.15 # extend by 15%
                label.bbox[0] -= size_offset
                label.bbox[2] += size_offset
            
            # offset accidentals right to overlap them into the note they are modifying
            if 'accidental' in label.name:
                size_offset = (label.x_max() - label.x_min()) * 0.5
                label.bbox[0] += size_offset
                label.bbox[2] += size_offset

        self.staffs.sort(key=Label.y_min)

        for staff in self.staffs:
            print(staff.bbox, staff.name)
    
    def _split_labels_by_staffs(self):
        cutoffs = [(a.y_max() + b.y_min()) / 2 for a, b in zip(self.staffs[:-1], self.staffs[1:])]
        cutoffs.append(math.inf)

        self.staff_labels = [[] for _ in self.staffs]

        for label in self.labels:
            # REMOVE: for testing only, TODO need to figure out a way to limit bad labels from sheet title
            if label.y_max() < 500:
                continue

            for staff_idx, y in enumerate(cutoffs):
                if label.y_min() < y:
                    self.staff_labels[staff_idx].append(label)
                    break
        
        print("split labels into staffs")
    
    def _process_labels(self):
        self.notes: list[list[Note]] = []

        for staff, staff_labels in zip(self.staffs, self.staff_labels):
            notes = self._process_staff(staff, staff_labels)
            self.notes.append(notes)
    
    def _process_staff(self, staff: Label, staff_labels: list[Label]) -> list[Note]:
        staff_labels.sort(key=Label.x_min)

        clef = Label(None, "clefF") # bass clef are hard to detect for some reason, default to base

        notes: list[Note] = []
        mods: list[Label] = []
        for label in staff_labels:
            if 'notehead' in label.name:
                notes.append(Note(label, clef, staff))
            elif 'rest' in label.name:
                notes.append(Note(label, clef, staff))
            elif 'clef' in label.name:
                clef = label
            else:
                mods.append(label)

        print(len(notes))

        global_mods = []

        mods_iterator = iter(mods)
        label = next(mods_iterator, None)
        while label != None:
            # pre note modifiers
            if label.x_max() > notes[0].label.x_min():
                break
            global_mods.append(label)

            label = next(mods_iterator, None)

        while label != None:
            # apply mod to notes that intersect with it
            for note in notes:
                if label.intersects(note.label):
                    note.modify(label)
            
            label = next(mods_iterator, None)
        
        return notes
    
    def _complete_notes(self):
        for notes in self.notes:
            start_time = 0
            for note in notes:
                note.complete()
                note.start_time = start_time
                start_time += note.duration
        
        self.notes = self.notes[4:]

        start_time = 0
        end_times = []
        all_notes = []
        for index, notes in enumerate(self.notes):
            print(notes)
            for note in notes:
                note.start_time += start_time
                all_notes.append(note)
            end_times.append(note.start_time)

            if index % 2 == 1:
                start_time = max(end_times)
                end_times = []

        self.notes = all_notes

    def __repr__(self) -> str:
        return "\n".join([str(notes) for notes in self.notes])


def main():
    import json

    with open(f"nggup2.json") as f:
        labels = json.load(f)
    
    labels = [Label(x['bbox'], x['name']) for x in labels]

    parser = MusicParser(labels)

    

    import player
    
    print(parser.notes)
    
    player.PianoPlayer().play(music.Music(parser.notes, 1))

if __name__ == "__main__":
    
    # import dataset
    # import matplotlib.pyplot as plt
    # data = dataset.MusicSheetDataSet("ds2_dense")
    # image, label = data[2]
    # plt.imshow(image)
    # plt.savefig("img.png", dpi=800)

    main()
