# -*- coding: utf-8 -*-
# Fragmento de Transicion: puente corto de 2 compases, mismo tempo
# que Normal, para conectar estados (cuantizable a compas).

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


def add_chord(track, channel, pitches, velocity, start_tick, duration_ticks):
    for p in pitches:
        add_note(track, channel, p, velocity, start_tick, duration_ticks)


def write_sequence(seq, filename):
    MidiSystem.write(seq, 1, File(filename))
    print("Escrito: %s" % filename)


def main():
    BPM = 132
    seq = Sequence(Sequence.PPQ, PPQ)

    meta = seq.createTrack()
    add_track_name(meta, "Transicion - tempo")
    add_tempo(meta, BPM)
    add_time_signature(meta, 4, 4)

    banjo = seq.createTrack()
    add_track_name(banjo, "Banjo - run")
    add_program_change(banjo, 0, 106)

    bass = seq.createTrack()
    add_track_name(bass, "Contrabajo")
    add_program_change(bass, 2, 33)

    perc = seq.createTrack()
    add_track_name(perc, "Percusion - fill")

    s16 = beats_to_ticks(0.25)
    q = beats_to_ticks(1.0)

    run = [57, 60, 64, 69, 72, 76, 81, 84, 81, 76, 72, 69, 64, 60, 57, 60]
    cursor = 0
    for i, p in enumerate(run):
        add_note(banjo, 0, p, 70 + i * 2, cursor, s16)
        cursor += s16

    add_note(bass, 2, 45, 90, 0, q * 4)
    add_note(bass, 2, 57, 100, q * 4, q * 4)

    for b in range(4):
        add_note(perc, 9, 76, 65 + b * 8, b * q, q)
    for b in range(4):
        add_note(perc, 9, 36, 100, q * 4 + b * q, q)

    cursor = beats_to_ticks(8.0)
    write_sequence(seq, "baking_bad_transicion.mid")
    print("Duracion: %.2fs" % (cursor * 60.0 / BPM / PPQ))


if __name__ == '__main__':
    main()
