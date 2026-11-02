import sys
import mido

src = sys.argv[1]
out = sys.argv[2]
keep_channels = set(int(c) for c in sys.argv[3].split(','))

mid = mido.MidiFile(src)
new = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)
for track in mid.tracks:
    nt = mido.MidiTrack()
    carry = 0
    for msg in track:
        if msg.is_meta or not hasattr(msg, 'channel') or msg.channel in keep_channels:
            nt.append(msg.copy(time=msg.time + carry))
            carry = 0
        else:
            carry += msg.time
    new.tracks.append(nt)

new.save(out)
print("ok", out)
