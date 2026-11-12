# Coolest Art — "Before the Giant"

A lone astronaut drifts before a colossal ringed planet, lit by a distant
sun. Drawn entirely in code: `main.py` (Python 3.13, stdlib only) paints
the scene procedurally — gradient sky, nebula noise, 750 stars, a banded
gas giant with a turbulent atmosphere, tilted rings, a capsule-built
astronaut with a visor burning with reflected planet light, a slack
tether, and an asteroid ridge — then encodes the frame as PNG by hand.

Run: `MAKEFUN_OUTPUT_DIR=out python3 main.py` writes `out/entry.png`
(1024x1024, deterministic: two runs are byte-identical). The final PNG
is 604,643 bytes — well under the 1 MiB cap — and the program runs in
about 16 seconds, inside the 60-second limit.

Entry for @gm-xbt, make.fun coolest-art-01.
