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

        offset = self.staff_offsets[rel_position % 7]
        # apply any flat/sharp modifiers
        for modifier in self.modifiers:
            mod_y = (modifier.y_max() + modifier.y_min()) / 2
            if 'Flat' in modifier.name:
                mod_y = (mod_y + modifier.y_max()) / 2
            if mod_y < notehead.y_min() or mod_y > notehead.y_max() or modifier.x_min() > notehead.x_min():
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

    def _get_pitches(self):
        self.staff_center = (self.staff.y_min() + self.staff.y_max()) / 2
        self.offset_size = (self.staff.y_max() - self.staff.y_min()) / 8

        for note in self.notes:
            if 'rest' in note.name:

                break

            semitone = self._get_semitone(note)
            self.pitches.append(semitone)

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

        augmentation = sum(mod.name == "augmentationdot" for mod in self.modifiers)
        self.duration = int(self.duration * (2 - (1 / 2) ** augmentation) * 64)

    def __init__(self, staff: Label, clef: Label):
        self.staff = staff
        self.clef = clef
        self.notes: list[Label] = []

        self.modifiers: list[Label] = []
        self.pitches = []
    
    def addNote(self, note: Label):
        self.notes.append(note)
        return self

    def modify(self, labels):
        if type(labels) is Label:
            labels = [labels]

        self.modifiers.extend(labels)

        return self
    
    def complete(self):
        self.pitches: list[int] = []
        # process order is important
        self._get_pitches()
        self._get_duration()

        return self

    def __repr__(self):
        return f"{self.pitches} {self.duration}"

class MusicParser:
    def __init__(self, labels: list[Label]):
        self.labels = labels
        
        self._pre_process()
        self._split_labels_by_staffs()
        self._process_labels()

    def _pre_process(self):
        self.staffs: list[Label] = []
        for label in self.labels:
            if label.name == 'staff':
                self.staffs.append(label)
            
            # make noteheads a little larger for better modifier detection
            if 'notehead' in label.name:
                size_offset = (label.x_max() - label.x_min()) * 0.15 # extend by 15%
                label.box[0] -= size_offset
                label.box[2] += size_offset
            
            if 'accidental' in label.name:
                size_offset = (label.x_max() - label.x_min()) * 0.5
                label.box[0] += size_offset
                label.box[2] += size_offset

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

        keys = [0] * 7

        notes = []

        while max_item != None:
            if (min_item != None and min_item.x_min() < max_item.x_max()):
                if 'notehead' in min_item.name:
                    if note == None:
                        note = Note(staff, clef)
                    note.addNote(min_item)
                    note.staff_offsets = keys
                    for mod in modifiers:
                        note.modify(mod)
                elif 'rest' in min_item.name:
                    notes.append(Note(staff, clef).addNote(min_item).complete())
                elif 'clef' in min_item.name:
                    clef = min_item
                elif 'key' in min_item.name:
                    mod_y = (min_item.y_max() + min_item.y_min()) / 2
                    if 'Flat' in min_item.name:
                        mod_y = (mod_y + min_item.y_max()) / 2
                    
                    staff_center = (staff.y_min() + staff.y_max()) / 2
                    offset_size = (staff.y_max() - staff.y_min()) / 8

                    rel_position = np.round((staff_center - mod_y) / offset_size)

                    match clef.name:
                        case 'clefG': # treble clef
                            rel_position += 8
                        case 'clefCAlto':
                            rel_position += 2
                        case 'clefCTenor':
                            rel_position += 0
                        case 'clefF': # base clef
                            rel_position -= 4
                    
                    keys[int(rel_position % 7)] = -1 if 'Flat' in min_item.name else +1

                elif note != None:
                    modifiers.add(min_item)
                    note.modify(min_item)
                else:
                    modifiers.add(min_item)
                
                min_item = next(min_sorted, None)
            else:
                if 'notehead' in max_item.name and note != None:
                    note.complete()
                    notes.append(note)
                    note = None
                elif 'key' in max_item.name:
                    pass
                elif max_item in modifiers:
                    modifiers.remove(max_item)
                
                max_item = next(max_sorted, None)
        
        return notes

    def __repr__(self) -> str:
        return "\n".join([str(notes) for notes in self.notes])


def main():
    import dataset
    import matplotlib.pyplot as plt

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

    import player
    
    m = music.Music()
    m.time = 32

    m.tracks = [[], [], [], []]
    
    for i in range(12):
        m.tracks[i % 4].extend(parser.notes[i])

    # for i in parser.notes:
    #     print([x.pitches for x in i])
    #     print(sum([x.duration for x in i]))
    
    player.PianoPlayer().play(m)

if __name__ == "__main__":
    main()
