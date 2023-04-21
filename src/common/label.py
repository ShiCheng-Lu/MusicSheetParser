class Bbox:
    def __init__(self, bbox=None):
        self.bbox: list[float] = bbox
    
    @property
    def bbox(self):
        return [self.x_min, self.y_min, self.x_max, self.y_max]

    @bbox.setter
    def bbox(self, v):
        if v == None:
            v = [None, None, None, None]
        self.x_min, self.y_min, self.x_max, self.y_max = v
    
    @property
    def width(self):
        return self.x_max - self.x_min
    
    @property
    def height(self):
        return self.y_max - self.y_min
    
    def intersects(self, other) -> bool:
        return (self.x_max >= other.x_min and
                self.x_min <= other.x_max and
                self.y_max >= other.y_min and
                self.y_min <= other.y_max)
    
    def intersection(self, other, result=None):
        if result == None:
            result = self
        
        result.bbox = [
            max(self.x_min, other.x_min),
            max(self.y_min, other.y_min),
            min(self.x_max, other.x_max),
            min(self.y_max, other.y_max),
        ]
        return result


    def union(self, other, result=None):
        if result == None:
            result = self

        result.bbox = [
            min(self.x_min, other.x_min),
            min(self.y_min, other.y_min),
            max(self.x_max, other.x_max),
            max(self.y_max, other.y_max),
        ]
        return result
    
    def move(self, x, y, result=None):
        if result == None:
            result = self
        
        result.bbox = [
            self.x_min + x,
            self.y_min + y,
            self.x_max + x,
            self.y_max + y,
        ]
        return result
    
    def valid(self):
        return self.x_max >= self.x_min and self.y_max >= self.y_min
    
    def copy(self, other=None):
        if other == None:
            other = Bbox()
        other.bbox = self.bbox
        return other
    
    def area(self):
        return (self.x_max - self.x_min) * (self.y_max - self.y_min)
    
    def to_dict(self):
        return self.bbox
    
    def from_dict(self, data):
        self.bbox = data
        return self

class Label(Bbox):
    def __init__(self, bbox=None, name=None):
        super().__init__(bbox)
        self.name: str = name
    
    def copy(self, other=None):
        if other == None:
            other = Label()
        super().copy(other)
        other.name = self.name
        return other
    
    def __repr__(self):
        return f"{self.name}"
    
    def to_dict(self):
        return {
            "bbox": super().to_dict(),
            "name": self.name
        }
    
    def from_dict(self, data):
        super().from_dict(data["bbox"])
        self.name = data["name"]
        return self