import io

# def write_varint(num):
#     result = []
#     while (num >= 0x80):
#         result.append(num & 0x7f | 0x80)
#         num = num >> 7
#     result.append(num & 0x7f | 0x80)
#     result[0] ^= 0x80
#     result.reverse()
#     return list(map(lambda x: f"{x:0<2x}", result))

class TrackStream(io.BufferedReader):
    def __init__(self, stream, size):
        self.stream = stream
        self.size = size
    def read(self, len):
        if len > self.size:
            return None
        else:
            self.size -= len
            return self.stream.read(len)
    def peek(self, len):
        return self.stream.peek(len)

def read_varint(file: io.BufferedReader):
    byte = int.from_bytes(file.read(1), 'big')
    num = 0
    while (byte & 0x80):
        num = (num << 7) | (byte & 0x7f)
        byte = int.from_bytes(file.read(1), 'big')
    return num + byte

def read_int(file: io.BufferedReader, bytes):
    return int.from_bytes(file.read(bytes), 'big')

def read_chunk(file: io.BufferedReader):
    # 4 character ASCII type
    chunk_type = file.read(4)
    # 32-bit length
    chunk_length = read_int(file, 4)

    match chunk_type:
        case b'MThd':
            assert(chunk_length == 6)

            format = read_int(file, 2)
            ntrks = read_int(file, 2)
            division = read_int(file, 2)

            print(format, ntrks, division)
        case b'MTrk':
            track_stream = TrackStream(file, chunk_length)
            while track_stream.size > 0:
                read_event(track_stream)

total_time = 0
def read_event(file: io.BufferedReader):
    global total_time

    delta_time = read_varint(file)
    total_time += delta_time

    event = int.from_bytes(file.read(1), 'big')
    
    print(f"e: {total_time} {event:02x} ", end="")

    match event:
        # sysex event
        case 0xf0:
            len = read_varint(file)
            data = file.read(len)
            print(f"sysex event: {len} {data}")
        case 0xf7:
            len = read_varint(file)
            data = file.read(len)
            print(f"sysex event: {len} {data}")

        # meta-event
        case 0xff:
            read_meta_event(file)

        # MIDI event
        case 0xd7:
            description = file.read(1)
            while description != 0xd0:
                print(description, end="")
                description = file.read(1)
            
        case _:
            read_midi_event(event, file)

last_event = None
def read_midi_event(type: int, file: io.BufferedReader):
    # https://drive.google.com/file/d/1Px1QBHL9YyhhS9BE7EEn0qR8fE1ezgSC/view
    global last_event
    if (type & 0x80 == 0):
        # running status
        type = last_event
    else:
        last_event = type

    match (type >> 4, type & 0b1111):
        case (0b1000, chan): # note off
            key = read_int(file, 1)
            vel = read_int(file, 1)
            print(f"note off: {chan} {key} {vel}")
        case (0b1001, chan): # note on
            key = read_int(file, 1)
            vel = read_int(file, 1)
            print(f"note on: {chan} {key} {vel}")
        case (0b1010, chan): # polyphonic key pressure
            key = read_int(file, 1)
            pressure = read_int(file, 1)
            print(f"polyphonic: {chan} {key} {pressure}")
        case (0b1011, chan): # control change
            number = read_int(file, 1)
            value = read_int(file, 1)
            print(f"control change: {chan} {number} {value}")
        case (0b1100, chan): # program change
            program = read_int(file, 1)
            print(f"program change: {chan} {program}")
        case (0b1101, chan): # channel pressure
            pressure = read_int(file, 1)
            print(f"pressure change: {chan} {pressure}")
        case (0b1110, chan): # pitch bend change
            l = read_int(file, 1)
            m = read_int(file, 1)
            bend = m << 7 | l
            print(f"pitch bend: {chan} {bend}")
        case (0b1011, chan): # channel mode messages
            number = read_int(file, 1)
            value = read_int(file, 1)
            print(f"channel mode: {chan} {number} {value}")
        case (0b1111, 0b0000): # system exclusive
            print("system exclusive")
        case (0b1111, 0b0001): # MIDI time code quarter frame
            v = read_int(file, 1)
            msg_type = v >> 4
            values = v & 0xf
            print(f"quarter frame: {msg_type} {values}")
        case (0b1111, 0b0010): # song position pointer
            l = read_int(file, 1)
            m = read_int(file, 1)
            pointer = m << 7 | l
            print(f"song position: {pointer}")
        case (0b1111, 0b0011): # song select
            song = read_int(file, 1)
            print(f"song select: {song}")
        case (0b1111, 0b0100): # reserved
            print("reserved")
        case (0b1111, 0b0101): # reserved
            print("reserved")
        case (0b1111, 0b0110): # tune request
            print("tune request")
        case (0b1111, 0b0111): # end of exclusive
            print("end of exclusive")
        # system real time messages
        case (0b1111, 0b1000): # timing clock
            print("clock")
        case (0b1111, 0b1001): # reserved
            print("reserved")
        case (0b1111, 0b1010): # start
            print("start")
        case (0b1111, 0b1011): # continue
            print("continue")
        case (0b1111, 0b1100): # stop
            print("stop")
        case (0b1111, 0b1101): # reserved
            print("reserved")
        case (0b1111, 0b1110): # active sensing
            print("active sensing")
        case (0b1111, 0b1111): # reset
            print("reset")

def read_meta_event(file: io.BufferedReader):
    # https://drive.google.com/file/d/1t4jcCCKoi5HMi7YJ6skvZfKcefLhhOgU/view
    type = read_int(file, 1)
    len = read_varint(file)
    data = file.read(len)

    match type:
        case 0x00: # sequence number
            assert(len == 0x02)
            ssss = data
            print(f"sequence number {ssss}")
        case 0x01: # text event
            text = data
            print('text event', text)
        case 0x02: # copyright notice
            text = data
            print('copyright notice', text)
        case 0x03: # sequence/track name
            text = data
            print('seqeunce name', text)
        case 0x04: # instrument name
            text = data
            print(f"instrument name {text}")
        case 0x05: # lyric
            text = data
            print(f"lyric {text}")
        case 0x06: # marker
            text = data
            print(f"marker {text}")
        case 0x07: # cue point
            text = data
            print(f"cue point {text}")
        case 0x20: # midi channel prefix
            assert(len == 0x01)
            cc = data
            print(f"midi channel prefix {cc}")
        case 0x2f: # end of track
            assert(len == 0x00)
        case 0x51: # set tempo
            assert(len == 0x03)
            tttttt = data
        case 0x54: # smpte offset
            assert(len == 0x05)
            hr = data[0]
            mn = data[1]
            se = data[2]
            fr = data[3]
            ff = data[4]
        case 0x58: # time signature
            assert(len == 0x04)
            nn = data[0]
            dd = data[0]
            cc = data[0]
            bb = data[0]
        case 0x59: # key signature
            assert(len == 0x02)
            sf = data[0]
            mi = data[0]
        case 0x7f: # sequencer-sepecific meta-event
            pass
        case _:
            print(f"unknown meta event: {type} {len}")

class Midi:

    format = 0
    ntrks = 1
    division = 0

    class Event:
        
        pass

    def __init__(self):
        pass


if __name__ == "__main__":

    with open("./iwitw.mid", "rb") as f:
        read_chunk(f)
        print("NEW CHUNK")
        total_time = 0
        read_chunk(f)
        print("NEW CHUNK")
        total_time = 0
        read_chunk(f)
        print("NEW CHUNK")
        # while f.peek(1):
        #     read_chunk(f)
        #     total_time = 0
        #     print("NEW CHUNK")
        
    pass
