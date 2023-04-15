from processor.staff_utils import *

# only import if script is ran directly, these imports are quite slow
import matplotlib.pyplot as plt
import torch
from torchvision.utils import draw_bounding_boxes
import time

img = cv2.imread("sheets/monstadt medley.png", cv2.IMREAD_GRAYSCALE)
width = img.shape[1]
bars = vertical_section(img)

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

