from common.label import Bbox, Label
from common.music import Staff
from processor.bar_processor import BarProcessor

from model.model import MusicSymbolDetector
import json
import matplotlib.pyplot as plt
import torch
from torchvision.utils import draw_bounding_boxes

with open(f"category.json") as f:
    categories = json.load(f)
detector = MusicSymbolDetector()
detector.load("saved_models_bars/10")

class SectionProcessor:
    def __init__(self, section: Bbox, staffs: list[Staff], parent):
        self.section = section
        self.bars: list[BarProcessor] = []
        self.parent = parent

        # split the section into bars by staffs
        cutoff = self.section.y_min
        for a, b in zip(staffs[:-1], staffs[1:]):
            mid = (a.y_max + b.y_min) / 2
            bar = Label([self.section.x_min, cutoff, self.section.x_max, mid], "bar")

            bar_processor = BarProcessor(bar, a)
            self.bars.append(bar_processor)
            a.bars.append(bar_processor)
            cutoff = mid
        
        bar = Label([self.section.x_min, cutoff, self.section.x_max, self.section.y_max], "bar")

        bar_processor = BarProcessor(bar, staffs[-1])
        self.bars.append(bar_processor)
        staffs[-1].bars.append(bar_processor)

    def process(self):
        section = self.parent.image[self.section.y_min:self.section.y_max, self.section.x_min:self.section.x_max]
        # object detect
        labels = detector(section)
        for label in labels:
            label.name = categories[str(label.name)]["name"]

        # boxes = [label.bbox for label in labels]
        # plt.imshow(draw_bounding_boxes(
        #     torch.tensor(section).unsqueeze(0), 
        #     torch.tensor(boxes), 
        #     [label.name for label in labels]).moveaxis(0, 2))
        # plt.show()
    
        # for label in labels:

            # weird beams
            if label.name == "beam" and label.height >= self.section.height / 3:
                continue

            label.move(self.section.x_min, self.section.y_min)

            for bar in self.bars:
                if bar.intersects(label):
                    bar.labels.append(label)

        for bar in self.bars:
            bar.process()

    @property
    def notes(self):
        notes = []
        for bar in self.bars:
            notes.extend(bar.notes)
        return notes
