import cv2
from common import Label

def get_staff(file_name, label_name="staff"):
    img = cv2.imread(file_name, cv2.IMREAD_GRAYSCALE)
    width = img.shape[1]
    height = img.shape[0]
    dim = (1, height) # keep original height
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    
    staff_starts = []
    last_dense_line = 0
    for index, density in enumerate(resized):
        if density[0] < 50:
            if index > last_dense_line:
                staff_starts.append(index)
            last_dense_line = index + height / 50

    staff_ends = []
    last_dense_line = height
    for index, density in reversed(list(enumerate(resized))):
        if density[0] < 50:
            if index < last_dense_line:
                staff_ends.append(index)
            last_dense_line = index - height / 50
    staff_ends.reverse()

    return [Label([0, start, width, end], label_name) for start, end in zip(staff_starts, staff_ends)]

if __name__ == "__main__":
    # only import if script is ran directly, these imports are quite slow
    import matplotlib.pyplot as plt
    import torch
    from torchvision.utils import draw_bounding_boxes

    file_name = "sheets/genshin main theme.png"

    staffs = get_staff(file_name)

    img = cv2.imread(file_name, cv2.IMREAD_GRAYSCALE)
    boxes = [staff.bbox for staff in staffs]
    labels = [staff.name for staff in staffs]

    print(boxes)

    plt.imshow(draw_bounding_boxes(torch.tensor(img).unsqueeze(0), torch.tensor(boxes), labels).moveaxis(0, 2))

    plt.savefig("staffs.png", dpi=800)
    plt.show()
