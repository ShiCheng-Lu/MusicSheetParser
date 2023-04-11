from torchvision import datasets, utils
import json
import cv2
import os
import torch
import matplotlib.pyplot as plt

class MusicSheetDataSet(datasets.VisionDataset):
    def __init__(self, root=None, split='train', transform=None):
        super().__init__(root)
        if root == None:
            return
        
        self.split = split # train, test
        self.transform = transform

        with open(f"ds2_dense/deepscores_{split}.json") as f:
            self.data = json.load(f)

        self.ids = [image['id'] for image in self.data['images']]

    def n_classes(self):
        return sum(cat['annotation_set'] == 'deepscores' for cat in self.data['categories'].values())

    def _load_image(self, image):
        path = image['filename']
        return cv2.imread(os.path.join(self.root, 'images', path), cv2.IMREAD_GRAYSCALE)

    def _load_target(self, image):
        anno_ids = image['ann_ids']
        return [self.data['annotations'][id] for id in anno_ids]

    def __getitem__(self, index):
        data = self.data['images'][index]

        image = self._load_image(data)
        target = self._load_target(data)

        if self.transform:
            return self.transform(image, target)
        return image, target

    def showLabels(self, index):
        image, targets = self[index]

        plt.imshow(utils.draw_bounding_boxes(
            image.mul(255).type(torch.uint8), targets['boxes'], width=4
        ).moveaxis(0, 2))
        plt.savefig("img.png", dpi=2000)

    def __len__(self):
        return len(self.ids)
    
    def get_category(self, cat_id):
        return self.data['categories'][str(cat_id)]
