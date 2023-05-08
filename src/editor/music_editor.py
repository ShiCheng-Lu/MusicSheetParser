import pygame
import pygame_gui
import player.music
from player.piano_player import PianoPlayer

width = 180


class MusicEditorMenu(pygame_gui.elements.UIPanel):
    def __init__(self, manager, parent):
        super().__init__(relative_rect=pygame.Rect(900, 0, 180, 860))
        self.parent = parent
        self.manager = manager

        self.file_dialogue = pygame_gui.windows.UIFileDialog(
            pygame.Rect(0, 0, 500, 500),
            manager=self.manager, 
            visible=0)
        self.file_dialogue.draggable = False
        self.open_file_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, width, 50),
            container=self,
            manager=manager,
            text="Load File")

        self.time_sig_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, width, 50),
            container=self,
            manager=manager,
            anchors={'top_target': self.open_file_button},
            text=f"Time Signature:",)
        self.time_sig = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(0, 0, width, 50),
            container=self,
            manager=manager,
            anchors={'top_target': self.time_sig_label},)

        self.play_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, width, 50),
            container=self,
            manager=manager,
            anchors={'top_target': self.time_sig},
            text="Play")

        self.save_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, -50, width, 50),
            container=self,
            manager=manager,
            anchors={'bottom': 'bottom'},
            text="Save")

        self.playable = None

    def set_selected(self, music):
        self.selected = music
        self.time_sig.set_text(f"{music.time_sig[0]}/{music.time_sig[1]}")

    def process_event(self, event: pygame.event.Event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.play_button:
                if self.playable == None or not self.playable.playing:
                    self.playable = player.music.Music(self.selected)
                    self.playable.play(PianoPlayer())
                else:
                    self.playable.stop()

            if event.ui_element == self.open_file_button:
                if self.file_dialogue.alive():
                    self.file_dialogue.show()
                else:
                    self.file_dialogue = pygame_gui.windows.UIFileDialog(
                        pygame.Rect(0, 0, 500, 500),
                        manager=self.manager)
                self.file_dialogue.draggable = False

            if event.ui_object_id == '#file_dialog.#ok_button':
                # selected file
                path: str = self.file_dialogue.current_file_path
                if path.endswith('.json'):
                    # load json
                    pass
                if path.endswith(['.png', '.jpeg', '.jpg']):
                    # detect image
                    pass
        
        if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            if event.ui_element == self.time_sig:
                try:
                    num = int(event.text.split("/")[0])
                    den = int(event.text.split("/")[1])

                    self.selected.time_sig = [num, den]
                except:
                    pass