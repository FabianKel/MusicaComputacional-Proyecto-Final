# -*- coding: utf-8 -*-
# Stinger: Detectado. Golpe disonante corto, mismo timbre que
# Peligro/Persecucion, anuncia el cambio de estado.

from javax.sound.midi import (Sequence, MidiSystem, ShortMessage,
                               MidiEvent, MetaMessage)
from java.io import File

PPQ = 480
KICK = 36
HIGH_FLOOR_TOM = 43


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
    add_tempo(meta, BPM)

    trumpet = seq.createTrack()
    add_program_change(trumpet, 0, 60)
    drums = seq.createTrack()

    q = int(round(PPQ * 1.0))
    e = int(round(PPQ * 0.5))

    add_chord(trumpet, 0, [57, 63], 110, 0, e)
    add_note(drums, 9, KICK, 110, 0, e)
    add_note(drums, 9, HIGH_FLOOR_TOM, 100, e, e)

    total = q
    write_sequence(seq, "stinger_detectado.mid")
    print("Duracion: %.2fs" % (total * (60.0 / BPM) / PPQ))


if __name__ == '__main__':
    main()
