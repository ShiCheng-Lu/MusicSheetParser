from note_processor import Note
import math
from common import Label
import staff_utils
import operator

'''
Parser:
1. object detection with model
2. split by staff and bar
3. re-detect bars that are 'invalid' (optionally re-detect every bar)
4. output to manual editor
'''


class MusicParser:
    def __init__(self, labels: list[Label], name=None, process_all=True):
        self.labels = labels
        self.name = name

        if process_all:
            self.process_all()
    
    def process_all(self):
        self.pre_process()
        self.split_labels_by_staffs()
        self.process_labels()
        self.complete_notes()

    def pre_process(self):
        '''
        preprocess labels
        '''
        self.staffs: list[Label] = []

        tempo_note = Label([math.inf, math.inf, math.inf, math.inf])
        for label in self.labels:
            if 'notehead' in label.name:

                if label.x_min + label.y_min < tempo_note.x_min + tempo_note.y_min:
                    tempo_note = label
            
        
        self.labels.remove(tempo_note)
    
    def split_labels_by_staffs(self):
        '''
        split labels into the staffs they are in
        '''
        self.staffs = staff_utils.get_staff(self.name)

        cutoffs = [(a.y_max + b.y_min) / 2 for a, b in zip(self.staffs[:-1], self.staffs[1:])]
        cutoffs.append(math.inf)

        self.staff_labels = [[] for _ in self.staffs]

        for label in self.labels:
            # REMOVE: for testing only, TODO need to figure out a way to limit bad labels from sheet title
            if label.y_max < 500:
                continue

            for staff_idx, y in enumerate(cutoffs):
                if label.y_min < y:
                    self.staff_labels[staff_idx].append(label)
                    break
        
        print("split labels into staffs")
    
    def process_labels(self):
        self.notes: list[list[Note]] = []

        for staff, staff_labels in zip(self.staffs, self.staff_labels):
            notes = self.process_staff(staff, staff_labels)
            self.notes.append(notes)
    
    def process_staff(self, staff: Label, staff_labels: list[Label]) -> list[Note]:
        staff_labels.sort(key=operator.attrgetter("x_min"))

        clef = Label(None, "clefF") # bass clef are hard to detect for some reason, default to base

        notes: list[Note] = []
        mods: list[Label] = []
        for label in staff_labels:
            if 'notehead' in label.name:
                # make noteheads a little larger for better modifier detection
                size_offset = (label.x_max - label.x_min) * 0.05 # extend by 5%
                label.x_min -= size_offset
                label.x_max += size_offset
                notes.append(Note(label, clef, staff))
            elif 'rest' in label.name:
                notes.append(Note(label, clef, staff))
            elif 'clef' in label.name:
                clef = label
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

        print(len(notes))

        global_mods = []

        mods_iterator = iter(mods)
        label = next(mods_iterator, None)
        while label != None:
            # pre note modifiers
            if label.x_max > notes[0].label.x_min:
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
    
    def complete_notes(self):
        for notes in self.notes:
            start_time = 0
            last_note_time = 0

            note_group_counter = 0
            # group notes
            notes = iter(notes)
            group_end = 0
            while (note := next(notes, None)):
                if note.label.x_min > group_end:
                    start_time += last_note_time
                    note_group_counter += 1
                
                group_end = note.label.x_max

                note.complete()
                note.start_time = start_time
                
                group_end = note.label.x_max
                last_note_time = note.duration
            
            print(note_group_counter, start_time + last_note_time)

        # group by brace

        start_time = 0
        end_times = []
        all_notes = []
        for index, notes in enumerate(self.notes):
            print(notes)
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

    parser = MusicParser(labels, "sheets/genshin main theme.png")

    import player
    import music

    import matplotlib.pyplot as plt
    import torch
    import cv2
    from torchvision.utils import draw_bounding_boxes

    img = cv2.imread("sheets/genshin main theme.png", cv2.IMREAD_GRAYSCALE)
    boxes = [note.label.bbox for note in parser.notes]
    labels = [note.label.name if note.pitch == None else music.PITCH_MAP[note.pitch] for note in parser.notes]

    plt.imshow(draw_bounding_boxes(torch.tensor(img).unsqueeze(0), torch.tensor(boxes), labels, font_size=30).moveaxis(0, 2))

    plt.savefig("staffs.png", dpi=800)

    # save notes as Labels
    durations = [note.duration for note in parser.notes]
    list_res = []
    for bbox, label, duration in zip(boxes, labels, durations):
        list_res.append({
            "bbox": bbox,
            "name": label,
            "duration": duration,
        })

    import json
    with open("notes.json", 'w') as f:
        f.write(json.dumps(list_res))

    # player.PianoPlayer().play(music.Music(parser.notes, 80))
    # import dataset
    # import matplotlib.pyplot as plt
    # data = dataset.MusicSheetDataSet("ds2_dense")
    # image, label = data[2]
    # plt.imshow(image)
    # plt.savefig("img.png", dpi=800)

