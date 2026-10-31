# -*- coding: utf-8 -*-
# Normal (Exploracion): loop fijo, sin cambios de tempo. Intro (1 vez)
# + Seccion A + Seccion B, con punto de bucle al final de B.
# 3 capas: BAJA = bajo+bateria, MEDIA = +guitarra, ALTA = +banjo+armonica+trompeta.

from javax.sound.midi import (Sequence, MidiSystem, ShortMessage,
                               MidiEvent, MetaMessage)
from java.io import File

PPQ = 480
KICK = 36
SIDE_STICK = 37
SNARE = 38
TAMBOURINE = 54
HI_WOOD_BLOCK = 76
LO_WOOD_BLOCK = 77


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


CHORDS = {
    'Am': [57, 60, 64], 'Dm': [50, 53, 57], 'E7': [52, 56, 59, 62],
    'F': [53, 57, 60], 'C': [48, 52, 55],
}
BASS_ROOT = {'Am': 45, 'Dm': 38, 'E7': 40, 'F': 41, 'C': 36}
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
    add_track_name(meta, "Normal - tempo")
    add_tempo(meta, BPM)
    add_time_signature(meta, 4, 4)

    banjo = seq.createTrack()
    add_track_name(banjo, "CAPA ALTA - Banjo")
    add_program_change(banjo, 0, 106)

    guitar = seq.createTrack()
    add_track_name(guitar, "CAPA MEDIA - Guitarra acustica")
    add_program_change(guitar, 1, 25)

    bass = seq.createTrack()
    add_track_name(bass, "CAPA BAJA - Contrabajo")
    add_program_change(bass, 2, 33)

    trumpet = seq.createTrack()
    add_track_name(trumpet, "CAPA ALTA - Trompeta con sordina")
    add_program_change(trumpet, 3, 60)

    harmonica = seq.createTrack()
    add_track_name(harmonica, "CAPA ALTA - Armonica")
    add_program_change(harmonica, 4, 23)

    drums = seq.createTrack()
    add_track_name(drums, "CAPA BAJA - Bateria")

    bar_ticks = beats_to_ticks(4.0)
    e = beats_to_ticks(0.5)

    def bass_walk(chord_name, start_tick):
        root = BASS_ROOT[chord_name]
        fifth = root + 7
        q = beats_to_ticks(1.0)
        add_note(bass, 2, root, 95, start_tick, q)
        add_note(bass, 2, fifth, 88, start_tick + q, q)
        add_note(bass, 2, root, 92, start_tick + 2 * q, q)
        add_note(bass, 2, fifth, 88, start_tick + 3 * q, q)

    def guitar_stab(chord_name, start_tick, beats_list, velocity=75):
        chord = CHORDS[chord_name]
        dur = beats_to_ticks(0.25)
        for b in beats_list:
            add_chord(guitar, 1, chord, velocity, start_tick + beats_to_ticks(b), dur)

    def drum_bar(start_tick, dense=True, backbeat='snare'):
        eb = beats_to_ticks(0.5)
        q = beats_to_ticks(1.0)
        add_note(drums, 9, KICK, 100, start_tick, q)
        add_note(drums, 9, KICK, 95, start_tick + 2 * q, q)
        snare_note = SNARE if backbeat == 'snare' else SIDE_STICK
        add_note(drums, 9, snare_note, 95, start_tick + q, q)
        add_note(drums, 9, TAMBOURINE, 80, start_tick + q, q)
        add_note(drums, 9, snare_note, 95, start_tick + 3 * q, q)
        add_note(drums, 9, TAMBOURINE, 80, start_tick + 3 * q, q)
        step = eb if dense else q
        count = 8 if dense else 4
        toggle = True
        t = start_tick
        for i in range(count):
            block = HI_WOOD_BLOCK if toggle else LO_WOOD_BLOCK
            add_note(drums, 9, block, 70, t, step)
            toggle = not toggle
            t += step

    progression_a = ['Am', 'Dm', 'E7', 'Am', 'Am', 'Dm', 'E7', 'Am']
    melody_a = [
        CELLS['Am_1'], CELLS['Dm_1'], CELLS['E7_1'], CELLS['Am_arp'],
        [69, 76, 72, 76, 69, None, 72, None],
        [74, 69, 77, 69, 74, None, 77, None],
        [64, 68, 71, 74, 68, 71, 74, None],
        None,
    ]

    def write_section_a(start_tick):
        for i, chord_name in enumerate(progression_a):
            t = start_tick + i * bar_ticks
            bass_walk(chord_name, t)
            guitar_stab(chord_name, t, [0, 1, 2, 3], velocity=80)
            drum_bar(t, dense=True, backbeat='snare')

            if i == 6:
                add_note(trumpet, 3, 71, 85, t + beats_to_ticks(3.0), beats_to_ticks(1.0))

            pattern = melody_a[i]
            if pattern is not None:
                for j, p in enumerate(pattern):
                    add_note(banjo, 0, p, 100, t + j * e, e)
            else:
                add_note(banjo, 0, 69, 100, t, beats_to_ticks(1.5))
                add_note(banjo, 0, 72, 95, t + beats_to_ticks(1.5), beats_to_ticks(0.5))
                add_note(banjo, 0, 76, 100, t + beats_to_ticks(2.0), beats_to_ticks(1.0))
                add_note(banjo, 0, 69, 105, t + beats_to_ticks(3.0), beats_to_ticks(1.0))
                add_note(trumpet, 3, 57, 80, t + beats_to_ticks(3.0), beats_to_ticks(1.0))
        return start_tick + len(progression_a) * bar_ticks

    progression_b = ['F', 'C', 'Dm', 'E7', 'F', 'C', 'Dm', 'E7']
    harmonica_melody = [
        [(65, 2.0), (69, 1.0), (72, 1.0)],
        [(72, 2.0), (76, 1.0), (67, 1.0)],
        [(74, 2.0), (77, 1.0), (69, 1.0)],
        [(64, 1.0), (68, 1.0), (71, 2.0)],
        [(65, 1.0), (69, 1.0), (72, 1.0), (77, 1.0)],
        [(76, 2.0), (72, 1.0), (67, 1.0)],
        [(74, 1.0), (77, 1.0), (69, 1.0), None],
        [(64, 0.5), (68, 0.5), (71, 0.5), (74, 0.5), (64, 1.0), (68, 1.0)],
    ]

    def write_section_b(start_tick):
        for i, chord_name in enumerate(progression_b):
            t = start_tick + i * bar_ticks
            bass_walk(chord_name, t)
            chord = CHORDS[chord_name]
            add_chord(banjo, 0, chord, 60, t, beats_to_ticks(0.5))
            add_chord(banjo, 0, chord, 55, t + beats_to_ticks(2.0), beats_to_ticks(0.5))
            drum_bar(t, dense=False, backbeat='side_stick')

            if i in (0, 4):
                add_note(trumpet, 3, CHORDS[chord_name][-1], 70,
                          t + beats_to_ticks(3.5), beats_to_ticks(0.5))

            tt = t
            for item in harmonica_melody[i]:
                if item is None:
                    tt += beats_to_ticks(1.0)
                    continue
                pitch, dur_beats = item
                add_note(harmonica, 4, pitch, 85, tt, beats_to_ticks(dur_beats))
                tt += beats_to_ticks(dur_beats)
        return start_tick + len(progression_b) * bar_ticks

    cursor = 0
    intro_start = cursor
    for bar in range(4):
        t = cursor
        bass_walk('Am', t)
        guitar_stab('Am', t, [0], velocity=65)
        drum_bar(t, dense=True, backbeat='side_stick' if bar < 2 else 'snare')
        cursor += bar_ticks

    pickup_start = intro_start + 3 * bar_ticks + beats_to_ticks(2.0)
    for i, p in enumerate([64, 68, 71, 74]):
        add_note(banjo, 0, p, 90, pickup_start + i * e, e)

    loop_start = cursor
    cursor = write_section_a(cursor)
    cursor = write_section_b(cursor)
    total_end = cursor

    write_sequence(seq, "baking_bad_normal.mid")

    def ticks_to_seconds(ticks):
        return ticks * (60.0 / BPM) / PPQ

    print("Duracion del loop: %.2fs" % ticks_to_seconds(total_end - loop_start))
    print("Punto de bucle: %.2fs -> %.2fs (intro suena 1 sola vez antes)" %
          (ticks_to_seconds(loop_start), ticks_to_seconds(total_end)))


if __name__ == '__main__':
    main()
