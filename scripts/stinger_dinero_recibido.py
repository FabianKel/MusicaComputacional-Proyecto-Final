# -*- coding: utf-8 -*-
# Stinger: Dinero recibido. Arpegio ascendente breve y brillante.

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

    bell = seq.createTrack()
    add_program_change(bell, 0, 15)
    banjo = seq.createTrack()
    add_program_change(banjo, 1, 106)

    s16 = int(round(PPQ * 0.25))
    notes = [57, 60, 64, 69, 72]
    t = 0
    for i, p in enumerate(notes):
        dur = s16 * 4 if i == len(notes) - 1 else s16
        add_note(bell, 0, p, 100 + i * 2, t, dur)
        t += s16
    add_note(banjo, 1, 69, 100, 0, s16 * 8)

    total = s16 * 4 + s16 * 4
    write_sequence(seq, "stinger_dinero_recibido.mid")
    print("Duracion: %.2fs" % (total * (60.0 / BPM) / PPQ))


if __name__ == '__main__':
    main()
