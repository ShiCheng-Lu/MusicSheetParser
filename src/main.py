'''
Editor bounding boxes
'''

import pygame
import pygame_gui
from editor.music import Music
from editor.selction_gui import EditorMenu
from editor.sheet_display import SheetDisplay
import common.music
import json


# from processor.music_processor import MusicParser
# parser = MusicParser(file)
# parser.process()

import json
with open(f"test.json") as f:
    parser = common.music.Music().from_dict(json.load(f))

music = Music(parser)

pygame.init()
w, h = 1080, 860
screen = pygame.display.set_mode((w, h))
running = True

# file = "sheets/bohemia rhapsody.png"
file = "sheets/genshin main theme.png"
# file = "sheets/imagine john lennon.png"
# file = "sheets/never gonna give you up.png"

img = pygame.image.load(file)
img.convert()

manager = pygame_gui.UIManager((w, h))
menu = EditorMenu(manager, music)
display = SheetDisplay(manager, img, music)
menu.display = display
display.menu = menu

def save_and_update():
    with open(f"test.json", 'w') as f:
        f.write(json.dumps(music.to_dict()))
    display.render()
menu.on_update = save_and_update

clock = pygame.time.Clock()
while running:
    time_delta = clock.tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        manager.process_events(event)

    manager.update(time_delta)
    manager.draw_ui(screen)

    pygame.display.update()

pygame.quit()