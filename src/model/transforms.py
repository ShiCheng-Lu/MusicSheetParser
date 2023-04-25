import random
from common.label import Label, Bbox

class Transform:
    def __init__(self, *args):
        self.transforms = args

    def __call__(self, image, labels: list[Label]):
        for transform in self.transforms:
            image, labels = transform(image, labels)
        return image, labels
    
    def assemble(self, image, labels: list[Label]):
        for transform in reversed(self.transforms):
            image, labels = transform.assemble(image, labels)
        return image, labels

class Crop(Transform):
    def __init__(self, region: Bbox, threshold):
        '''
        region: the region to crop
        threshold: what percentage of area is still in the image to keep the label
        '''
        self.region = region
        self.threshold = threshold

    def __call__(self, image, labels: list[Label]):
        # crop labels, discard any that are outside the area
        new_labels = []
        for label in labels:
            new = label.intersect(self.region).offset(self.region.x_min, self.region.y_min)
            new_area = new.area()

            if new_area == 0 or new_area < label.area() * self.threshold:
                continue

            new_labels.append(label)
        
        # crop image
        image = image[self.region[1] : self.region[3], self.region[0] : self.region[2]]

        return image, new_labels

class RandomCrop(Crop):
    def __init__(self, threshold):
        self.threshold = threshold

    def __call__(self, image, labels):
        height, width = image.shape

        x = random.randrange(0, width // 2)
        y = random.randrange(0, height // 2)
        self.region = [x, y, x + width // 2, y + height // 2]
        
        return super()(image, labels)

class Filter(Transform):
    def __init__(self, filter):
        '''filter out labels that match certain criteria'''
        self.filter = filter
    
    def __call__(self, image, labels: list[Label]):
        new_labels = []
        for label in labels:
            if self.filter(label):
                new_labels.append(label)
        return image, new_labels

class FilterByLabel(Filter):
    def __init__(self, labelList: list[Label]):
        '''filter by label name'''
        super().__init__(self.inFilteredList)
        self.filteredList = labelList

    def inFilteredList(self, label: Label):
        return label.label in self.filteredList
