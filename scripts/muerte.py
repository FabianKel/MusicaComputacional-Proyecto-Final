# -*- coding: utf-8 -*-
# Muerte: sting final, sin loop. Mismo material armonico pero
# descendente y sin resolver, tempo mas lento, instrumentacion escasa.

from javax.sound.midi import (Sequence, MidiSystem, ShortMessage,
                               MidiEvent, MetaMessage)
from java.io import File

PPQ = 480


def beats_to_ticks(b):
    return int(round(b * PPQ))


def add_track_name(track, name, start_tick=0):
    data = bytearray(name.encode('ascii', 'ignore'))
    meta = MetaMessage()
    meta.setMessage(0x03, bytes(data), len(data))
    track.add(MidiEvent(meta, start_tick))


def add_tempo(track, bpm, start_tick=0):
    mpq = int(round(60000000.0 / bpm))
    data = bytearray(3)
    data[0] = (mpq >> 16) & 0xFF
    data[1] = (mpq >> 8) & 0xFF
    data[2] = mpq & 0xFF
    meta = MetaMessage()
    meta.setMessage(0x51, bytes(data), 3)
    track.add(MidiEvent(meta, start_tick))


def add_time_signature(track, num=4, den=4, start_tick=0):
    import math
    data = bytearray([num, int(round(math.log(den, 2))), 24, 8])
    meta = MetaMessage()
    meta.setMessage(0x58, bytes(data), 4)
    track.add(MidiEvent(meta, start_tick))


def add_program_change(track, channel, program, start_tick=0):
    msg = ShortMessage()
    msg.setMessage(ShortMessage.PROGRAM_CHANGE, channel, program - 1, 0)
    track.add(MidiEvent(msg, start_tick))


def add_note(track, channel, pitch, velocity, start_tick, duration_ticks):
    if pitch is None:
        return
    on = ShortMessage()
    on.setMessage(ShortMessage.NOTE_ON, channel, pitch, velocity)
    track.add(MidiEvent(on, int(start_tick)))
    off = ShortMessage()
    off.setMessage(ShortMessage.NOTE_OFF, channel, pitch, 0)
    track.add(MidiEvent(off, int(start_tick + duration_ticks)))


def write_sequence(seq, filename):
    MidiSystem.write(seq, 1, File(filename))
    print("Escrito: %s" % filename)


def main():
    BPM = 70
    seq = Sequence(Sequence.PPQ, PPQ)

    meta = seq.createTrack()
    add_track_name(meta, "Muerte - tempo")
    add_tempo(meta, BPM)
    add_time_signature(meta, 4, 4)

    banjo = seq.createTrack()
    add_track_name(banjo, "Banjo - descenso")
    add_program_change(banjo, 0, 106)

    bass = seq.createTrack()
    add_track_name(bass, "Contrabajo - raices")
    add_program_change(bass, 2, 33)

    trumpet = seq.createTrack()
    add_track_name(trumpet, "Trompeta con sordina - tension final")
    add_program_change(trumpet, 3, 60)

    bar_ticks = beats_to_ticks(4.0)
    half = beats_to_ticks(2.0)

    bass_roots = [45, 40, 38, 45]
    banjo_notes = [69, 64, 60, 57]

    cursor = 0
    for i in range(4):
        t = cursor
        add_note(bass, 2, bass_roots[i], 80, t, bar_ticks)
        add_note(banjo, 0, banjo_notes[i], 85 - i * 8, t, half)
        cursor += bar_ticks

    add_note(trumpet, 3, 62, 55, cursor - bar_ticks, bar_ticks * 2)
    cursor += bar_ticks

    write_sequence(seq, "baking_bad_muerte.mid")
    print("Duracion: %.2fs" % (cursor * 60.0 / BPM / PPQ))


if __name__ == '__main__':
    main()
