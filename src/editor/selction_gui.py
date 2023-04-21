
import pygame
import pygame_gui
from common.label import Bbox
import common.music
import editor.pygame_utils as pygame_utils
from editor.music import Note, Bar
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

class NoteEditorMenu:
    def __init__(self, manager, music, on_update=None):
        self.music = music
        self.on_update = on_update

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
            options_list=common.music.SEMITONE_MAP,
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
            options_list=MOD_MAP,
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
        
        self.delete_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, menu_rect.width, 50),
            container=self.panel,
            manager=manager,
            anchors={'top_target': self.duration_selector},
            text="Delete Note")
        
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
            tone = TONE_MAP[note.pitch + A4_POS]
            # set pitch selector
            self.pitch_selector.selected_option = tone
            self.pitch_selector.current_state.selected_option = tone
            self.pitch_selector.current_state.start()

            # set duration selector
            self.duration_selector.set_current_value(note.duration * 32)
            self.update()
    
    def update(self):
        duration_text = common.music.display_duration(self.duration_selector.current_value / 32)
        self.duration_label.set_text(f"Note Duration: {duration_text}")

    def process_event(self, event):
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.duration_selector:
                self.update()
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.delete_button and self.selected:
                bar: Bar = self.selected.parent_bar
                bar.delete_note(self.selected)
                bar.validate()
            
            if event.ui_element == self.save_button and self.selected:
                self.selected.update( 
                    self.duration_selector.current_value / 32,
                    TONE_MAP.index(self.pitch_selector.selected_option) - A4_POS,
                    MOD_MAP[self.modifier_selector.selected_option])

            if self.on_update != None:
                self.on_update()
