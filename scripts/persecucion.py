# -*- coding: utf-8 -*-
# Persecucion (Combate): transformacion del motivo por disminucion
# ritmica (corchea -> semicorchea, celda x2 por compas) y tempo mas
# alto. Misma progresion/acordes/bajo que Normal.
# 3 capas: BAJA = bajo+bateria+tambores, MEDIA = +guitarra, ALTA = +fiddle+trompeta.

from javax.sound.midi import (Sequence, MidiSystem, ShortMessage,
                               MidiEvent, MetaMessage)
from java.io import File

PPQ = 480
KICK = 36
SNARE = 38
HI_WOOD_BLOCK = 76
LO_WOOD_BLOCK = 77
LOW_FLOOR_TOM = 41
HIGH_FLOOR_TOM = 43


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
CELLS = {
    'Am_1':   [69, 72, 76, 72, 69, None, 76, None],
    'Dm_1':   [74, 77, 81, 77, 74, None, 69, None],
    'E7_1':   [64, 68, 71, 74, 64, None, 71, None],
    'Am_arp': [69, 72, 76, 81, 76, 72, 69, None],
}


def main():
    BPM = 150
    seq = Sequence(Sequence.PPQ, PPQ)

    meta = seq.createTrack()
    add_track_name(meta, "Persecucion - tempo")
    add_tempo(meta, BPM)
    add_time_signature(meta, 4, 4)

    fiddle = seq.createTrack()
    add_track_name(fiddle, "CAPA ALTA - Fiddle (motivo disminuido)")
    add_program_change(fiddle, 0, 111)

    guitar = seq.createTrack()
    add_track_name(guitar, "CAPA MEDIA - Guitarra distorsion")
    add_program_change(guitar, 1, 30)

    bass = seq.createTrack()
    add_track_name(bass, "CAPA BAJA - Bajo electrico")
    add_program_change(bass, 2, 35)

    trumpet = seq.createTrack()
    add_track_name(trumpet, "CAPA ALTA - Trompeta con sordina")
    add_program_change(trumpet, 3, 60)

    drums = seq.createTrack()
    add_track_name(drums, "CAPA BAJA - Bateria")

    bar_ticks = beats_to_ticks(4.0)
    e = beats_to_ticks(0.5)
    s16 = beats_to_ticks(0.25)

    progression = ['Am', 'Dm', 'E7', 'Am', 'Am', 'Dm', 'E7', 'Am']
    cells = [CELLS['Am_1'], CELLS['Dm_1'], CELLS['E7_1'], CELLS['Am_arp'],
             CELLS['Am_1'], CELLS['Dm_1'], CELLS['E7_1'], CELLS['Am_arp']]

    def bass_ostinato(chord_name, start_tick):
        root = BASS_ROOT[chord_name]
        fifth = root + 7
        pattern = [root, fifth, root, fifth, root, fifth, root, fifth]
        for j, p in enumerate(pattern):
            vel = 102 if j % 2 == 0 else 90
            add_note(bass, 2, p, vel, start_tick + j * e, e)

    def guitar_stabs(chord_name, start_tick):
        chord = CHORDS[chord_name]
        dur = beats_to_ticks(0.2)
        for off in [0.5, 1.0, 2.5, 3.0]:
            add_chord(guitar, 1, chord, 85, start_tick + beats_to_ticks(off), dur)

    def drums_bar(start_tick):
        q = beats_to_ticks(1.0)
        for b in range(4):
            add_note(drums, 9, KICK, 105, start_tick + b * q, q)
        add_note(drums, 9, SNARE, 100, start_tick + q, q)
        add_note(drums, 9, SNARE, 100, start_tick + 3 * q, q)
        # tambores de tension: pulso grave continuo + acento sincopado
        for b in range(4):
            add_note(drums, 9, LOW_FLOOR_TOM, 90, start_tick + b * q, q)
        add_note(drums, 9, HIGH_FLOOR_TOM, 95, start_tick + beats_to_ticks(1.5), beats_to_ticks(0.5))
        add_note(drums, 9, HIGH_FLOOR_TOM, 95, start_tick + beats_to_ticks(3.5), beats_to_ticks(0.5))
        # galope continuo en semicorcheas, sin huecos hasta el final del compas
        toggle = True
        t = start_tick
        for i in range(16):
            block = HI_WOOD_BLOCK if toggle else LO_WOOD_BLOCK
            add_note(drums, 9, block, 75, t, s16)
            toggle = not toggle
            t += s16

    def lead_motif(cell, start_tick):
        for rep in range(2):
            rep_start = start_tick + rep * beats_to_ticks(2.0)
            for j, p in enumerate(cell):
                add_note(fiddle, 0, p, 108, rep_start + j * s16, s16)

    def trumpet_offbeats(chord_name, start_tick):
        top_note = CHORDS[chord_name][-1]
        dur = beats_to_ticks(0.2)
        for off in [0.5, 1.5, 2.5, 3.5]:
            add_note(trumpet, 3, top_note, 95, start_tick + beats_to_ticks(off), dur)

    cursor = 0
    for i, chord_name in enumerate(progression):
        t = cursor
        bass_ostinato(chord_name, t)
        drums_bar(t)
        guitar_stabs(chord_name, t)
        lead_motif(cells[i], t)
        trumpet_offbeats(chord_name, t)
        cursor += bar_ticks

    total_end = cursor
    write_sequence(seq, "baking_bad_persecucion.mid")
    print("Duracion del loop: %.2fs (%d compases)" %
          (total_end * 60.0 / BPM / PPQ, len(progression)))


if __name__ == '__main__':
    main()
