import pygame
import common.music
import pygame_gui
from common.label import Bbox
import editor.pygame_utils

pygame.font.init()
font = pygame.font.Font('freesansbold.ttf', 20)

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
MOD_MAP.update({v: k for k, v in MOD_MAP.items()})

w, h = 1080, 860
menu_rect = Bbox([900, 0, 1080, 860])
width = 180


class Note(common.music.Note):
    def __init__(self, note: common.music.Note, parent_bar):
        note.copy(self)
        self.parent_bar = parent_bar

    def render(self, screen, selected):
        thickness = 5

        text = font.render(self.pitch_str, True, (25, 25, 255))

        textRect = text.get_rect()
        textRect.x = self.x_min
        textRect.bottom = self.y_min

        rect = editor.pygame_utils.to_pygame_rect(self)
        rect.width += thickness
        rect.height += thickness

        color = (25, 150, 150) if selected == self else (25, 200, 25)

        pygame.draw.rect(screen, color, rect, thickness)
        screen.blit(text, textRect)

    def update(self, duration, pitch, modifier):
        self.duration: float = duration
        self.pitch: int = pitch
        self.modifier = modifier

        self.parent_bar.validate()
        pass
    
    def select(self, x, y):
        if self.contains(x, y):
            return self

class NoteEditorMenu(pygame_gui.elements.UIPanel):
    def __init__(self, manager, parent):
        super().__init__(relative_rect=pygame.Rect(900, 0, 180, 860))
        self.parent = parent

        self.pitch_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, width, 50),
            container=self,
            manager=manager,
            text="Note Pitch:",)
        self.pitch_selector = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(0, 0, width, 50),
            container=self,
            manager=manager,
            anchors={"top_target": self.pitch_label},
            options_list=common.music.SEMITONE_MAP + ['Rest'],
            starting_option="Rest",)
        
        self.modifier_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, width, 50),
            container=self,
            manager=manager,
            anchors={"top_target": self.pitch_selector},
            text="Note Modifier:",)
        self.modifier_selector = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(0, 0, width, 50),
            container=self,
            manager=manager,
            anchors={"top_target": self.modifier_label},
            options_list=MOD_MAP,
            starting_option="None",)

        self.duration_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, width, 50),
            container=self,
            manager=manager,
            anchors={"top_target": self.modifier_selector},
            text="Note Duration:",)
        self.duration_selector = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(0, 0, width, 50),
            container=self,
            manager=manager,
            start_value=0,
            anchors={"top_target": self.duration_label},
            value_range=(0, 32),)
        
        self.delete_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, width, 50),
            container=self,
            manager=manager,
            anchors={'top_target': self.duration_selector},
            text="Delete Note")
        
        self.save_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, -50, width, 50),
            container=self,
            manager=manager,
            anchors={'bottom': 'bottom'},
            text="Save")
    
    def set_selected(self, note: Note):
        self.selected = note
        if note:
            # set pitch selector
            tone = TONE_MAP[note.pitch + A4_POS]
            if "rest" in note.name:
                tone = "Rest"
            self.pitch_selector.selected_option = tone
            self.pitch_selector.current_state.selected_option = tone
            self.pitch_selector.current_state.start()

            #set modifier selector
            mod = MOD_MAP[note.modifier]
            self.modifier_selector.selected_option = mod
            self.modifier_selector.current_state.selected_option = mod
            self.modifier_selector.current_state.start()

            # set duration selector
            self.duration_selector.set_current_value(note.duration * 32)
            self.update_text()
    
    def update_text(self):
        duration_text = common.music.display_duration(self.duration_selector.current_value / 32)
        self.duration_label.set_text(f"Note Duration: {duration_text}")

    def process_event(self, event: pygame.event.Event):
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.duration_selector:
                self.update_text()
                bar = self.selected.parent_bar
                bar.update_duration(self.selected, event.value / 32)
                bar.validate()
            
            self.parent()
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.delete_button:
                bar = self.selected.parent_bar
                bar.notes.remove(self.selected)
                bar.validate()
            
            if event.ui_element == self.save_button:
                self.selected.update(
                    self.duration_selector.current_value / 32,
                    TONE_MAP.index(self.pitch_selector.selected_option) - A4_POS,
                    MOD_MAP[self.modifier_selector.selected_option])

            self.parent()
