import common.music

class Note(common.music.Note):
    def __init__(self, note: common.music.Note, parent_bar):
        note.copy(self)

class Bar(common.music.Bar):
    def __init__(self, bar: common.music.Bar):
        bar.copy(self)
        self.notes: list[Note] = [Note(note, self) for note in self.notes]

class Staff(common.music.Staff):
    def __init__(self, staff: common.music.Staff):
        staff.copy(self)
        self.bars: list[Bar] = [Bar(bar) for bar in self.bars]

class Music(common.music.Music):
    def __init__(self, music: common.music.Music):
        music.copy(self)
        self.staffs: list[Staff] = [Staff(staff) for staff in self.staffs]
    
    def play(self):