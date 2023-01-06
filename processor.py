import numpy as np
import re
import music

class Label:
    def __init__(self, name, box):
        self.name = name
        self.box = box
    
    def __repr__(self):
        return f"{self.name}"

    def x_min(self):
        return self.box[0]
    
    def x_max(self):
        return self.box[2]
    
    def y_min(self):
        return self.box[1]
    
    def y_max(self):
        return self.box[3]

    def area(self):
        return (self.x_max() - self.x_min()) * (self.y_max() - self.y_min())

    def intersect(self, other):
        box = [
            max(self.x_min(), other.x_min()),
            max(self.y_min(), other.y_min()),
            min(self.x_max(), other.x_max()),
            min(self.x_max(), other.x_max()),
        ]
        return Label(self.name, box)

    def union(self, other):
        box = [
            min(self.x_min(), other.x_min()),
            min(self.y_min(), other.y_min()),
            max(self.x_max(), other.x_max()),
            max(self.x_max(), other.x_max()),
        ]
        return Label(self.name, box)

pitchMap = [
"A0",
"Bb0",
"B0",
"C1",
"Db1",
"D1",
"Eb1",
"E1",
"F1",
"Gb1",
"G1",
"Ab1",
"A1",
"Bb1",
"B1",
"C2",
"Db2",
"D2",
"Eb2",
"E2",
"F2",
"Gb2",
"G2",
"A2",
"Ab2",
"Bb2",
"B2",
"C3",
"Db3",
"D3",
"Eb3",
"E3",
"F3",
"Gb3",
"G3",
"Ab3",
"A3", #36
"Bb3",
"B3",
"C4",
"Db4",
"D4",
"Eb4",
"E4",
"F4",
"Gb4",
"G4",
"Ab4",
"A4",
"Bb4",
"B4",
"C5",
"Db5",
"D5",
"Eb5",
"E5",
"F5",
"Gb5",
"G5",
"Ab5",
"A5",
"Bb5",
"B5",
"C6",
"Db6",
"D6",
"Eb6",
"E6",
"F6",
"Gb6",
"G6",
"Ab6",
"A6",
"Bb6",
"B6",
"C7",
"Db7",
"D7",
"Eb7",
"E7",
"F7",
"Gb7",
"G7",
"Ab7",
"A7",
"Bb7",
"B7",
]

class Note(music.Note):
    def _rel_position(self):
        if 'rest' in self.notes[0].name:
            return
        staff_center = (self.staff.y_min() + self.staff.y_max()) / 2
        offset_size = (self.staff.y_max() - self.staff.y_min()) / 8

        for note in self.notes:
            note_center = (note.y_min() + note.y_max()) / 2
            inspace = 'InSpace' in note.name

            # use whether note in inspace to more accurately determine relative position
            if inspace == True:
                rel_position = np.round((staff_center - note_center - offset_size) / (offset_size * 2)) * 2 + 1
            else:
                rel_position =  np.round((staff_center - note_center) / (offset_size * 2)) * 2
            
            self.rel_positions.append(int(rel_position))

    def _get_semitone(self):
        # offset rel_position to number of lines from A3 (tuned at 440Hz)
        for rel_position in self.rel_positions:
            match self.clef.name:
                case 'clefG': # treble clef
                    rel_position += 8
                case 'clefCAlto':
                    rel_position += 2
                case 'clefCTenor':
                    rel_position += 0
                case 'clefF': # base clef
                    rel_position -= 4
            
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

            # apply any flat/sharp modifiers
            for modifier in self.modifiers:
                pass
            
            self.semitones.append(semitones)

    def _get_duration(self):
        note = self.notes[0]

        if 'DoubleWhole' in note.name:
            self.duration = 2
        elif 'Whole' in note.name:
            self.duration = 1
        elif 'Half' in note.name:
            self.duration = 0.5
        elif 'Quarter' in note.name:
            self.duration = 0.25
        elif flag := next((mod for mod in self.modifiers if 'flag' in mod.name), note if 'rest' in note.name else None): 
            # noteheadBlack, duration determined by flag
            num = re.search(r'\d+', flag.name).group()
            self.duration = 1 / int(num)
        else: 
            # noteheadBlack, duration determined by beam(s)
            beam_count = sum('beam' == mod.name for mod in self.modifiers)
            self.duration = 1 / (2 ** (beam_count + 2))    

    def __init__(self, staff: Label, clef: Label):
        self.staff = staff
        self.clef = clef
        self.notes: list[Label] = []

        self.modifiers: list[Label] = []
    
    def addNote(self, note: Label):
        self.notes.append(note)
        return self

    def modify(self, labels):
        if type(labels) is Label:
            labels = [labels]

        self.modifiers.extend(labels)

        return self
    
    def complete(self):
        self.rel_positions: list[int] = []
        self.semitones: list[int] = []
        # process order is important
        self._rel_position()
        self._get_semitone()
        self._get_duration()

        self.pitches = [pitchMap[semitones + 36] for semitones in self.semitones]
        self.duration = int(self.duration * 2000)

        return self

    def __repr__(self):
        return f"{self.rel_positions} {self.semitones} {self.pitches} {self.duration}"

