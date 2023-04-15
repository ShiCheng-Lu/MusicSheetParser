'''
Editor bounding boxes
'''

import pygame
from pygame.locals import *
import pygame_gui
from editor.note import Note
from editor.selction_gui import NoteEditorMenu
from editor.sheet_display import SheetDisplay
import json

pygame.init()
w, h = 1080, 860
screen = pygame.display.set_mode((w, h))
running = True

img = pygame.image.load("sheets/genshin main theme.png")
img.convert()

with open(f"notes.json") as f:
    labels = json.load(f)
notes = [Note(x['bbox'], x['name'], x['duration']) for x in labels]

manager = pygame_gui.UIManager((w, h))
menu = NoteEditorMenu(manager)
display = SheetDisplay(manager, img, notes, menu.set_selected)

clock = pygame.time.Clock()
while running:
    time_delta = clock.tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        display.process_event(event)
        manager.process_events(event)
        menu.process_event(event)

    manager.update(time_delta)
    manager.draw_ui(screen)

    pygame.display.update()

pygame.quit()
