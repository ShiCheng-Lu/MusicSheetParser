import pygame
import pygame_gui
from common.label import Bbox
from editor.music import Note, Music

w, h = 1080, 860
# menu_rect = Bbox([900, 0, 1080, 860])

class SheetDisplay:
    def __init__(self, manager, image, music: Music, on_select_note):
        self.scale = 1
        self.image = image
        self.image_rect = image.get_rect()
        self.surface = pygame.Surface((self.image_rect.width, self.image_rect.height))
        self.offset = Bbox((0, 0, 0, 0))

        self.music = music
        self.on_selected_note = on_select_note

        self.display_image = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(0, 0, 900, h),
            manager=manager,
            image_surface=self.surface)
        
        self.moved = False
        self.moving = False
        self.selected = None
        
        self.update()
        self.render()
    
    def update(self):
        self.surface.fill((0, 0, 0))
        self.surface.blit(self.image, (0, 0))
        self.music.render(self.surface)
    
    def render(self):
        surface = pygame.Surface((900, h))
        result = pygame.transform.scale(self.surface, 
            (self.image_rect.width * self.scale, self.image_rect.height * self.scale))
        surface.blit(result, (self.offset.x_min, self.offset.y_min))

        self.display_image.set_image(surface)

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
                self.offset.scale(1.1, 1.1)
                self.offset.move(-w / 2 * 0.1, -h / 2 * 0.1)
                self.render()
            
            if event.button == pygame.BUTTON_WHEELDOWN:
                # zoom out relative to center of screen
                self.scale *= 0.9
                self.offset.scale(0.9, 0.9)
                self.offset.move(w / 2 * 0.1, h / 2 * 0.1)
                self.render()
            
            if event.button == pygame.BUTTON_LEFT:
                self.moving = True
                self.moved = False

        if event.type == pygame.MOUSEBUTTONUP:
            self.moving = False

        if event.type == pygame.MOUSEMOTION and self.moving:
            self.moved = True
            self.offset.move(*event.rel)
            self.render()
        
        if event.type == pygame.MOUSEBUTTONUP and event.button == pygame.BUTTON_LEFT and not self.moved:
            mouse_pos = Bbox(event.pos * 2)
            selected = None
            
            # selected = self.music.select()
            for staff in self.music.staffs:
                for bar in staff.bars:
                    for note in bar.notes:
                        if mouse_pos.intersects(note):
                            selected = note
                        note.render_color = (25, 200, 25)
            
            if selected != None:
                selected.render_color = (200, 150, 25)
            if self.on_selected_note:
                self.on_selected_note(selected)
            self.render()