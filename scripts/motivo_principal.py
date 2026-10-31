# -*- coding: utf-8 -*-
# Motivo Principal: presentacion aislada del tema (sin loop, con
# cadencia final). Normal y Persecucion transforman este mismo material.

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


# La menor, con Sol# (3ra de Mi7) como unica alteracion.
CHORDS = {
    'Am': [57, 60, 64],
    'Dm': [50, 53, 57],
    'E7': [52, 56, 59, 62],
}
BASS_ROOT = {'Am': 45, 'Dm': 38, 'E7': 40}
CELLS = {
    'Am_1':   [69, 72, 76, 72, 69, None, 76, None],
    'Dm_1':   [74, 77, 81, 77, 74, None, 69, None],
    'E7_1':   [64, 68, 71, 74, 64, None, 71, None],
    'Am_arp': [69, 72, 76, 81, 76, 72, 69, None],
}


def main():
    BPM = 132
    seq = Sequence(Sequence.PPQ, PPQ)

    meta = seq.createTrack()
    add_track_name(meta, "Motivo Principal - tempo")
    add_tempo(meta, BPM)
    add_time_signature(meta, 4, 4)

    banjo = seq.createTrack()
    add_track_name(banjo, "Banjo - motivo")
    add_program_change(banjo, 0, 106)

    guitar = seq.createTrack()
    add_track_name(guitar, "Guitarra - acompanamiento")
    add_program_change(guitar, 1, 25)

    bass = seq.createTrack()
    add_track_name(bass, "Contrabajo - raices")
    add_program_change(bass, 2, 33)

    bar_ticks = beats_to_ticks(4.0)
    e = beats_to_ticks(0.5)

    progression = ['Am', 'Dm', 'E7', 'Am']
    cells = [CELLS['Am_1'], CELLS['Dm_1'], CELLS['E7_1'], CELLS['Am_arp']]

    cursor = 0
    for i, chord_name in enumerate(progression):
        t = cursor
        add_chord(guitar, 1, CHORDS[chord_name], 55, t, bar_ticks)
        add_note(bass, 2, BASS_ROOT[chord_name], 85, t, bar_ticks)
        for j, p in enumerate(cells[i]):
            add_note(banjo, 0, p, 100, t + j * e, e)
        cursor += bar_ticks

    # cadencia final, Am sostenido
    t = cursor
    add_chord(guitar, 1, CHORDS['Am'], 60, t, bar_ticks)
    add_note(bass, 2, BASS_ROOT['Am'], 90, t, bar_ticks)
    add_note(banjo, 0, 69, 105, t, beats_to_ticks(2.0))
    add_note(banjo, 0, 76, 100, t + beats_to_ticks(2.0), beats_to_ticks(2.0))
    cursor += bar_ticks

    write_sequence(seq, "baking_bad_motivo_principal.mid")
    print("Duracion: %.2fs" % (cursor * 60.0 / BPM / PPQ))


if __name__ == '__main__':
    main()
