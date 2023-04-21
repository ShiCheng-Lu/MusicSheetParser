import pygame
import os
import common.music
import time
import keyboard
import json
from player.music import Music, MusicPlayer

pygame.init()
pygame.mixer.set_num_channels(50)

class PianoPlayer(MusicPlayer):
    def __init__(self):
        super().__init__()
        self.notes: dict[str, pygame.mixer.Sound] = {}

        for file in os.listdir("asset/notes"):
            note = file.split(".")[0]
            self.notes[note] = pygame.mixer.Sound(f"asset/notes/{file}")

    def play(self, semitone: int, duration):
        tone = common.music.SEMITONE_MAP[semitone]
        self.notes[tone].play(0, int(duration * 240000 / self.bpm))
        # print(tone)


def main():
    with open(f"test.json") as f:
        music = common.music.Music().from_dict(json.load(f))
    music = Music(music)
    player = PianoPlayer()

    music.play(player)

if __name__ == "__main__":
    main()
