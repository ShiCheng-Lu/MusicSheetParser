class Bbox:
    def __init__(self, x_min, y_min, x_max, y_max):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    def __init__(self, box):
        self.__init__(box[0], box[1], box[2], box[3])
    
    def __repr__(self) -> str:
        return f"{self.x_min} {self.y_min} {self.x_max} {self.y_max}"

    def area(self):
        return (self.x_max - self.x_min) * (self.y_max - self.y_min)

    def intersects_with(self, other):
        return not (
            self.x_max < other.x_min or
            self.x_min > other.x_max or
            self.y_max < other.y_min or
            self.y_min > other.y_max)

    def intersect(self, other, dest=None):
        dest = dest or self
        dest.x_min = max(self.x_min, other.x_min)
        dest.y_min = max(self.y_min, other.y_min)
        dest.x_max = min(self.x_max, other.x_max)
        dest.y_max = min(self.y_max, other.y_max)
        return dest

    def union(self, other, dest=None):
        dest = dest or self
        dest.x_min = min(self.x_min, other.x_min)
        dest.y_min = min(self.y_min, other.y_min)
        dest.x_max = max(self.x_max, other.x_max)
        dest.y_max = max(self.y_max, other.y_max)
        return dest
    
    def offset(self, x_offset, y_offset, dest=None):
        dest = dest or self
        dest.x_min = self.x_min - x_offset
        dest.y_min = self.y_min - y_offset
        dest.x_max = self.x_max - x_offset
        dest.y_max = self.y_max - y_offset
        return dest


class Label(Bbox):
    def __init__(self, label, box=None):
        if box != None:
            super().__init__(box)
        self.label = label

    def __repr__(self) -> str:
        return f"{self.label}-{super().__repr__()}"

    def intersect(self, other):
        return super().intersect(other, Label(self.label))

    def union(self, other):
        return super().union(other, Label(self.label))
