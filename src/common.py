class Label:
    def __init__(self, bbox=None, name=None):
        self.bbox: list[float] = bbox
        self.name: str = name
    
    @property
    def bbox(self):
        return [self.x_min, self.y_min, self.x_max, self.y_max]

    @bbox.setter
    def bbox(self, v):
        if v == None: return
        self.x_min, self.y_min, self.x_max, self.y_max = v
    
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
    
    def copy(self, other=None):
        if other == None:
            other = Label(None, None, None)
        other.bbox = self.bbox.copy()
    
    def area(self):
        return (self.x_max - self.x_min) * (self.y_max - self.y_min)
    
    def __repr__(self):
        return f"{self.name}"
