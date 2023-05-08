
import pygame_gui
from common.label import Bbox
import editor.pygame_utils as pygame_utils
from editor.note_editor import Note, NoteEditorMenu
from editor.bar_editor import Bar, BarEditorMenu
from editor.music_editor import MusicEditorMenu
import json

w, h = 1080, 860
menu_rect = Bbox([900, 0, 1080, 860])

class EditorMenu:
    def __init__(self, manager, music, on_update=None):
        self.music = music
        self.update_func = on_update

        self.panel = pygame_gui.elements.UIPanel(relative_rect=pygame_utils.to_pygame_rect(menu_rect))

        self.note_editor_menu = NoteEditorMenu(manager, self.on_update)
        self.bar_editor_menu = BarEditorMenu(manager, self.on_update)
        self.music_editor_menu = MusicEditorMenu(manager, self.on_update)

        self.display = None
        
        self.set_selected(music, 0, 0)
    
    def set_selected(self, selected, x, y):
        if isinstance(selected, Note):
            self.active_menu = self.note_editor_menu
        elif isinstance(selected, Bar):
            self.active_menu = self.bar_editor_menu
            self.bar_editor_menu.add_note_pos = (x, y)
        else:
            selected = self.music
            self.active_menu = self.music_editor_menu
        
        self.note_editor_menu.hide()
        self.bar_editor_menu.hide()
        self.music_editor_menu.hide()

        self.active_menu.set_selected(selected)
        self.active_menu.show()

    def on_update(self):
        self.display.update_render(self.active_menu.selected)
        self.display.render()

        with open(f"test.json", 'w') as f:
            f.write(json.dumps(self.music.to_dict()))

