from processor.staff_utils import *
import matplotlib.pyplot as plt
import torch
from torchvision.utils import draw_bounding_boxes
import json

def test_staff_utils():
    img = cv2.imread("sheets/bohemia rhapsody.png", cv2.IMREAD_GRAYSCALE)
    cv2.threshold(img, 250, 255, cv2.THRESH_BINARY, img)
    width = img.shape[1]
    bars = section(img)

    # start = time.time()

    staffs = get_staffs(img)
    bars: list[Label] = []
    for staff in staffs:
        bars.extend(get_bars(img, staff))

    boxes = [staff.bbox for staff in bars]
    labels = [staff.name for staff in bars]

    # end = time.time()
    # print(f"Process time: {end - start}")


    plt.imshow(draw_bounding_boxes(torch.tensor(img).unsqueeze(0), torch.tensor(boxes), labels).moveaxis(0, 2))

    plt.savefig("staffs.png", dpi=800)
    plt.show()

# def test_section_detect():
    
#     with open(f"category.json") as f:
#         categories = json.load(f)
    
#     detector = MusicSymbolDetector()
#     detector.load("saved_models_bars/10")

#     labels: list[Label] = []

#     image = cv2.imread("sheets/genshin main theme.png", cv2.IMREAD_GRAYSCALE)
#     for section in processor.staff_utils.section(image):
#         image_section = image[section.y_min:section.y_max, section.x_min:section.x_max]
#         res = detector(torch.tensor(image_section).div(255).unsqueeze(0))
#         labels.extend(res)

#         for label in res:
#             label.name = categories[str(label.name)]["name"]
        
#         boxes = [label.bbox for label in res]
#         labels = [label.name for label in res]

#         plt.imshow(draw_bounding_boxes(torch.tensor(image_section).unsqueeze(0), torch.tensor(boxes), labels).moveaxis(0, 2))
#         plt.show()
    
#     parser = MusicParser2(labels, "sheets/genshin main theme.png")
#     parser.process()

#     with open(f"test3.json", 'w') as f:
#         f.write(json.dumps(parser.to_dict()))

test_staff_utils()