class MusicParser:
    def __init__(self, labels: list[Label]):
        self.labels = labels
        
        self._pre_process_labels()
        self._get_staffs()
        self._split_labels_by_staffs()
        self._process_labels()

    def _pre_process_labels(self):
        # make noteheads a little larger for better modifier detection
        for label in self.labels:
            if 'notehead' in label.name:
                size_offset = (label.x_max() - label.x_min()) * 0.10 # extend by 10%
                label.box[0] -= size_offset
                label.box[2] += size_offset
        pass

    def _get_staffs(self):
        self.staffs: list[Label] = []
        for label in self.labels:
            if label.name == 'staff':
                self.staffs.append(label)
        
        self.staffs.sort(key=Label.y_min)
    
    def _split_labels_by_staffs(self):
        cutoffs = list(map(lambda a, b : (a.y_max() + b.y_min()) / 2, self.staffs[:-1], self.staffs[1:]))

        self.staff_labels = [[] for _ in self.staffs]

        for label in self.labels:
            for staff_idx, y in enumerate(cutoffs):
                if label.y_min() < y:
                    self.staff_labels[staff_idx].append(label)
                    break
            else: # last section of staff
                self.staff_labels[-1].append(label)
    
    def _process_labels(self):
        self.notes: list[list[Note]] = []

        for staff, staff_labels in zip(self.staffs, self.staff_labels):
            notes = self._process_staff(staff, staff_labels)
            self.notes.append(notes)
    
    def _process_staff(self, staff: Label, staff_labels: list[Label]) -> list[Note]:
        min_sorted = iter(sorted(staff_labels, key=Label.x_min)) # sort by x_min
        max_sorted = iter(sorted(staff_labels, key=Label.x_max)) # sort by x_max

        min_item = next(min_sorted, None)
        max_item = next(max_sorted, None)

        modifiers = set()
        note = None
        clef = None

        notes = []

        while max_item != None:
            if (min_item != None and min_item.x_min() < max_item.x_max()):
                if 'notehead' in min_item.name:
                    if note == None:
                        note = Note(staff, clef)
                    note.addNote(min_item)
                    for mod in modifiers:
                        note.modify(mod)
                elif 'rest' in min_item.name:
                    notes.append(Note(staff, clef).addNote(min_item).complete())
                elif 'clef' in min_item.name:
                    clef = min_item
                elif note != None:
                    modifiers.add(min_item)
                    note.modify(min_item)
                
                min_item = next(min_sorted, None)
            else:
                if 'notehead' in max_item.name and note != None:
                    note.complete()
                    notes.append(note)
                    note = None
                elif max_item in modifiers:
                    modifiers.remove(max_item)
                
                max_item = next(max_sorted, None)
        
        return notes

    def __repr__(self) -> str:
        return "\n".join([str(notes) for notes in self.notes])


def main():
    import dataset
    import matplotlib.pyplot as plt
    import threading

    data = dataset.MusicSheetDataSet("ds2_dense")

    def toLabelList(list):
        labels = []
        for item in list:
            labels.append(Label(
                data.get_category(item['cat_id'][0])['name'],
                item['a_bbox']
            ))
        return labels

    image, labels = data[2]
    parser = MusicParser(toLabelList(labels))

    plt.imshow(image)
    plt.savefig("img.png", dpi=800)

    # print("playing music")

    import player
    import time
    
    m = music.Music()



    m.tracks = [[], [], [], []]
    
    for i in range(12):
        m.tracks[i % 4].extend(parser.notes[i])
    player.PianoPlayer().play(m)

if __name__ == "__main__":
    main()
