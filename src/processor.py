from music import Note
import math
from common import Label

class MusicParser:
    def __init__(self, labels: list[Label]):
        self.labels = labels
        
        self._pre_process()
        self._split_labels_by_staffs()
        self._process_labels()
        self._complete_notes()

    def _pre_process(self):
        self.staffs: list[Label] = []

        tempo_note = Label([math.inf, math.inf, math.inf, math.inf])
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
                size_offset = (label.x_max() - label.x_min()) * 0.1 # extend by 10%
                label.bbox[0] -= size_offset
                label.bbox[2] += size_offset

                if label.bbox[0] + label.bbox[1] < tempo_note.bbox[0] + tempo_note.bbox[1]:
                    tempo_note = label
            
            # offset accidentals right to overlap them into the note they are modifying
            if 'accidental' in label.name:
                size_offset = (label.x_max() - label.x_min())
                label.bbox[0] += size_offset
                label.bbox[2] += size_offset
        
        self.labels.remove(tempo_note)

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
                # pre process some mods
                area_mods = ['flag', 'beam', 'slur', 'tie']
                if any(mod_name in label.name for mod_name in area_mods):
                    label.bbox[1] = 0
                    label.bbox[3] = math.inf

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
            last_note_time = 0

            note_group_counter = 0
            # group notes
            notes = iter(notes)
            group_end = 0
            while (note := next(notes, None)):
                if note.label.x_min() > group_end:
                    start_time += last_note_time
                    note_group_counter += 1
                
                group_end = note.label.x_max()

                note.complete()
                note.start_time = start_time
                
                group_end = note.label.x_max()
                last_note_time = note.duration
            
            print(note_group_counter, start_time + last_note_time)

        # group by brace

        start_time = 0
        end_times = []
        all_notes = []
        for index, notes in enumerate(self.notes):
            for note in notes:
                note.start_time += start_time
                all_notes.append(note)
            end_times.append(note.start_time + note.duration)

            if index % 2 == 1:
                start_time = max(end_times)
                end_times = []

        self.notes = all_notes

    def __repr__(self) -> str:
        return "\n".join([str(notes) for notes in self.notes])

if __name__ == "__main__":
    import json

    with open(f"nggup2.json") as f:
        labels = json.load(f)
    
    labels = [Label(x['bbox'], x['name']) for x in labels]

    parser = MusicParser(labels)

    import player
    import music
    
    player.PianoPlayer().play(music.Music(parser.notes, 0.5))
    # import dataset
    # import matplotlib.pyplot as plt
    # data = dataset.MusicSheetDataSet("ds2_dense")
    # image, label = data[2]
    # plt.imshow(image)
    # plt.savefig("img.png", dpi=800)

