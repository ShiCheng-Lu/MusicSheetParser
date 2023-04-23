import keyboard
from player.music import MusicPlayer

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
