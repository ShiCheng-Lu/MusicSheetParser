import pygame
import pygame_gui
from common.label import Bbox
from editor.music import Note, Music

w, h = 1080, 860
# menu_rect = Bbox([900, 0, 1080, 860])

class SheetDisplay(pygame_gui.elements.UIImage):
    def __init__(self, manager, image, music: Music):
        super().__init__(relative_rect=pygame.Rect(0, 0, 900, h),
            manager=manager,
            image_surface=image)

        self.scale = 1
        self.music_image = image
        self.image_rect = image.get_rect()
        self.surface = pygame.Surface((self.image_rect.width, self.image_rect.height))
        self.display_surface = pygame.Surface((900, h))
        self.offset = Bbox((0, 0, 0, 0))

        self.music = music

        self.moved = False
        self.moving = False
        self.selected = None
        self.menu = None
        
        self.update_render(None)
        self.render()
    
    def update_render(self, selected):
        self.surface.fill((0, 0, 0))
        self.surface.blit(self.music_image, (0, 0))
        self.music.render(self.surface, selected)
    
    def render(self):
        self.display_surface.fill((0, 0, 0))

        result = pygame.transform.scale(self.surface, 
            (self.image_rect.width * self.scale, self.image_rect.height * self.scale))
        self.display_surface.blit(result, (self.offset.x_min, self.offset.y_min))

        self.set_image(self.display_surface)

    def process_event(self, event):
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
            if self.display_surface.get_rect().collidepoint(event.pos):
                selected = None
                
                x = (event.pos[0] - self.offset.x_min) / self.scale
                y = (event.pos[1] - self.offset.y_min) / self.scale

                selected = self.music.select(x, y)
                self.update_render(selected)
                self.render()

                self.menu.set_selected(selected, x, y)
