class Note:
    def __init__(self, pitch=None, duration=0, start_time=0):
        self.pitch: int = pitch
        self.duration: int = duration
        self.start_time: int = start_time

class Music:
    def __init__(self, notes, bpm):
        self.bpm: int = bpm
        self.notes: list[Note] = notes
        self.compiled = False
