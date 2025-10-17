import pydirectinput
import time
import pynput
import mido

import threading
song_thread = None
stop_event = threading.Event()
import tqdm

songs = [
    ("asset/songs/lver/lver+3.mid", 6),
    ("asset/songs/iwitw/iwitw+4.mid", 0),
]
song_index = 0

def play_song():
    global stop
    
    song = mido.MidiFile(songs[song_index][0])

    main_track = None
    note_check = lambda e: (e.time != 0)
    main_track = list(filter(note_check, song.tracks[1]))

    print("Starting track")

    tempo = None
    for event in song.tracks[0]:
        if tempo == None and event.type == "set_tempo":
            tempo = event.tempo / song.ticks_per_beat / 1000000
            break

    lowest_note = 9999
    highest_note = -1
    for event in main_track:
        if (event.type == "note_on"):
            lowest_note = min(lowest_note, event.note)
            highest_note = max(highest_note, event.note)
    print(lowest_note, highest_note)

    note_on = None
    started = False

    for event in tqdm.tqdm(main_track):
        if stop_event.is_set():
            print("Stopping")
            return

        # skips the start with no notes playing
        if started:
            time.sleep(event.time * tempo)
        
        if (event.type == "note_off" or 
            (event.type == "note_on" and event.velocity == 0)):
            # note off
            if note_on == event.note:
                pydirectinput.mouseUp(_pause=False)
                note_on = False
            pass
        elif (event.type == "note_on"):
            note = (event.note - lowest_note + songs[song_index][1])
            if (note > 0 and note < 36):
                if note_on:
                    pydirectinput.mouseUp(_pause=False)

                pydirectinput.moveRel(0, -note * 50, _pause=False)
                pydirectinput.mouseDown(_pause=False)
                note_on = event.note
                # note on
                pass
            started = True
        # print(event)

def cleanup():
    if song_thread != None:
        stop_event.set()
        song_thread.join()
        print("Stopped")
        pydirectinput.mouseUp(_pause=False)
        stop_event.clear()
    
if __name__ == "__main__":
    # wait for key input
    def on_click(x, y, button, pressed):
        if (button == pynput.mouse.Button.x2 and not pressed): # forward button, start
            cleanup()
            song_thread = threading.Thread(target=play_song)
            song_thread.start()
        if (button == pynput.mouse.Button.x2 and pressed): # calibrate, look at feet
            print("Calibrate")
            pydirectinput.moveRel(0, 0, _pause=False)

        # quit
        if (button == pynput.mouse.Button.x1 and pressed): # calibrate, look at feet
            return False
        
    listener = pynput.mouse.Listener(on_click=on_click)
    listener.start()
    listener.join()

    cleanup()
