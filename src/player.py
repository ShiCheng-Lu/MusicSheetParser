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

vintageLyre = {
      3: 'Q',   4: 'W',   6: 'E',   8: 'R',  10: 'T',  11: 'Y',  13: 'U', 
     -9: 'A',  -7: 'S',  -6: 'D',  -4: 'F',  -2: 'G',   0: 'H',   1: 'J',
    -21: 'Z', -19: 'X', -18: 'C', -16: 'V', -14: 'B', -12: 'N', -11: 'M', 
}

standard = {
      3: 'q',   5: 'w',   7: 'e',   8: 'r',  10: 't',  12: 'y',  14: 'u', 
     -9: 'a',  -7: 's',  -5: 'd',  -4: 'f',  -2: 'g',   0: 'h',   2: 'j',
    -21: 'z', -19: 'x', -17: 'c', -16: 'v', -14: 'b', -12: 'n', -10: 'm', 
}

class GenshinPlayer(MusicPlayer):
    def __init__(self):
        super().__init__()
    
    def play(self, semitone: int, duration):
        key = standard.get(semitone, None)
        if key != None:
            keyboard.press_and_release(key)
    
    def start(self, music):
        keyboard.wait('P')

def main():
    with open(f"test.json") as f:
        music = common.music.Music().from_dict(json.load(f))
    music = Music(music)
    player = GenshinPlayer()

    music.play(player)

if __name__ == "__main__":
    main()