# -*- coding: utf-8 -*-
# Entrega en las Sombras: drone + cluster disonante, colocacion
# aleatoria controlada (semilla fija) dentro de una paleta de alturas
# curada. Tecnica de composicion aleatoria (Xenakis, Schaeffer).

from javax.sound.midi import (Sequence, MidiSystem, ShortMessage,
                               MidiEvent, MetaMessage)
from java.io import File
import random

PPQ = 480
OPEN_TRIANGLE = 81
LOW_TOM = 45
VIBRASLAP = 58


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
    BPM = 58
    random.seed(13)
    seq = Sequence(Sequence.PPQ, PPQ)

    meta = seq.createTrack()
    add_track_name(meta, "Entrega - tempo")
    add_tempo(meta, BPM)
    add_time_signature(meta, 4, 4)

    drone_track = seq.createTrack()
    add_track_name(drone_track, "Contrabajo - drone")
    add_program_change(drone_track, 0, 44)

    pad_track = seq.createTrack()
    add_track_name(pad_track, "Pad metalico - cluster")
    add_program_change(pad_track, 1, 94)

    bell_track = seq.createTrack()
    add_track_name(bell_track, "Campanas")
    add_program_change(bell_track, 2, 15)

    fx_track = seq.createTrack()
    add_track_name(fx_track, "FX / riser")
    add_program_change(fx_track, 3, 103)

    perc_track = seq.createTrack()
    add_track_name(perc_track, "Percusion")

    bar_ticks = beats_to_ticks(4.0)
    PRISON_CLUSTER = [28, 29, 34, 35]

    def sustain_drone(start_tick, dur_ticks, pitch=28, velocity=70):
        seg = beats_to_ticks(8.0)
        t = start_tick
        end = start_tick + dur_ticks
        while t < end:
            add_note(drone_track, 0, pitch, velocity, t, min(seg, end - t))
            t += seg

    def pad_cluster(start_tick, dur_ticks, pitches, velocity=55):
        add_chord(pad_track, 1, pitches, velocity, start_tick, dur_ticks)

    def scatter_events(track, channel, start_tick, length_ticks,
                        pitch_pool, note_choice, velocity_range,
                        density, min_gap_beats=1.0):
        slot = beats_to_ticks(min_gap_beats)
        t = start_tick
        end = start_tick + length_ticks
        while t < end:
            if random.random() < density:
                pitch = random.choice(pitch_pool) if note_choice else pitch_pool
                vel = random.randint(velocity_range[0], velocity_range[1])
                dur = beats_to_ticks(random.choice([0.5, 1.0, 1.5, 2.0]))
                jitter = random.randint(0, slot // 3)
                add_note(track, channel, pitch, vel, t + jitter, dur)
            t += slot

    cursor = 0

    sec1_start = cursor
    sec1_len = 8 * bar_ticks
    sustain_drone(sec1_start, sec1_len, pitch=28, velocity=62)
    scatter_events(bell_track, 2, sec1_start, sec1_len, PRISON_CLUSTER, True, (40, 55), density=0.10, min_gap_beats=2.0)
    scatter_events(perc_track, 9, sec1_start, sec1_len, OPEN_TRIANGLE, False, (25, 40), density=0.05, min_gap_beats=3.0)
    cursor += sec1_len

    sec2_start = cursor
    sec2_len = 8 * bar_ticks
    sustain_drone(sec2_start, sec2_len, pitch=28, velocity=68)
    pad_cluster(sec2_start, 4 * bar_ticks, [52, 58], velocity=42)
    pad_cluster(sec2_start + 4 * bar_ticks, 4 * bar_ticks, [53, 59], velocity=46)
    scatter_events(bell_track, 2, sec2_start, sec2_len, PRISON_CLUSTER, True, (45, 65), density=0.18, min_gap_beats=1.5)
    scatter_events(perc_track, 9, sec2_start, sec2_len, LOW_TOM, False, (50, 70), density=0.22, min_gap_beats=1.0)
    scatter_events(perc_track, 9, sec2_start, sec2_len, OPEN_TRIANGLE, False, (30, 45), density=0.08, min_gap_beats=2.5)
    cursor += sec2_len

    sec3_start = cursor
    sec3_len = 8 * bar_ticks
    sustain_drone(sec3_start, sec3_len, pitch=28, velocity=78)
    add_note(fx_track, 3, 76, 40, sec3_start, beats_to_ticks(0.1))
    for k in range(6):
        add_note(fx_track, 3, 76, 40 + k * 12, sec3_start + k * beats_to_ticks(0.6), beats_to_ticks(0.6))
    pad_cluster(sec3_start, 4 * bar_ticks, [58, 59, 64], velocity=58)
    pad_cluster(sec3_start + 4 * bar_ticks, 4 * bar_ticks, [52, 53, 58], velocity=62)
    scatter_events(bell_track, 2, sec3_start, sec3_len, PRISON_CLUSTER, True, (55, 80), density=0.28, min_gap_beats=1.0)
    scatter_events(perc_track, 9, sec3_start, sec3_len, LOW_TOM, False, (60, 85), density=0.32, min_gap_beats=0.75)
    scatter_events(perc_track, 9, sec3_start, sec3_len, VIBRASLAP, False, (55, 75), density=0.12, min_gap_beats=2.0)
    cursor += sec3_len

    sec4_start = cursor
    sec4_len = 4 * bar_ticks
    sustain_drone(sec4_start, sec4_len, pitch=28, velocity=64)
    pad_cluster(sec4_start, sec4_len, [52, 58], velocity=30)
    scatter_events(bell_track, 2, sec4_start, sec4_len, PRISON_CLUSTER, True, (35, 50), density=0.12, min_gap_beats=2.0)
    scatter_events(perc_track, 9, sec4_start, sec4_len, OPEN_TRIANGLE, False, (20, 35), density=0.06, min_gap_beats=3.0)
    cursor += sec4_len

    write_sequence(seq, "baking_bad_entrega.mid")
    print("Duracion: %.2fs" % (cursor * 60.0 / BPM / PPQ))


if __name__ == '__main__':
    main()
