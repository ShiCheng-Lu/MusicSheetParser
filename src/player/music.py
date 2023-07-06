import common.music
import time
import threading

class MusicPlayer:
    '''
    MusicPlayer: base class
    '''
    def __init__(self, bpm=None):
        self.bpm = 80

    def play(self, semitone, duration):
        pass
    
    def wait(self, duration):
        time.sleep(duration * 240 / self.bpm)
    
    def start(self, music):
        pass

class Note(common.music.Note):
    def __init__(self, note: common.music.Note):
        note.copy(self)
    
    def play(self, player: MusicPlayer):
        '''
        play the note with the player
        '''
        if 'rest' not in self.name:
            player.play(self.semitone, self.duration)
        return self.duration

class Bar(common.music.Bar):
    def __init__(self, bar: common.music.Bar):
        bar.copy(self)
        self.notes: list[Note] = [Note(note) for note in self.notes]
        self.notes.sort(key=lambda x: x.x_min)

        self.notes_iter = iter(self.notes)
        self.current_note = next(self.notes_iter, None)

        self.current_time = 0
        self.next_note_time = 0

    def play(self, delta, player):
        '''
        play a section of the bar with the player

        returns how long the bar played for, then the caller should wait that time then call play again to play the next notes.
        returns 0 if there are no more notes to play
        '''
        if self.current_note == None:
            return 0
        # self.next_note_time -= delta
        # if self.next_note_time <= 0:

        # play note group
        group_x_end = self.current_note.x_max
        duration = 0
        while self.current_note != None and self.current_note.x_min < group_x_end:
            self.current_note.play(player)
            duration = max(duration, self.current_note.duration)
            group_x_end = self.current_note.x_max

            self.current_note = next(self.notes_iter, None)
        
        return duration
        # self.next_note_time += duration
        # return self.next_note_time

class Staff(common.music.Staff):
    def __init__(self, staff: common.music.Staff, parent):
        staff.copy(self)
        self.bars: list[Bar] = [Bar(bar) for bar in self.bars]
        self.parent = parent
    
    def play(self, player: MusicPlayer):
        for bar in self.bars:
            self.parent.bar_sem.wait()
            if self.parent.stop_event.is_set():
                return

            duration = bar.play(0, player)
            player.wait(duration)
            while duration != 0:
                duration = bar.play(0, player)
                player.wait(duration)

    def reset(self):
        for bar in self.bars:
            bar.reset()

class Music(common.music.Music):
    def __init__(self, music: common.music.Music):
        music.copy(self)
        self.staffs: list[Staff] = [Staff(staff, self) for staff in self.staffs]

        self.bar_sem = threading.Barrier(self.group)
        self.staff_sem = threading.Barrier(self.group)

        self.stop_event = threading.Event()

        self.playing_threads: list[threading.Thread] = []
    
    @property
    def playing(self):
        return not self.stop_event.is_set()
    
    def play_staffs(self, staffs, player):
        for staff in staffs:
            self.staff_sem.wait()
            staff.play(player)

    def play(self, player: MusicPlayer):
        self.stop_event.clear()
        player.start(self)
        staff_groups = [[] for _ in range(self.group)]
        for index, staff in enumerate(self.staffs):
            staff_groups[index % self.group].append(staff)
        for staffs in staff_groups:
            thread = threading.Thread(target=self.play_staffs, args=(staffs, player))
            self.playing_threads.append(thread)
        for thread in self.playing_threads:
            thread.start()

    def stop(self):
        self.stop_event.set()
        for thread in self.playing_threads:
            thread.join()
