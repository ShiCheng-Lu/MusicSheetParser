'''
Music data structure

{
    "name": <string>
    "staffs": [
        {
            "bbox": <int[4]>,
            "name": "staff",
            "keys": <int[7]>,
            "clef": {
                "bbox": <int[4]>,
                "name": <string>
            }
            "bars": [
                {
                    "bbox": <int[4]>,
                    "name": "bar",
                    "notes": [
                        {
                            "bbox": <int[4]>,
                            "name": <string>,
                            "pitch": <int>,
                            "modifier": <int>,
                            "duration": <float>
                        },
                        ...
                    ]
                },
                ...
            ]
        },
        ...
    ]
    "group": <int>
}

'''


from common.label import Label

SEMITONE_MAP = [ # range: -48 to +39 relative to A4
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

class Note(Label):
    def __init__(self, bbox=None, name=None):
        super().__init__(bbox, name)
        self.duration: float = 0
        self.pitch: int = 0
        self.start: float = 0
        self.modifier: int = 0 # +1/-1 for sharp or flat
        self.parent_bar: Bar = None # Bar
    
    @property
    def semitone(self):
        semitone = self.pitch // 7 * 12
        match self.pitch % 7:
            case 0: semitone += 0
            case 1: semitone += 2
            case 2: semitone += 3
            case 3: semitone += 5
            case 4: semitone += 7
            case 5: semitone += 8
            case 6: semitone += 10
        if self.modifier != None:
            return semitone + self.modifier
        else:
            return semitone + self.parent_bar.parent_staff.keys[self.pitch % 7]
    
    @property
    def pitch_str(self):
        return 'rest' if 'rest' in self.name else SEMITONE_MAP[self.semitone]
    
    def copy(self, other=None):
        if other == None:
            other = Note()
        super().copy(other)
        other.parent_bar = self.parent_bar
        other.duration = self.duration
        other.pitch = self.pitch
        other.start = self.start
        other.modifier = self.modifier
        return other
    
    def to_dict(self):
        return super().to_dict() | {
            "pitch": self.pitch,
            "duration": self.duration,
            "modifier": self.modifier
        }
    
    def from_dict(self, data, parent_bar=None):
        super().from_dict(data)
        self.duration = data["duration"]
        self.pitch = data["pitch"]
        self.modifier = data["modifier"]
        self.parent_bar = parent_bar
        return self


class Bar(Label):
    def __init__(self, bbox=None, name=None):
        super().__init__(bbox, name)
        self.parent_staff: Staff = None
        self.notes: list[Note] = []
    
    def copy(self, other=None):
        if other == None:
            other = Bar()
        super().copy(other)
        other.parent_staff = self.parent_staff
        other.notes = [note.copy() for note in self.notes]
        return other

    def to_dict(self):
        return super().to_dict() | {
            "notes": [note.to_dict() for note in self.notes],
        }
    
    def from_dict(self, data, parent_staff=None):
        super().from_dict(data)
        self.notes = [Note().from_dict(note, self) for note in data['notes']]
        self.parent_staff = parent_staff
        return self

class Staff(Label):
    def __init__(self, bbox=None, name=None):
        super().__init__(bbox, name)
        self.keys: list[int] = [0 for _ in range(7)]
        self.clef: Label = None
        self.bars: list[Bar] = []
        self.parent_music: Music = None
    
    def copy(self, other=None):
        if other == None:
            other = Staff()
        super().copy(other)
        other.keys = self.keys.copy()
        other.clef = self.clef.copy()
        other.bars = [bar.copy() for bar in self.bars]
        return other
    
    def to_dict(self):
        return super().to_dict() | {
            "keys": self.keys,
            "clef": self.clef.to_dict(),
            "bars": [bar.to_dict() for bar in self.bars],
        }
    
    def from_dict(self, data, parent_music):
        super().from_dict(data)
        self.keys = data["keys"]
        self.clef = Label().from_dict(data["clef"])
        self.bars = [Bar().from_dict(bar, self) for bar in data["bars"]]
        self.parent_music = parent_music
        return self

class Music:
    def __init__(self):
        self.staffs: list[Staff] = []
        self.group: int = None
        self.bpm: int = 80
        self.time_sig: list[int] = [4, 4]
    
    @property
    def time_sig_duration(self):
        return self.time_sig[0] / self.time_sig[1]
    
    def copy(self, other=None):
        if other == None:
            other = Music()
        other.staffs = [staff.copy() for staff in self.staffs]
        other.group = self.group
        other.bpm = self.bpm
        other.time_sig = self.time_sig
    
    def to_dict(self):
        return {
            "staffs": [staff.to_dict() for staff in self.staffs],
            "group": self.group,
            "bpm": self.bpm,
        }
    
    def from_dict(self, data):
        self.staffs = [Staff().from_dict(data, self) for data in data["staffs"]]
        self.group = data["group"]
        self.bpm = data["bpm"]
        return self

def display_duration(duration: float):
    '''
    displayed duration 1/2, 3/4 etc.
    '''
    if duration == int(duration):
        return f"{duration}"
    
    denom = 2
    while True:
        numerator = duration * denom
        if numerator == int(numerator):
            return f"{int(numerator)}/{denom}"
        denom += 1
