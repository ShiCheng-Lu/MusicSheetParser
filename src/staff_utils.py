import cv2
from common import Label

def get_staff(img: cv2.Mat, label_name="staff"):
    '''
    Get Labels of staffs sorted by y value, use longest black horizontal lines in the image
    - image
    '''
    width = img.shape[1]
    height = img.shape[0]
    dim = (1, height) # keep original height
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA).flatten()

    DENSITY_THRESHOLD = min(resized) * 2 # density cutoff for a horizonal staff line relative to the page width, 0 to 255
    STAFF_VERTICAL_GAP = height / 50 # max vertical height between each line of the staff
    
    staff_starts = []
    last_dense_line = 0
    for index, density in enumerate(resized):
        if density < DENSITY_THRESHOLD:
            if index > last_dense_line:
                staff_starts.append(index)
            last_dense_line = index + STAFF_VERTICAL_GAP

    staff_ends = []
    last_dense_line = height
    for index, density in reversed(list(enumerate(resized))):
        if density < DENSITY_THRESHOLD:
            if index < last_dense_line:
                staff_ends.append(index)
            last_dense_line = index - STAFF_VERTICAL_GAP
    staff_ends.reverse()

    return [Label([0, start, width, end], label_name) for start, end in zip(staff_starts, staff_ends)]

def get_bars(img: cv2.Mat, staff: Label, avoid: list[Label]=[], label_name="bar"):
    '''
    Get bars
    - file_name: name of the image file for processing
    - staff: the staff Label to get the bars from
    - label_name: name of the labels to generate
    '''
    DENSITY_THRESHOLD = 5 # density cutoff for a vertical bar line relative to the staff height, 0 to 255
    # full line through the staff, exactly the same from left and right
    width = img.shape[1]
    dim = (width, 1) # keep original height
    resized = cv2.resize(img[staff.y_min:staff.y_max,:], dim, interpolation = cv2.INTER_AREA)[0]

    for section in avoid:
        resized[:, section.x_min:section.x_max] = 255

    bars_candidate: list[Label] = []
    last_bar = None
    for index, density in enumerate(resized):
        if density < DENSITY_THRESHOLD:
            if last_bar == None:
                last_bar = Label([index, staff.y_min, index, staff.y_max], label_name)
                bars_candidate.append(last_bar)
            last_bar.x_max = index
        else:
            last_bar = None
    
    bars: list[Label] = []
    for bar in bars_candidate:
        '''
        a bar must:
        1. have the same pixel arragement to the left/right of the bar
        2. end above or below the staff, does not extend out both above and below
        This is to ensure note stems are not detected as bars,
        every notehead that has a stem going through the entire staff will
        - have notehead/beam within the staff, fails condition 1
        - have both notehead and beam outside the staff, fails condition 2
        Sometimes bars will be missed due to symbols that go over bars, such as tie/slur
        '''
        x_min_sample = img[staff.y_min:staff.y_max, bar.x_min - (bar.width + 1)]
        x_max_sample = img[staff.y_min:staff.y_max, bar.x_max + (bar.width + 1)]

        if any(a != b for a, b in zip(x_min_sample, x_max_sample)):
            continue
        
        y_min_sample = img[staff.y_min - (bar.width + 1), bar.x_min:bar.x_max]
        y_max_sample = img[staff.y_max + (bar.width + 1), bar.x_min:bar.x_max]

        print(y_min_sample, y_max_sample)

        if (sum(y_min_sample) == 0) and (sum(y_max_sample) == 0):
            continue

        bars.append(bar)

    return bars

if __name__ == "__main__":
    # only import if script is ran directly, these imports are quite slow
    import matplotlib.pyplot as plt
    import torch
    from torchvision.utils import draw_bounding_boxes
    
    img = cv2.imread("sheets/bohemia rhapsody.png", cv2.IMREAD_GRAYSCALE)

    staffs = get_staff(img)
    bars: list[Label] = []
    for staff in staffs:
        bars.extend(get_bars(img, staff))

    boxes = [staff.bbox for staff in bars]
    labels = [staff.name for staff in bars]

    plt.imshow(draw_bounding_boxes(torch.tensor(img).unsqueeze(0), torch.tensor(boxes), labels).moveaxis(0, 2))

    plt.savefig("staffs.png", dpi=800)
    plt.show()
