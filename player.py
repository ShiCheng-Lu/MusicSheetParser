import pygame
import os
from music import Note, Music
import time
import math

pygame.init()
pygame.mixer.set_num_channels(50)

class PianoPlayer:
    def __init__(self, dir = "asset/notes"):
        self.notes: dict[str, pygame.mixer.Sound] = {}
        
        for file in os.listdir(dir):
            note =file.split(".")[0]
            self.notes[note] = pygame.mixer.Sound(f"{dir}/{file}")

    def playNote(self, note: Note, duration: int):
        for pitch in note.pitches:
            self.notes[pitch].play(0, duration)

    def play(self, music: Music):
        trackCount = len(music.tracks)
        
        nextNoteTime = [0] * trackCount
        noteIndexes = [0] * trackCount

        # startTime = time.time()
        # playTime = startTime

        while any([math.isinf(x) for x in nextNoteTime]):
            for i in range(trackCount):
                if nextNoteTime[i] == 0:
                    try:
                        note = music.tracks[i][noteIndexes[i]]
                        self.playNote(note, note.duration * music.time)
                        nextNoteTime[i] = note.duration
                        noteIndexes[i] += 1
                    except IndexError:
                        nextNoteTime[i] =  math.inf
            
            timeStep = min(nextNoteTime)
            for i in range(trackCount):
                nextNoteTime[i] -= timeStep
            
            time.sleep(timeStep / 1000 * music.time)

def note(str):
    return Note([str], 250)

def main():
    # test, play some notes
    player = PianoPlayer()

    # player.play([
    #     note("A3"),
    #     note("B3"),
    #     note("C4"),
    #     note("D4"),
    #     note("E4"),
    #     note("F4"),
    #     note("G4"),
    #     note("G4"),
    #     note("G4"),
    #     note("G4"),
    #     note("G4"),
    #     note("G4"),
    #     note("G4"),
    #     note("G4"),
    # ])

    player.play([Note([pitchMap[i]], 200) for i in range(-22, 46)])

if __name__ == "__main__":
    main()