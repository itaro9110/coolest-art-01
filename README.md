# Coolest Art — "The Last Lighthouse"

In a storm that has swallowed the coast, one keeper climbs to relight
the lamp — and far below, a small boat with a single lantern rows home
into the beam. It is a picture about guidance: someone keeping the
light on so someone else can find their way back.

Drawn entirely in code: `main.py` (Python 3.13, stdlib only) paints the
scene procedurally — a bruised storm sky, soft storm clouds, a dark
swell with foam crests, jagged basalt rocks, a tapered lighthouse with
warm lit windows, a glowing lamp room, two beams cutting the rain, the
keeper on the gallery with his own small lantern, and the little boat
with its sail and bow lantern — then encodes the frame as PNG by hand.

Run: `MAKEFUN_OUTPUT_DIR=out python3 main.py` writes `out/entry.png`
(1024x1024, deterministic: two runs write byte-identical output).

No network, no clock, no external assets — every pixel is computed
from a single fixed seed, so the picture is the same on every machine.
