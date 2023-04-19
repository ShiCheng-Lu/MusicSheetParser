import pygame
import os
from common.music import Note, Music, PITCH_MAP
import time
import keyboard

pygame.init()
pygame.mixer.set_num_channels(50)

class PianoPlayer:
    def __init__(self, dir="asset/notes"):
        self.notes: dict[str, pygame.mixer.Sound] = {}

        for file in os.listdir(dir):
            note = file.split(".")[0]
            self.notes[note] = pygame.mixer.Sound(f"{dir}/{file}")

    def playNote(self, note: Note, bpm: int):
        if note.pitch == None: # rest
            return
        self.notes[PITCH_MAP[note.pitch]].play(0, int(note.duration * 240000 / bpm))

    def play(self, music: Music):
        current_time = 0
        
        notes = sorted(music.notes, key=lambda note: note.start_time)

        for note in notes:
            if note.start_time > current_time:
                time.sleep((note.start_time - current_time) * 240 / music.bpm)
                current_time = note.start_time
            self.playNote(note, music.bpm)

keyMap = {

}

class GenshinPlayer:
    def __init__(self):
        pass
    def play(self, music: Music):
        keyboard.wait('p') # wait for p to be pressed

def main():
    # test, play some notes
    player = PianoPlayer()

    m = Music()
    m.bpm = 32
    m.notes = [Note(i, 1, (i + 50) * 8) for i in range(-48, 39)]
    player.play(m)

if __name__ == "__main__":
    main()
