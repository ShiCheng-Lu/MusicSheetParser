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


    # boxes = [note.label.bbox for note in parser.notes]
    # labels = [note.label.name if note.pitch == None else music.PITCH_MAP[note.pitch] for note in parser.notes]

    # plt.imshow(draw_bounding_boxes(torch.tensor(parser.image).unsqueeze(0), torch.tensor(boxes), labels, font_size=30).moveaxis(0, 2))
    
    import pygame
    import pygame_gui
    from editor.music import Music
    from editor.selction_gui import NoteEditorMenu
    from editor.sheet_display import SheetDisplay
    import json

    # notes = [Note(note) for note in parser.notes]

    pygame.init()
    w, h = 1080, 860
    screen = pygame.display.set_mode((w, h))
    running = True

    img = pygame.image.load("sheets/genshin main theme.png")
    img.convert()

    manager = pygame_gui.UIManager((w, h))
    menu = NoteEditorMenu(manager)
    display = SheetDisplay(manager, img, Music(parser), menu.set_selected)

    clock = pygame.time.Clock()
    while running:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            display.process_event(event)
            manager.process_events(event)
            menu.process_event(event)

        manager.update(time_delta)
        manager.draw_ui(screen)

        pygame.display.update()

    pygame.quit()


test_processor()