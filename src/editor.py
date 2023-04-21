'''
Editor bounding boxes
'''

import pygame
import pygame_gui
from editor.music import Music
from editor.selction_gui import NoteEditorMenu
from editor.sheet_display import SheetDisplay
from processor.processor import MusicParser2

# notes = [Note(note) for note in parser.notes]

pygame.init()
w, h = 1080, 860
screen = pygame.display.set_mode((w, h))
running = True

img = pygame.image.load("sheets/genshin main theme.png")
img.convert()

parser = MusicParser2("sheets/genshin main theme.png")
parser.process()

music = Music(parser)

manager = pygame_gui.UIManager((w, h))
menu = NoteEditorMenu(manager, music)
display = SheetDisplay(manager, img, music, menu.set_selected)

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