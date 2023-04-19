from processor.staff_utils import *

# only import if script is ran directly, these imports are quite slow
import matplotlib.pyplot as plt
import torch
from torchvision.utils import draw_bounding_boxes

def test_staff_utils():
    img = cv2.imread("sheets/genshin main theme.png", cv2.IMREAD_GRAYSCALE)
    width = img.shape[1]
    bars = section(img)

    # start = time.time()

    # staffs = get_staffs(img)
    # bars: list[Label] = []
    # for staff in staffs:
    #     bars.extend(get_bars(img, staff))

    boxes = [staff.bbox for staff in bars]
    labels = [staff.name for staff in bars]

    # end = time.time()
    # print(f"Process time: {end - start}")


    plt.imshow(draw_bounding_boxes(torch.tensor(img).unsqueeze(0), torch.tensor(boxes), labels).moveaxis(0, 2))

    plt.savefig("staffs.png", dpi=800)
    plt.show()

def test_processor():
    from processor.processor import MusicParser2
    import json

    with open(f"nggup2.json") as f:
        labels = json.load(f)
    
    labels = [Label(x['bbox'], x['name']) for x in labels]

    parser = MusicParser2(labels, "sheets/genshin main theme.png")
    parser.process()

    with open(f"test2.json", 'w') as f:
        f.write(json.dumps(parser.to_dict()))

test_processor()