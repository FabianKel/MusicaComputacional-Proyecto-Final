# Baking Bad — Música (Proyecto Final, Música Computacional)

Material: Motivo Principal, Normal, Persecución (Combate), Peligro,
Menú Principal, Muerte, Fragmento de Transición, 3 SFX y 3 Stingers. Cada pieza tiene su
propio script Jython (`javax.sound.midi`), independiente del resto.

## Qué composiciones hay y en qué momento ocurren

- **Motivo Principal** (`MIDI/baking_bad_motivo_principal.mid`): presentación aislada del tema (banjo+guitarra+bajo, sin loop). Es la identidad sonora de la que Normal, Peligro y Menú se derivan.
- **Normal** (`MIDI/baking_bad_normal.mid`) — Exploración. Suena mientras el jugador cocina. 132 BPM, loop fijo.
- **Persecución / Combate** (`MIDI/baking_bad_persecucion.mid`): te descubrieron. 132 BPM (mismo tempo que el resto, a pedido del equipo para facilitar las transiciones), disminución rítmica del motivo, tambores de tensión.
- **Peligro** (`MIDI/baking_bad_peligro.mid`): tensión/poco tiempo, sin descubrimiento todavía. Mismo tempo que Normal (132 BPM), arpegio continuo en campana aguda sobre el mismo motivo (no acelera el pulso, solo la densidad ritmica).
- **Menú Principal** (`MIDI/baking_bad_menu.mid`): pantalla de menú. El motivo principal en loop, solo banjo+guitarra+bajo (sin capas fuertes).
- **Muerte** (`MIDI/baking_bad_muerte.mid`): game over. Sting sin loop, tempo lento (70 BPM), descenso sobre el mismo material armónico, sin resolver.
- **Fragmento de Transición** (`MIDI/baking_bad_transicion.mid`): puente corto (2 compases, 132 BPM) para conectar estados, cuantizable a compás.
- **SFX**: Cocinar pastel, Tomar orden, Entregar orden (`MIDI/sfx_*.mid`).
- **Stingers**: Dinero recibido, Dinero perdido, Detectado (`MIDI/stinger_*.mid`).

Los previews en `previews/` están renderizados con un soundfont General MIDI genérico
(FluidSynth, reverb/chorus desactivados), solo de referencia.

## Tabla comparativa (piezas con loop / capas)

| | **Motivo Principal** | **Normal** | **Combate** | **Peligro** | **Menú** |
|---|---|---|---|---|---|
| Rol | Identidad sonora | Cocina tranquila | Te descubrieron | Tensión / poco tiempo | Pantalla de menú |
| Tempo | 132 BPM | 132 BPM | 132 BPM | 132 BPM | 132 BPM |
| Relación con el motivo | Original | Arreglo completo | Disminución rítmica (corchea→semicorchea) | Arpegio continuo en campana sobre el mismo motivo | Motivo sin capas fuertes |
| Duración | 9.09s (sin loop) | Intro 7.27s + loop 29.09s | Loop 14.55s | Loop 14.55s | Loop 14.55s |
| Capas verticales | No aplica | Baja/Media/Alta | Baja/Media/Alta | Baja/Media/Alta | Sin capas |
| Script | `motivo_principal.py` | `normal.py` | `persecucion.py` | `peligro.py` | `menu.py` |

## Piezas sin loop (stings)

| | **Muerte** | **Transición** | **SFX (x3)** | **Stingers (x3)** |
|---|---|---|---|---|
| Tempo | 70 BPM | 132 BPM | 132 BPM | 132 BPM |
| Duración | 17.14s | 3.64s | 0.3-1.1s | 0.45-0.91s |
| Script | `muerte.py` | `transicion.py` | `sfx_*.py` | `stinger_*.py` |

## FMOD (`P3_BakingBad/`)

Eventos ya colocados en el proyecto FMOD, cada uno con su LoopRegion/TempoMarker:
Musica (Normal), Peligro, Combate, Menu, Muerte, Transicion, 3 eventos SFX y 3 Stingers.
Peligro y Combate tienen remezcla vertical (Media/Alta) atada al parámetro Intensidad,
igual que Normal. El resto son eventos de un solo disparo.

## Estructura de esta carpeta

```
proyectoFinal/
├── README.md
├── scripts/        (1 script Jython por pieza, + split_layers.py para exportar capas)
├── MIDI/           (salida de cada script)
├── previews/       (mp3 de referencia, renderizados con FluidSynth)
├── stems/          (wav usados por el proyecto FMOD)
└── P3_BakingBad/   (proyecto FMOD Studio)
```

Cada script es independiente (`jython <script>.py` desde `scripts/`, genera su `.mid` ahí mismo).
`split_layers.py` filtra canales MIDI por capa (usado para exportar Peligro_Baja/Media/Alta.wav).
