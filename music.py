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

class Bbox:
    def __init__(self, box):
        self.box = box
    
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
            min(self.y_max(), other.y_max()),
        ]
        return Bbox(box)
    
    def intersects_with(self, other):
        return not (
            self.x_max() < other.x_min()
            or
            self.x_min() > other.x_max()
            or
            self.y_max() < other.y_min()
            or
            self.y_min() > other.y_max()
        )

    def union(self, other):
        box = [
            min(self.x_min(), other.x_min()),
            min(self.y_min(), other.y_min()),
            max(self.x_max(), other.x_max()),
            max(self.y_max(), other.y_max()),
        ]
        return Bbox(box)

class Label(Bbox):
    def __init__(self, name, box):
        super().__init__(box)
        self.name = name
    
    def __repr__(self):
        return f"{self.name}-{self.box}"

    def intersect(self, other):
        return Label(self.name, super().intersect(other).box)
    
    def union(self, other):
        return Label(self.name, super().union(other).box)
