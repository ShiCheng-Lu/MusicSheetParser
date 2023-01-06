class Note:
    def __init__(self, pitches = None, duration = None):
        self.pitches: list[int] = pitches
        self.duration: int = duration
    
    def add_pitch(self, pitch):
        pass

class Music:
    def __init__(self):
        self.time: int
        self.tracks: list[list[Note]]