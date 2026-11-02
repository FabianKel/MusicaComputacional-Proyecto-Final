# -*- coding: utf-8 -*-
# SFX: Entregar orden. Resolucion ascendente corta, final brillante.

from javax.sound.midi import (Sequence, MidiSystem, ShortMessage,
                               MidiEvent, MetaMessage)
from java.io import File

PPQ = 480


def add_tempo(track, bpm, start_tick=0):
    mpq = int(round(60000000.0 / bpm))
    data = bytearray(3)
    data[0] = (mpq >> 16) & 0xFF
    data[1] = (mpq >> 8) & 0xFF
    data[2] = mpq & 0xFF
    meta = MetaMessage()
    meta.setMessage(0x51, bytes(data), 3)
    track.add(MidiEvent(meta, start_tick))


def add_program_change(track, channel, program, start_tick=0):
    msg = ShortMessage()
    msg.setMessage(ShortMessage.PROGRAM_CHANGE, channel, program - 1, 0)
    track.add(MidiEvent(msg, start_tick))


def add_note(track, channel, pitch, velocity, start_tick, duration_ticks):
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
    BPM = 132
    seq = Sequence(Sequence.PPQ, PPQ)

    meta = seq.createTrack()
    add_tempo(meta, BPM)

    banjo = seq.createTrack()
    add_program_change(banjo, 0, 106)
    bell = seq.createTrack()
    add_program_change(bell, 1, 15)

    s16 = int(round(PPQ * 0.25))
    notes = [60, 64, 69, 76]
    t = 0
    for i, p in enumerate(notes):
        dur = s16 * 3 if i == len(notes) - 1 else s16
        add_note(banjo, 0, p, 95 + i * 3, t, dur)
        t += s16
    add_note(bell, 1, 76, 100, s16 * 3, s16 * 4)

    total = s16 * 3 + s16 * 4
    write_sequence(seq, "sfx_entregar_orden.mid")
    print("Duracion: %.2fs" % (total * (60.0 / BPM) / PPQ))


if __name__ == '__main__':
    main()
