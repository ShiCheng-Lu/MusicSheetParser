import pygame
import os
import common.music
import time
import keyboard
import json
from player.music import Music, MusicPlayer

pygame.init()
pygame.mixer.set_num_channels(50)

# class Note(common.music.Note):
#     def __init__(self, note: common.music.Note, parent_bar):
#         note.copy(self)

# class Bar(common.music.Bar):
#     def __init__(self, bar: common.music.Bar):
#         bar.copy(self)
#         self.notes: list[Note] = [Note(note, self) for note in self.notes]

# class Staff(common.music.Staff):
#     def __init__(self, staff: common.music.Staff):
#         staff.copy(self)
#         self.bars: list[Bar] = [Bar(bar) for bar in self.bars]

# class Music(common.music.Music):
#     def __init__(self, music: common.music.Music):
#         music.copy(self)
#         self.staffs: list[Staff] = [Staff(staff) for staff in self.staffs]


# class PianoPlayer(player.music.MusicPlayer):
#     def __init__(self, dir="asset/notes"):
#         self.notes: dict[str, pygame.mixer.Sound] = {}

#         for file in os.listdir(dir):
#             note = file.split(".")[0]
#             self.notes[note] = pygame.mixer.Sound(f"{dir}/{file}")

#     def play(self, semitone: int, duration: int):
#         if note.pitch == None: # rest
#             return
#         self.notes[TONE_MAP[note.semitone]].play(0, int(duration * 240000 / bpm))

#     def playBar(self, bar: Bar):


#     def play(self, music: Music):
#         current_time = 0
        
#         notes = sorted(music.notes, key=lambda note: note.start_time)

#         for note in notes:
#             if note.start_time > current_time:
#                 time.sleep((note.start_time - current_time) * 240 / music.bpm)
#                 current_time = note.start_time
#             self.playNote(note, music.bpm)

# keyMap = {

# }

# class GenshinPlayer:
#     def __init__(self):
#         pass
#     def play(self, music: Music):
#         keyboard.wait('p') # wait for p to be pressed

class PianoPlayer(MusicPlayer):
    def __init__(self):
        super().__init__()
        self.notes: dict[str, pygame.mixer.Sound] = {}

        for file in os.listdir("asset/notes"):
            note = file.split(".")[0]
            self.notes[note] = pygame.mixer.Sound(f"asset/notes/{file}")

    def play(self, semitone: int, duration):
        tone = common.music.TONE_MAP[semitone]
        self.notes[tone].play(0, int(duration * 240000 / self.bpm))


def main():
    with open(f"test2.json") as f:
        music = common.music.Music().from_dict(json.load(f))
    music = Music(music)
    player = PianoPlayer()

    music.play(player)

if __name__ == "__main__":
    main()
