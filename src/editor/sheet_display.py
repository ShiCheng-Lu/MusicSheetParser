import pygame
import pygame_gui
from common import Bbox
from editor.note import Note

w, h = 1080, 860
# menu_rect = Bbox([900, 0, 1080, 860])

class SheetDisplay:
    def __init__(self, manager, image, notes, on_select_note):
        self.surface = pygame.Surface((900, h))
        self.scale = 1
        self.image = image
        self.image_rect = image.get_rect()
        self.notes: list[Note] = notes
        self.on_selected_note = on_select_note

        self.display_image = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(0, 0, 900, h),
            manager=manager,
            image_surface=self.surface)
        
        self.moved = False
        self.moving = False
        self.selected = None

        self.render()
    
    def render(self):
        display_img = pygame.transform.scale(self.image, 
            (self.image_rect.width * self.scale, self.image_rect.height * self.scale))
        self.surface.fill((0, 0, 0))
        self.surface.blit(display_img, self.image_rect)
        for note in self.notes:
            note.updatePos(self.image_rect.x, self.image_rect.y, self.scale)
            note.render(self.surface)

        self.display_image.set_image(self.surface)

    def process_event(self, event):
        # all events require event.pos, ignore events that doesn have it
        try:
            if not self.surface.get_rect().collidepoint(event.pos):
                return
        except AttributeError:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_WHEELUP:
                # zoom in
                self.scale *= 1.1
                self.image_rect.x = w//2 - (w//2 - self.image_rect.x) * 1.1
                self.image_rect.y = h//2 - (h//2 - self.image_rect.y) * 1.1
                self.render()
            
            if event.button == pygame.BUTTON_WHEELDOWN:
                # zoom out relative to center of screen
                self.scale *= 0.9
                self.image_rect.x = w//2 - (w//2 - self.image_rect.x) * 0.9
                self.image_rect.y = h//2 - (h//2 - self.image_rect.y) * 0.9
                self.render()
            
            if event.button == pygame.BUTTON_LEFT:
                self.moving = True
                self.moved = False

        if event.type == pygame.MOUSEBUTTONUP:
            self.moving = False

        if event.type == pygame.MOUSEMOTION and self.moving:
            self.moved = True
            self.image_rect.move_ip(event.rel)
            self.render()
        
        if event.type == pygame.MOUSEBUTTONUP and event.button == pygame.BUTTON_LEFT and not self.moved:
            mouse_pos = Bbox(event.pos * 2)
            selected = None
            for note in self.notes:
                if mouse_pos.intersects(note.renderBox):
                    selected = note
                note.renderColour = (25, 200, 25)
            if selected != None:
                selected.renderColour = (200, 150, 25)
                if self.on_selected_note: self.on_selected_note(selected)
            self.render()