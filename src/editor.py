'''
Editor bounding boxes
'''

import pygame
from pygame.locals import *
from common import Label, Bbox
from music import PITCH_MAP

pygame.init()
w, h = 1080, 860
screen = pygame.display.set_mode((w, h))
running = True

img = pygame.image.load("sheets/genshin main theme.png")

img.convert()
rect = img.get_rect()
rect.center = w//2, h//2
moving = False
moved = False

scale = 1

font = pygame.font.Font('freesansbold.ttf', 20)
NON_NOTE_LABELS = [
    "restDoubleWhole",
    "restWhole",
    "restHalf",
    "restQuarter",
    "rest8th",
    "rest16th",
    "rest32nd",
    "rest64th",
    "rest128th",
]
PITCH_MAP_LABEL = {
    pitch : font.render(pitch, True, (25, 25, 255))
    for pitch in PITCH_MAP + NON_NOTE_LABELS
}

class Note(Label):
    def __init__(self, bbox, name, duration):
        super().__init__(bbox, name)
        durationText = f"1/{1/duration:.3}".rstrip('.0') if 'rest' not in name else ''
        self.text = font.render(f"{durationText}{name}", True, (25, 25, 255))
        self.textRect = self.text.get_rect()
        self.textRect.x = self.x_min
        self.textRect.bottom = self.y_min
        self.renderBox = Bbox(bbox)

    def render(self, screen):
        # draw box
        thickness = 3
        xywh = [
            self.renderBox.x_min, 
            self.renderBox.y_min, 
            self.renderBox.width + thickness, 
            self.renderBox.height + thickness]
        pygame.draw.rect(screen, (25, 200, 25), xywh, thickness)
        # draw text
        screen.blit(self.text, self.textRect)
    
    def updatePos(self, x, y, scale):
        self.renderBox.bbox = [
            self.x_min * scale + x,
            self.y_min * scale + y,
            self.x_max * scale + x,
            self.y_max * scale + y,
        ]
        self.textRect.x = self.renderBox.x_min
        self.textRect.bottom = self.renderBox.y_min


import json
with open(f"notes.json") as f:
    labels = json.load(f)
notes = [Note(x['bbox'], x['name'], x['duration']) for x in labels]

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        if event.type == MOUSEBUTTONDOWN:
            if rect.collidepoint(event.pos):
                moving = True
            moved = False

        if event.type == MOUSEBUTTONUP:
            moving = False

        if event.type == MOUSEMOTION and moving:
            moved = True
            rect.move_ip(event.rel)
            for note in notes:
                note.updatePos(rect.x, rect.y, scale)
        
        if event.type == MOUSEWHEEL and event.y < 0 and scale > 0.2:
            # zoom out relative to center of screen
            scale *= 0.9
            rect.x = w//2 - (w//2 - rect.x) * 0.9
            rect.y = h//2 - (h//2 - rect.y) * 0.9
            for note in notes:
                note.updatePos(rect.x, rect.y, scale)
        
        if event.type == MOUSEWHEEL and event.y > 0:
            # zoom in
            scale *= 1.1
            rect.x = w//2 - (w//2 - rect.x) * 1.1
            rect.y = h//2 - (h//2 - rect.y) * 1.1
            for note in notes:
                note.updatePos(rect.x, rect.y, scale)
        
        if event.type == MOUSEBUTTONUP and event.button == BUTTON_LEFT and not moved:
            mouse_pos = Bbox(event.pos * 2)
            for label in notes:
                if mouse_pos.intersects(label):
                    print(label.name)
    
    display_img = pygame.transform.scale(img, (rect.width * scale, rect.height * scale))
    
    screen.fill((0, 0, 0))
    screen.blit(display_img, rect)

    for note in notes:
        note.render(screen)

    pygame.display.update()

pygame.quit()