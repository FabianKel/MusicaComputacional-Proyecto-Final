# -*- coding: utf-8 -*-
# SFX: Cocinar pastel. Textura ritmica corta (revuelto/horneado).

from javax.sound.midi import (Sequence, MidiSystem, ShortMessage,
                               MidiEvent, MetaMessage)
from java.io import File

PPQ = 480
LO_WOOD_BLOCK = 77
HI_WOOD_BLOCK = 76


def add_tempo(track, bpm, start_tick=0):
    mpq = int(round(60000000.0 / bpm))
    data = bytearray(3)
    data[0] = (mpq >> 16) & 0xFF
    data[1] = (mpq >> 8) & 0xFF
    data[2] = mpq & 0xFF
    meta = MetaMessage()
    meta.setMessage(0x51, bytes(data), 3)
    track.add(MidiEvent(meta, start_tick))


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

    perc = seq.createTrack()

    s16 = int(round(PPQ * 0.25))
    toggle = True
    t = 0
    for i in range(10):
        block = HI_WOOD_BLOCK if toggle else LO_WOOD_BLOCK
        vel = 50 + (i % 3) * 10
        add_note(perc, 9, block, vel, t, s16)
        toggle = not toggle
        t += s16

    write_sequence(seq, "sfx_cocinar_pastel.mid")
    print("Duracion: %.2fs" % (t * (60.0 / BPM) / PPQ))


if __name__ == '__main__':
    main()
