import common.music
import pygame_gui
import pygame
import editor.pygame_utils
from editor.note_editor import Note
from common.label import Bbox

width = 180
menu = None


class Bar(common.music.Bar):
    def __init__(self, bar: common.music.Bar, parent_staff):
        bar.copy(self)
        self.parent_staff = parent_staff
        self.notes: list[Note] = [Note(note, self) for note in self.notes]

        self.valid = False
        self.validate()

    def validate(self):
        duration = 0
        target_duration = self.parent_staff.parent_music.time_sig_duration

        group_duration = 0
        group_x_end = 0
        for note in sorted(self.notes, key=lambda x: x.x_min):
            if note.x_min > group_x_end:
                # new group
                duration += group_duration
                group_x_end = note.x_max
                group_duration = note.duration
            else:
                group_duration = max(group_duration, note.duration)
                group_x_end = max(group_x_end, note.x_max)
        duration += group_duration

        self.valid = duration % target_duration == 0

    def render(self, screen, selected):
        for note in self.notes:
            note.render(screen, selected)
        
        # don't outline if its valid
        if self.valid and selected != self:
            return

        thickness = 3
        if selected == self:
            color = (100, 100, 100)
        else:
            color = (200, 25, 25)
        rect = editor.pygame_utils.to_pygame_rect(self)
        pygame.draw.rect(screen, color, rect, thickness)
    
    def delete_note(self, note):
        if note in self.notes:
            self.notes.remove(note)
    
    def select(self, x, y):
        for note in self.notes:
            if result := note.select(x, y):
                return result
        if self.contains(x, y):
            return self

class BarEditorMenu(pygame_gui.elements.UIPanel):
    def __init__(self, manager, parent) -> None:
        super().__init__(relative_rect=pygame.Rect(900, 0, 180, 860))
        self.parent = parent
        self.add_note_pos = (0, 0)

        self.duration_selector = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, width, 50),
            container=self,
            manager=manager,
            text="Bar Duration")
        self.add_note_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, width, 50),
            container=self,
            manager=manager,
            anchors={"top_target": self.duration_selector},
            text="Add Note")

    def set_selected(self, bar: Bar):
        self.selected = bar

    def process_event(self, event: pygame.event.Event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.add_note_button:
                size = self.selected.parent_staff.height / 8
                new_note = common.music.Note([
                    self.add_note_pos[0] - size,
                    self.add_note_pos[1] - size,
                    self.add_note_pos[0] + size,
                    self.add_note_pos[1] + size,
                    ], 'customNote')
                self.selected.notes.append(Note(new_note, self.selected))

                self.parent()



