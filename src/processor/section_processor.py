from common.label import Bbox, Label
from common.music import Staff
from processor.bar_processor import BarProcessor

class SectionProcessor:

    def __init__(self, section: Bbox, staffs: list[Staff], labels: list[Label]):
        self.section = section
        self.bars: list[BarProcessor] = []

        # split the section into bars by staffs
        cutoff = self.section.y_min
        for a, b in zip(staffs[:-1], staffs[1:]):
            mid = (a.y_max + b.y_min) / 2
            bar = Label([self.section.x_min, cutoff, self.section.x_max, mid])

            self.bars.append(BarProcessor(bar, a, []))
            a.bars.append(BarProcessor(bar, a, []))
            cutoff = mid
        
        bar = Label([self.section.x_min, cutoff, self.section.x_max, self.section.y_max])
        self.bars.append(BarProcessor(bar, staffs[-1], []))
        staffs[-1].bars.append(bar)

        for bar in self.bars:
            for label in labels:
                if label.intersects(bar.section):
                    bar.labels.append(label)

    def process(self):
        for bar in self.bars:
            bar.process()

    @property
    def notes(self):
        notes = []
        for bar in self.bars:
            notes.extend(bar.notes)
        return notes
