import pygame
import os
from player.music import MusicPlayer

pygame.init()
pygame.mixer.set_num_channels(50)


SEMITONE_MAP = [  # range: -48 to +39 relative to A4
    "A4", "Bb4", "B4", "C5", "Db5", "D5", "Eb5", "E5", "F5", "Gb5", "G5", "Ab5",
    "A5", "Bb5", "B5", "C6", "Db6", "D6", "Eb6", "E6", "F6", "Gb6", "G6", "Ab6",
    "A6", "Bb6", "B6", "C7", "Db7", "D7", "Eb7", "E7", "F7", "Gb7", "G7", "Ab7",
    "A7", "Bb7", "B7",  # missing high C8 on standard piano
    # indexed negatively, these are lower than A4
    "A0", "Bb0", "B0", "C1", "Db1", "D1", "Eb1", "E1", "F1", "Gb1", "G1", "Ab1",
    "A1", "Bb1", "B1", "C2", "Db2", "D2", "Eb2", "E2", "F2", "Gb2", "G2", "Ab2",
    "A2", "Bb2", "B2", "C3", "Db3", "D3", "Eb3", "E3", "F3", "Gb3", "G3", "Ab3",
    "A3", "Bb3", "B3", "C4", "Db4", "D4", "Eb4", "E4", "F4", "Gb4", "G4", "Ab4",
]


class PianoPlayer(MusicPlayer):
    def __init__(self):
        super().__init__()
        self.notes: dict[str, pygame.mixer.Sound] = {}

        for file in os.listdir("asset/notes"):
            note = file.split(".")[0]
            self.notes[note] = pygame.mixer.Sound(f"asset/notes/{file}")

    def play(self, semitone: int, duration):
        tone = SEMITONE_MAP[semitone]
        self.notes[tone].play(0, int(duration * 240000 / self.bpm))
