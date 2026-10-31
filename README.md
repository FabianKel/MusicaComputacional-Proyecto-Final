# Baking Bad — Música (Proyecto Final, Música Computacional)

Material de Persona 1 (Diseño Sonoro y Composición Base): Motivo Principal, Normal y Persecución, cada una generada con su propio script Jython (`javax.sound.midi`). Incluye también "Entrega en las Sombras" (tema de sigilo).

## Qué composiciones hay y en qué momento ocurren

- **Motivo Principal** (`midi/baking_bad_motivo_principal.mid`) — Presentación aislada del tema (banjo + acompañamiento mínimo, sin batería, una sola pasada con cadencia final, sin loop). Pensada para pantalla de título/menú o como sting de transición: es la identidad sonora de la que Normal y Persecución son transformaciones.
- **Normal** (`midi/baking_bad_normal.mid`) — Estado de **Exploración**. Suena mientras el jugador cocina o recoge órdenes. Loop a tempo fijo, sin variaciones de velocidad.
- **Persecución** (`midi/baking_bad_persecucion.mid`) — Estado de **Combate**. Suena cuando descubren al jugador. Transformación directa del Motivo Principal (disminución rítmica + tempo más rápido), con una capa de tambores de tensión añadida.
- **Entrega en las Sombras** (`midi/baking_bad_entrega.mid`) — Fase de sigilo/entrega del pastel por los pasillos de la prisión (candidata a "Poco Tiempo"/Peligro; pendiente de confirmar con Persona 2). Composición aparte, sin relación temática con el motivo principal.

Los previews en `previews/` están renderizados con un soundfont General MIDI genérico (FluidSynth, reverb/chorus desactivados para evitar colas al loopear), solo de referencia.

## Tabla comparativa

| | **Motivo Principal** | **Normal** (Exploración) | **Persecución** (Combate) | **Entrega en las Sombras** |
|---|---|---|---|---|
| Rol en el juego | Identidad sonora / menú | Cocina tranquila | Te descubrieron, reaccionas | Sigilo entregando el pastel |
| Tempo | 132 BPM | 132 BPM fijo | 150 BPM | 58 BPM |
| Relación con el motivo | Es el motivo original | Mismo motivo, arreglo completo | Motivo disminuido (corchea→semicorchea, x2 por compás) + tempo más alto | Sin relación — composición aparte |
| Tonalidad / centro | La menor, con Sol# (3ra de Mi7) | Igual | Igual (mismos acordes y raíces de bajo) | Drone en Mi + cluster Mi-Fa-Sib-Si |
| Duración | 9.09s (una pasada, no loop) | Intro 7.27s (1 vez) + loop de 29.09s | Loop continuo de 12.80s (8 compases) | 115.86s (arco completo) |
| Técnica compositiva | Escritura directa | Escritura directa | Disminución rítmica + aumento de tempo | Colocación aleatoria controlada (semilla fija), técnica de composición aleatoria |
| Instrumentos (GM) | Banjo, Guitarra acústica, Contrabajo | + Trompeta con sordina, Armónica, Batería | Fiddle, Guitarra con distorsión, Bajo eléctrico, Trompeta con sordina, Batería + tambores de tensión | Contrabajo, Pad metálico, Campanas tubulares, FX/riser, Percusión |
| Canales MIDI | 0 Banjo · 1 Guitarra · 2 Bajo | 0 Banjo · 1 Guitarra · 2 Bajo · 3 Trompeta · 4 Armónica · 9 Batería | 0 Fiddle · 1 Guitarra · 2 Bajo · 3 Trompeta · 9 Batería | 0 Contrabajo · 1 Pad · 2 Campanas · 3 FX · 9 Percusión |
| Capas verticales (FMOD) | No aplica | Baja = Bajo+Batería · Media = +Guitarra · Alta = +Banjo+Armónica+Trompeta | Baja = Bajo+Batería+Tambores · Media = +Guitarra · Alta = +Fiddle+Trompeta | No definidas |
| Variación de velocity | Fija | Fija | Alta y constante (~85-108) en todas las voces | Baja y creciente por sección (25-85) |
| Script | `scripts/motivo_principal.py` | `scripts/normal.py` | `scripts/persecucion.py` | `scripts/entrega.py` |
| Archivo MIDI | `midi/baking_bad_motivo_principal.mid` | `midi/baking_bad_normal.mid` | `midi/baking_bad_persecucion.mid` | `midi/baking_bad_entrega.mid` |
| Preview | `previews/motivo_principal_preview.mp3` | `previews/normal_preview.mp3` | `previews/persecucion_preview_loop.mp3` (loop x4) | `previews/entrega_preview.mp3` |

## Estructura de esta carpeta

```
proyectoFinal/
├── README.md
├── scripts/
│   ├── motivo_principal.py
│   ├── normal.py
│   ├── persecucion.py
│   └── entrega.py
├── midi/
│   ├── baking_bad_motivo_principal.mid
│   ├── baking_bad_normal.mid
│   ├── baking_bad_persecucion.mid
│   └── baking_bad_entrega.mid
└── previews/
    ├── motivo_principal_preview.mp3
    ├── normal_preview.mp3
    ├── persecucion_preview_loop.mp3
    └── entrega_preview.mp3
```

Cada script es independiente (`jython <script>.py` desde la carpeta `scripts/`, genera su `.mid` en esa misma carpeta).
