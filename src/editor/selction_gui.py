
import pygame
import pygame_gui
from common.label import Bbox
import common.music
import editor.pygame_utils as pygame_utils
from editor.note_editor import Note, NoteEditorMenu
from editor.bar_editor import Bar, BarEditorMenu
import json

TONE_MAP = [
    "A0", "B0", "C1", "D1", "E1", "F1", "G1",
    "A1", "B1", "C2", "D2", "E2", "F2", "G2",
    "A2", "B2", "C3", "D3", "E3", "F3", "G3",
    "A3", "B3", "C4", "D4", "E4", "F4", "G4",
    "A4", "B4", "C5", "D5", "E5", "F5", "G5",
    "A5", "B5", "C6", "D6", "E6", "F6", "G6",
    "A6", "B6", "C7", "D7", "E7", "F7", "G7",
    "A7", "B7",
]
A4_POS = TONE_MAP.index("A4")

MOD_MAP = {"None": None, "Natural": 0, "Sharp": 1, "Flat": -1, "DoubleSharp": 2, "DoubleFlat": -2}

w, h = 1080, 860
menu_rect = Bbox([900, 0, 1080, 860])

class MusicEditorMenu(pygame_gui.elements.UIPanel):
    def __init__(self):
        super().__init__(relative_rect=pygame.Rect(900, 0, 180, 860))

    def set_selected(self, selected):
        pass

class EditorMenu:
    def __init__(self, manager, music, on_update=None):
        self.music = music
        self.update_func = on_update

        self.panel = pygame_gui.elements.UIPanel(relative_rect=pygame_utils.to_pygame_rect(menu_rect))

        self.note_editor_menu = NoteEditorMenu(manager, self.on_update)
        self.bar_editor_menu = BarEditorMenu(manager, self.on_update)
        self.music_editor_menu = MusicEditorMenu()

        self.display = None
        
        self.set_selected(None, 0, 0)
    
    def set_selected(self, selected, x, y):
        if isinstance(selected, Note):
            self.active_menu = self.note_editor_menu
        elif isinstance(selected, Bar):
            self.active_menu = self.bar_editor_menu
            self.bar_editor_menu.add_note_pos = (x, y)
        else:
            self.active_menu = self.music_editor_menu
        
        self.note_editor_menu.hide()
        self.bar_editor_menu.hide()

        self.active_menu.set_selected(selected)
        self.active_menu.show()

    def on_update(self):
        print("update")
        self.display.update_render(self.active_menu.selected)
        self.display.render()
