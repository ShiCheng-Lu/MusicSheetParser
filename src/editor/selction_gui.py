
import pygame
import pygame_gui
from common import Bbox
import music
import editor.pygame_utils as pygame_utils
from editor.note import Note

w, h = 1080, 860
menu_rect = Bbox([900, 0, 1080, 860])

class NoteEditorMenu:
    def __init__(self, manager):
        self.panel = pygame_gui.elements.UIPanel(relative_rect=pygame_utils.to_pygame_rect(menu_rect))

        self.pitch_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, menu_rect.width, 50),
            container=self.panel,
            manager=manager,
            text="Note Pitch:",)
        self.pitch_selector = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(0, 0, menu_rect.width, 50),
            container=self.panel,
            manager=manager,
            anchors={"top_target": self.pitch_label},
            options_list=music.PITCH_MAP,
            starting_option="A4",)
        
        self.modifier_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, menu_rect.width, 50),
            container=self.panel,
            manager=manager,
            anchors={"top_target": self.pitch_selector},
            text="Note Modifier:",)
        self.modifier_selector = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(0, 0, menu_rect.width, 50),
            container=self.panel,
            manager=manager,
            anchors={"top_target": self.modifier_label},
            options_list=["None", "Sharp", "Flat", "DoubleSharp", "DoubleFlat"],
            starting_option="None",)

        self.duration_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, menu_rect.width, 50),
            container=self.panel,
            manager=manager,
            anchors={"top_target": self.modifier_selector},
            text="Note Duration:",)
        self.duration_selector = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(0, 0, menu_rect.width, 50),
            container=self.panel,
            manager=manager,
            start_value=0,
            anchors={"top_target": self.duration_label},
            value_range=(0, 32),)
        
        self.save_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, -50, menu_rect.width, 50),
            container=self.panel,
            manager=manager,
            anchors={'bottom': 'bottom'},
            text="Save")
        
        self.selected = None
    
    def set_selected(self, note: Note):
        self.selected = note
        if note:
            # set pitch selector
            self.pitch_selector.selected_option = note.name
            self.pitch_selector.current_state.selected_option = note.name
            self.pitch_selector.current_state.start()

            # set duration selector
            self.duration_selector.set_current_value(note.duration * 32)
            self.update()
    
    def update(self):
        duration_text = music.display_duration(self.duration_selector.current_value / 32)
        self.duration_label.set_text(f"Note Duration: {duration_text}")

    def process_event(self, event):
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.duration_selector:
                self.update()
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if self.selected:
                self.selected.update(
                    self.pitch_selector.selected_option, 
                    self.duration_selector.current_value / 32)


