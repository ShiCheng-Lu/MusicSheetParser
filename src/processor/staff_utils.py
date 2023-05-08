import cv2
from common.label import Label, Bbox
from common.music import Staff, Bar

def get_staffs(img: cv2.Mat, label_name="staff") -> list[Staff]:
    '''
    Get Labels of staffs sorted by y value, use longest black horizontal lines in the image
    - img: the image matrix
    - label_name (Optional): the name of generated staff labels
    '''
    width = img.shape[1]
    height = img.shape[0]
    dim = (1, height) # keep original height
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA).flatten()

    DENSITY_THRESHOLD = 64 # density cutoff for a horizonal staff line relative to the page width, 0 to 255
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

    return [Staff([0, start, width, end], f"{label_name}-{index}") 
            for index, start, end in zip(range(len(staff_starts)), staff_starts, staff_ends)]

def get_bars(img: cv2.Mat, staff: Staff, avoid: list[Label]=[], label_name="bar"):
    '''
    Get bars
    - img: the image matrix
    - staff: the staff Label to get the bars from
    - label_name (Optional): name of the labels to generate
    '''
    DENSITY_THRESHOLD = 5 # density cutoff for a vertical bar line relative to the staff height, 0 to 255
    # full line through the staff, exactly the same from left and right
    height, width = img.shape

    dim = (width, 1) # keep original height
    resized = cv2.resize(img[staff.y_min:staff.y_max,:], dim, interpolation = cv2.INTER_AREA)[0]

    for section in avoid:
        resized[:, section.x_min:section.x_max] = 255

    '''
    a bar candidate is any vertical straight line that vertically spans the entire staff
    '''
    bars_candidate: list[Bar] = []
    last_bar = None
    for index, density in enumerate(resized):
        if density < DENSITY_THRESHOLD:
            if last_bar == None:
                last_bar = Bar([index, staff.y_min, index, staff.y_max], label_name)
                bars_candidate.append(last_bar)
            last_bar.x_max = index
        else:
            last_bar = None

    '''
    a bar must:
    - end at top and bottom flat
    - corners of bars are white
    '''
    bars: list[Label] = []
    for bar in bars_candidate:
        lt = bar.y_min
        rt = bar.y_min
        lb = bar.y_max
        rb = bar.y_max

        while img[lt][bar.x_min] == 0 and lt > 0:
            lt -= 1
        while img[rt][bar.x_max] == 0 and rt > 0:
            rt -= 1
        while img[lb][bar.x_min] == 0 and lb < height:
            lb += 1
        while img[rb][bar.x_max] == 0 and rb < height:
            rb += 1
        
        # ends flat
        if lt != rt or lb != rb:
            continue
        
        # corners are white
        if img[lt - 1][bar.x_min - 1] != 255:
            continue
        if img[rt - 1][bar.x_max + 1] != 255:
            continue
        if img[lb + 1][bar.x_max - 1] != 255:
            continue
        if img[rb + 1][bar.x_max + 1] != 255:
            continue
        
        if resized[bar.x_min - 1] < 50:
            continue
        if resized[bar.x_max + 1] < 50:
            continue

        bars.append(bar)

    return bars

def vertical_section(img: cv2.Mat, staffs: list[Staff] = None) -> list[Label]:
    if staffs == None:
        staffs = get_staffs(img)

    # split image vertically based on staffs
    width = img.shape[1]
    height = img.shape[0]
    dim = (1, height) # keep original height
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA).flatten()

    # median y of the brightest rows
    cutoffs = []
    low = max(staffs[0].y_min - staffs[0].height * 2, 0)
    high = min(staffs[-1].y_max + staffs[-1].height * 2, height)
    for staff in staffs + [Bbox([0, high, 0, 0])]:
        high = staff.y_min
        # find median y of the brightest rows
        brightest = [low]
        for row in range(low, high):
            if resized[row] > resized[brightest[0]]:
                brightest = [row]
            elif resized[row] == resized[brightest[0]]:
                brightest.append(row)
        cutoffs.append(brightest[len(brightest) // 2])
        # prepare for next iteration
        low = staff.y_max

    # remove rows that are not over the brightness cuffoff
    for cutoff in cutoffs:
        if resized[cutoff] < 254:
            cutoffs.remove(cutoff)

    labels = []
    for y_min, y_max in zip(cutoffs[:-1], cutoffs[1:]):
        labels.append(Label([0, y_min, width, y_max]))

    return labels

import math

def section(img: cv2.Mat) -> list[Label]:
    img = cv2.threshold(img.copy(), 250, 255, cv2.THRESH_BINARY)[1]

    staffs = get_staffs(img)
    vertial_sections = vertical_section(img, staffs)

    sections = []

    for section in vertial_sections:
        section_staffs = []
        section_bars: list[Label] = []
        for staff in staffs:
            if section.intersects(staff):
                section_staffs.append(staff)
            
                for bar in get_bars(img, staff):
                    bar.y_min = 0
                    bar.y_max = math.inf
                    for section_bar in section_bars:
                        if bar.intersects(section_bar):
                            break
                    else:
                        section_bars.append(bar)

        for left, right in zip(section_bars[:-1], section_bars[1:]):
            sections.append(Label([left.x_max, section.y_min, right.x_min, section.y_max], "section"))

    return sections

def pitch_from_pos(staff: Staff, bbox: Bbox):
    '''
    get the relative position of a bbox based on the center of the bbox and the staff
    '''
    center = (bbox.y_min + bbox.y_max) / 2
    staff_center = (staff.y_max + staff.y_min) / 2
    rel_position = round((staff_center - center) / (staff.height / 8))
    
    # offset rel_position to number of lines from A4 (tuned at 440Hz)
    match staff.clef.name:
        case 'clefG': # treble clef
            rel_position += 1
        case 'clefCAlto':
            rel_position -= 5
        case 'clefCTenor':
            rel_position -= 7
        case 'clefF': # base clef
            rel_position -= 11

    return int(rel_position)