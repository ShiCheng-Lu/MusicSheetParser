from torchvision import datasets, utils
import json
import cv2
import os
import torch
import matplotlib.pyplot as plt
import processor.staff_utils
from common.label import Bbox
import random
import multiprocessing

def crop(image, target, region: Bbox, dataset):
    boxes = []
    labels = []
    for annotation in target:
        # print(annotation)
        orig_box = Bbox(annotation['a_bbox'])
        new_box = orig_box.intersection(region)

        if not new_box.valid() or new_box.area() <= 0:
            continue

        new_box.move(-region.x_min, -region.y_min)

        for cat_id in annotation['cat_id']:
            if (cat_id == None):
                continue

            category = dataset.get_category(cat_id)
            if (category['annotation_set'] != 'deepscores'):
                continue

            if (category['name'] in {'stem', 'ledgerLine', 'staff'}):
                break
            # if (category['name'] in oneset):
            labels.append(int(cat_id))
            boxes.append(new_box.bbox)
    
    return (
        torch.tensor(image[region.y_min:region.y_max, region.x_min:region.x_max]).div(255).unsqueeze(0),
        {
            'boxes': torch.tensor(boxes),
            'labels': torch.tensor(labels),
        }
    )

def section(data):
    path = data['filename']
    image = cv2.imread(os.path.join("../ds2_dense", 'images', path), cv2.IMREAD_GRAYSCALE)
    sections = []
    try:
        for section in processor.staff_utils.section(image):
            section.name = data
            sections.append(section)
    except:
        pass
        # print(f"Failed to process {data['filename']}")
    return sections

class MusicSheetDataSet(datasets.VisionDataset):
    def __init__(self, root=None, split='train', transform=None):
        super().__init__(root)
        if root == None:
            return
        
        self.split = split # train, test
        self.transform = transform

        with open(f"{root}/deepscores_{split}.json") as f:
            self.data = json.load(f)

        self.sections = []

        with multiprocessing.Pool(12) as p:
            result = p.map(section, self.data['images'])
        
        for labels in result:
            self.sections.extend(labels)

        self.sampling_sections = self.sections


    def section(self, data):
        sections = []
        image = self._load_image(data)
        try:
            for section in processor.staff_utils.section(image):
                section.name = data
                sections.append(section)
        except:
            pass
            # print(f"Failed to process {data['filename']}")
        return sections

    def n_classes(self):
        return sum(cat['annotation_set'] == 'deepscores' for cat in self.data['categories'].values())

    def _load_image(self, image):
        path = image['filename']
        return cv2.imread(os.path.join(self.root, 'images', path), cv2.IMREAD_GRAYSCALE)

    def _load_target(self, image):
        anno_ids = image['ann_ids']
        return [self.data['annotations'][id] for id in anno_ids]

    def __getitem__(self, index):
        image = self._load_image(self.sampling_sections[index].name)
        target = self._load_target(self.sampling_sections[index].name)

        return crop(image, target, self.sections[index], self)

    def showLabels(self, index):
        image, targets = self[index]

        plt.imshow(utils.draw_bounding_boxes(
            image.mul(255).type(torch.uint8), targets['boxes'], width=4
        ).moveaxis(0, 2))

    def __len__(self):
        return len(self.sampling_sections)
    
    def get_category(self, cat_id):
        return self.data['categories'][str(cat_id)]
    
    def random(self, count):
        self.sampling_sections = random.sample(self.sections, count)
        return self
