import torch
import torchvision
from torch.utils.data import DataLoader
import math
import sys
from tqdm import tqdm
from common.label import Label
from model.dataset import MusicSheetDataSet

if (torch.cuda.is_available()):
    device = torch.device("cuda")
    print(device, torch.cuda.get_device_name(0))
else:
    device = torch.device("cpu")
    print(device)
print(torch.__version__)
print(torchvision.__version__)

class MusicSymbolDetector:
    def __init__(self):
        self.model = torchvision.models.detection.fasterrcnn_resnet50_fpn_v2(
            pretrained=True,
            num_classes=137,
            min_size=720,
            max_size=720,
            box_detections_per_img=50
        )

        params = [p for p in self.model.parameters() if p.requires_grad]
        self.optimizer = torch.optim.Adam(params)
        self.epoch = 0
        self.loss = 0
    
    def __call__(self, image):
        self.model.to(device)
        self.model.eval()

        torch_image = torch.tensor(image).div(255).unsqueeze(0).to(device)

        result = self.model([torch_image])[0]

        boxes = result["boxes"].detach().cpu()
        labels = result["labels"].detach().cpu()
        scores = result["scores"].detach().cpu()

        return [
            Label(
                box.tolist(),
                label.item(),
            ) for box, label, score in zip(boxes, labels, scores) if score >= 0.8
        ]
    
    def save(self, path):
        torch.save({
            "model": self.model.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "epoch": self.epoch,
            "loss": self.loss,
        }, path)

    def load(self, path = None):
        if path == None:
            path = self
            self = MusicSymbolDetector()
        
        data = torch.load(path)
        self.model.load_state_dict(data['model'])
        self.optimizer.load_state_dict(data['optimizer'])
        current_epoch = data['epoch']
        
        print("loaded model at epoch: {}, loss: {}".format(current_epoch, data['loss']))

        # move optimizer to cuda
        for state in self.optimizer.state.values():
            for k, v in state.items():
                if isinstance(v, torch.Tensor):
                    state[k] = v.to(device)

        return self
    
    def train(self, dataset: MusicSheetDataSet, epochs: int = 1, transform = None):
        self.model.to(device)
        self.model.train()
        torch.cuda.empty_cache()

        data_count = 10000

        for _ in range(epochs):
            all_losses = 0
            all_losses_dict = {}

            dataloader = DataLoader(
                dataset.random(10000),
                collate_fn=lambda x : zip(*x),
                shuffle = True
            )

            for images, targets in tqdm(dataloader):
                if transform != None:
                    images, targets = transform(images, targets, dataset)
                
                images = [image.to(device) for image in images]
                targets = [{k: v.to(device) for k, v in t.items()} for t in targets]

                if any(len(target['boxes']) == 0 for target in targets):
                    continue

                self.optimizer.zero_grad(set_to_none=True)

                loss_dict: dict[str, torch.Tensor] = self.model(images, targets) # the model computes the loss automatically if we pass in targets

                losses: torch.Tensor = sum(loss for loss in loss_dict.values())

                loss_value = losses.item()
                all_losses += loss_value
                
                for k, v in loss_dict.items():
                    if k not in all_losses_dict:
                        all_losses_dict[k] = 0
                    all_losses_dict[k] += v
                
                if not math.isfinite(loss_value):
                    print(f"Loss is {loss_value}, stopping trainig") # train if loss becomes infinity
                    print(loss_dict)
                    sys.exit(1)
                
                losses.backward()
                
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1)
                self.optimizer.step()
            
            self.epoch += 1
            self.loss = all_losses / data_count
            print("Epoch {:>3}, lr: {:.6f}, loss: {:.6f}, {}".format(
                self.epoch,
                self.optimizer.param_groups[0]['lr'], 
                self.loss,
                ', '.join("{}: {:.6f}".format(k, v / data_count) for k, v in all_losses_dict.items()),
            ))

            self.save(f"../saved_models_bars/{self.epoch}")
