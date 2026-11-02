# -*- coding: utf-8 -*-
# Peligro: variacion del Motivo Principal, mismo tempo que Normal,
# arpegio continuo en campana aguda (urgencia sin acelerar el pulso).
# 3 capas: BAJA = bajo+pulso, MEDIA = +guitarra, ALTA = +arpegio+trompeta.

from javax.sound.midi import (Sequence, MidiSystem, ShortMessage,
                               MidiEvent, MetaMessage)
from java.io import File

PPQ = 480
SIDE_STICK = 37
TAMBOURINE = 54


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


CHORDS = {'Am': [57, 60, 64], 'Dm': [50, 53, 57], 'E7': [52, 56, 59, 62]}
BASS_ROOT = {'Am': 45, 'Dm': 38, 'E7': 40}
ARP_CELLS = {
    'Am': [69, 72, 76, 81, 76, 72, 69, 64, 69, 72, 76, 81, 76, 72, 69, 64],
    'Dm': [74, 77, 81, 86, 81, 77, 74, 69, 74, 77, 81, 86, 81, 77, 74, 69],
    'E7': [68, 71, 74, 79, 74, 71, 68, 64, 68, 71, 74, 79, 74, 71, 68, 64],
}


def main():
    BPM = 132
    seq = Sequence(Sequence.PPQ, PPQ)

    meta = seq.createTrack()
    add_track_name(meta, "Peligro - tempo")
    add_tempo(meta, BPM)
    add_time_signature(meta, 4, 4)

    arp = seq.createTrack()
    add_track_name(arp, "CAPA ALTA - Campana (arpegio)")
    add_program_change(arp, 0, 10)

    guitar = seq.createTrack()
    add_track_name(guitar, "CAPA MEDIA - Guitarra acustica")
    add_program_change(guitar, 1, 25)

    bass = seq.createTrack()
    add_track_name(bass, "CAPA BAJA - Contrabajo")
    add_program_change(bass, 2, 33)

    trumpet = seq.createTrack()
    add_track_name(trumpet, "CAPA ALTA - Trompeta con sordina")
    add_program_change(trumpet, 3, 60)

    perc = seq.createTrack()
    add_track_name(perc, "CAPA BAJA - Pulso")

    bar_ticks = beats_to_ticks(4.0)
    q = beats_to_ticks(1.0)
    s16 = beats_to_ticks(0.25)

    progression = ['Am', 'Dm', 'E7', 'Am', 'Am', 'Dm', 'E7', 'Am']

    def bass_pulse(chord_name, start_tick):
        root = BASS_ROOT[chord_name]
        add_note(bass, 2, root, 95, start_tick, q * 2)
        add_note(bass, 2, root + 7, 85, start_tick + q * 2, q * 2)
        for b in range(4):
            add_note(perc, 9, SIDE_STICK, 60, start_tick + b * q, q)

    def guitar_stab(chord_name, start_tick):
        chord = CHORDS[chord_name]
        dur = beats_to_ticks(0.2)
        add_chord(guitar, 1, chord, 70, start_tick, dur)
        add_chord(guitar, 1, chord, 60, start_tick + beats_to_ticks(2.0), dur)
        add_note(perc, 9, TAMBOURINE, 55, start_tick + beats_to_ticks(1.5), s16)
        add_note(perc, 9, TAMBOURINE, 55, start_tick + beats_to_ticks(3.5), s16)

    def arp_cell(chord_name, start_tick):
        cell = ARP_CELLS[chord_name]
        for j, p in enumerate(cell):
            add_note(arp, 0, p, 100, start_tick + j * s16, s16)

    def trumpet_accent(chord_name, start_tick, i):
        if i % 2 == 1:
            top = CHORDS[chord_name][-1]
            add_note(trumpet, 3, top, 90, start_tick + beats_to_ticks(3.0), beats_to_ticks(1.0))

    cursor = 0
    for i, chord_name in enumerate(progression):
        t = cursor
        bass_pulse(chord_name, t)
        guitar_stab(chord_name, t)
        arp_cell(chord_name, t)
        trumpet_accent(chord_name, t, i)
        cursor += bar_ticks

    total_end = cursor
    write_sequence(seq, "baking_bad_peligro.mid")
    print("Duracion del loop: %.2fs (%d compases)" %
          (total_end * 60.0 / BPM / PPQ, len(progression)))


if __name__ == '__main__':
    main()
