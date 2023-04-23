import pygame
import common.music
import pygame_gui
from common.label import Bbox
import editor.pygame_utils
import player.music
from player.piano_player import PianoPlayer

width = 180

class MusicEditorMenu(pygame_gui.elements.UIPanel):
    def __init__(self, manager, parent):
        super().__init__(relative_rect=pygame.Rect(900, 0, 180, 860))
        self.parent = parent

        self.time_sig_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, width, 50),
            container=self,
            manager=manager,
            text="Time Signature:",)
        
        self.play_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, width, 50),
            container=self,
            manager=manager,
            anchors={'top_target': self.time_sig_label},
            text="Play")
        
        self.save_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, -50, width, 50),
            container=self,
            manager=manager,
            anchors={'bottom': 'bottom'},
            text="Save")
    
    def set_selected(self, music):
        self.selected = music

    def process_event(self, event: pygame.event.Event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.play_button:
                playable = player.music.Music(self.selected)
                playable.play(PianoPlayer())