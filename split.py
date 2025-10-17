# split tracks into each track
import mido

filename = 'asset/songs/lver/lver'
song = mido.MidiFile(f"{filename}.mid")

base = song.tracks[0]
for i, track in enumerate(song.tracks):
    single_track = mido.MidiFile()
    single_track.ticks_per_beat = song.ticks_per_beat
    new_track = single_track.add_track()
    new_track.extend(base)
    new_track = single_track.add_track()
    new_track.extend(track)
    single_track.save(f"{filename}+{i}.mid")

# song = mido.MidiFile(f"{filename}+3.mid")
# song.print_tracks()

# single_track = mido.MidiFile()
# single_track.ticks_per_beat = song.ticks_per_beat
# single_track.add_track().extend(song.tracks[0])
# single_track.add_track().extend(song.tracks[3])
# single_track.add_track().extend(song.tracks[6])
# single_track.save(f"{filename}+cmb.mid")
