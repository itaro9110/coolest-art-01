# The Last Lighthouse -- a keeper relights the lamp as a small boat finds home.
# Pure stdlib Python 3.13. Deterministic: fixed seed, no time, no network.
import math, os, random, struct, zlib

W = H = 1024
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/tmp")
rng = random.Random(20261113)
img = bytearray(W * H * 3)

def P(x, y, r, g, b):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        img[i] = r; img[i+1] = g; img[i+2] = b

def B(x, y, r, g, b, a):
    if 0 <= x < W and 0 <= y < H and a > 0:
        i = (y * W + x) * 3
        img[i] = int(img[i] + (r - img[i]) * a)
        img[i+1] = int(img[i+1] + (g - img[i+1]) * a)
        img[i+2] = int(img[i+2] + (b - img[i+2]) * a)

def row(y, r, g, b):
    i = y * W * 3
    img[i:i + W * 3] = bytes((r, g, b)) * W

def mix(a, b, t):
    return a + (b - a) * t

# --- storm sky: deep indigo above, bruised pale light near the horizon ---
for y in range(0, 620):
    t = y / 620
    row(y, int(mix(16, 74, t)), int(mix(22, 84, t)), int(mix(44, 104, t)))

def blob(cx, cy, rx, ry, r, g, b, a):
    # soft ellipse, alpha fading to the edge
    for y in range(max(0, int(cy - ry)), min(H, int(cy + ry) + 1)):
        dy = (y - cy) / ry
        dx = math.sqrt(max(0.0, 1 - dy * dy)) * rx
        for x in range(max(0, int(cx - dx)), min(W, int(cx + dx) + 1)):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            B(x, y, r, g, b, a * max(0.0, 1 - d))

# heavy storm clouds, dark bellies, lit undersides low down
for _ in range(38):
    cx = rng.uniform(-80, W + 80); cy = rng.uniform(20, 420)
    blob(cx, cy, rng.uniform(90, 250), rng.uniform(26, 68),
         10, 13, 30, rng.uniform(.25, .55))
for _ in range(16):
    cx = rng.uniform(0, W); cy = rng.uniform(330, 560)
    blob(cx, cy, rng.uniform(80, 220), rng.uniform(18, 44),
         150, 140, 110, rng.uniform(.10, .22))

# --- sea: dark swell below the horizon, a little warmer near the rocks ---
for y in range(620, H):
    t = (y - 620) / (H - 620)
    row(y, int(mix(20, 8, t)), int(mix(34, 14, t)), int(mix(52, 26, t)))

# foam crests: short pale strokes riding the swell
for _ in range(110):
    y = int(rng.uniform(640, 1000)); x0 = int(rng.uniform(0, W - 180))
    ln = int(rng.uniform(40, 180)); a = rng.uniform(.12, .4)
    for x in range(x0, x0 + ln):
        yy = y + int(3 * math.sin((x - x0) / 22))
        B(x, yy, 170, 190, 210, a * (1 - abs(x - x0 - ln / 2) / (ln / 2)))

# faint warm haze on the water, under where the lamp will shine
blob(660, 640, 320, 26, 200, 150, 70, .10)

def poly(points, r, g, b):
    # scanline fill of a simple polygon
    ys = [int(p[1]) for p in points]
    for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
        xs = []
        for i in range(len(points)):
            x1, y1 = points[i]; x2, y2 = points[(i + 1) % len(points)]
            if (y1 <= y < y2) or (y2 <= y < y1):
                xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
        if len(xs) >= 2:
            xs.sort()
            for x in range(max(0, int(xs[0])), min(W, int(xs[-1]) + 1)):
                P(x, y, r, g, b)

def ridge(x0, x1, ybase, n, r, g, b):
    # jagged rock silhouette between x0 and x1, rising off ybase
    pts = [(x0, ybase)]
    for i in range(1, n):
        pts.append((x0 + (x1 - x0) * i / n, ybase - rng.uniform(20, 120)))
    pts.append((x1, ybase))
    poly(pts, r, g, b)

# rock shelf across the lower right, tower ground; a low reef at left
ridge(430, 1024, 900, 14, 14, 14, 18)
ridge(0, 300, 930, 8, 12, 12, 16)
ridge(560, 900, 900, 9, 20, 20, 26)

# warm lamplight spilling onto the rocks below
blob(660, 870, 280, 70, 255, 180, 90, .12)

# --- the lighthouse: tapered tower, warm stone, storm-dark bands ---
TX = 660   # tower centre x at the base
TB = 800   # base y
TT = 300   # top y

def tower_half(y):
    return 46 - 18 * (TB - y) / (TB - TT)

for y in range(TT, TB + 1):
    hw = tower_half(y)
    for x in range(int(TX - hw), int(TX + hw) + 1):
        s = (x - (TX - hw)) / (2 * hw)   # 0 left .. 1 right
        shade = 0.72 + 0.28 * s
        P(x, y, int(214 * shade), int(196 * shade), int(164 * shade))

# dark storm bands
for by in (430, 520, 610):
    for y in range(by, by + 34):
        hw = tower_half(y)
        for x in range(int(TX - hw), int(TX + hw) + 1):
            P(x, y, 42, 38, 44)

# small warm windows, lit from inside
for wy, wx in ((380, -14), (470, 12), (560, -10)):
    for y in range(wy, wy + 12):
        for x in range(TX + wx, TX + wx + 9):
            P(x, y, 255, 190, 90)

# door at the base
for y in range(756, TB + 1):
    for x in range(TX - 13, TX + 14):
        P(x, y, 26, 24, 28)

# --- the lamp: first the halo, then glass, roof, gallery ---
blob(TX, 258, 150, 110, 255, 170, 60, .45)
blob(TX, 258, 70, 55, 255, 220, 130, .6)

# lamp room: bright glass panes
for y in range(238, 278):
    hw = 30 - (y - 238) * 0.1
    for x in range(int(TX - hw), int(TX + hw) + 1):
        P(x, y, 255, 190, 90)
# mullion bars
for x in (TX - 10, TX, TX + 10):
    for y in range(238, 278):
        P(x, y, 40, 36, 40)
# roof cap
for y in range(224, 238):
    hw = 34 - (y - 224) * 0.6
    for x in range(int(TX - hw), int(TX + hw) + 1):
        P(x, y, 30, 28, 34)
# gallery platform + railing
for x in range(TX - 58, TX + 59):
    P(x, 292, 30, 28, 34)
for x in range(TX - 58, TX + 59, 8):
    for y in range(276, 292):
        P(x, y, 30, 28, 34)

# --- the beam: two warm cones from the lamp, fading with distance ---
def beam(dx, dy):
    for d in range(0, 720, 2):
        cx = TX + dx * d; cy = 258 + dy * d
        wdt = 26 + d * 0.16
        a = 0.34 * (1 - d / 720)
        for y in range(int(cy - wdt), int(cy + wdt) + 1):
            for x in range(int(cx - 6), int(cx + 7)):
                B(x, y, 255, 200, 110, a * max(0.0, 1 - abs(y - cy) / wdt) * 0.5)

beam(-1, 0.10)    # out to sea, toward the boat
beam(1, -0.04)    # across the sky, nearly level

# --- the small boat, rowing home into the light ---
BX, BY = 330, 760
# hull: dark trapezoid
poly([(BX - 54, BY - 4), (BX + 54, BY - 4),
      (BX + 40, BY + 16), (BX - 40, BY + 16)], 24, 22, 26)
# mast + pale sail
for y in range(BY - 62, BY - 4):
    P(BX + 6, y, 30, 28, 32)
poly([(BX + 8, BY - 58), (BX + 8, BY - 8), (BX + 48, BY - 8)],
     216, 200, 170)
# rower: small dark silhouette, oar dipping
blob(BX - 18, BY - 16, 5, 6, 18, 16, 20, 1)
for y in range(BY - 12, BY - 2):
    P(BX - 18, y, 18, 16, 20)
for i in range(16):
    P(BX - 30 - i, BY - 2 + i, 40, 38, 42)
# bow lantern: warm dot + halo + reflection on the water
blob(BX + 46, BY - 8, 26, 20, 255, 200, 110, .55)
blob(BX + 46, BY - 8, 6, 6, 255, 230, 150, 1)
for y in range(BY + 18, BY + 70):
    B(BX + 46, y, 255, 190, 100, .22 * (1 - (y - BY) / 70))

# --- the keeper: small silhouette on the gallery, arm raised to the lamp ---
KX = TX + 18
for y in range(258, 292):
    P(KX, y, 20, 18, 22)
    P(KX + 1, y, 20, 18, 22)
blob(KX, 252, 5, 6, 20, 18, 22, 1)
for i in range(10):
    P(KX - 8 + i, 268 - i, 20, 18, 22)

# the keeper's own small lantern, raised toward the lamp
blob(KX - 10, 256, 7, 7, 255, 200, 110, .8)

# --- rain: diagonal streaks across the whole frame ---
for _ in range(500):
    x = int(rng.uniform(0, W)); y = int(rng.uniform(0, H))
    for i in range(7):
        B(x + i, y + i * 2, 180, 190, 210, .18)

# --- vignette: darken the corners so the lamp holds the eye ---
for y in range(H):
    dy = (y - 512) / 512
    for x in range(W):
        dx = (x - 512) / 512
        d = dx * dx + dy * dy
        if d > 0.55:
            f = 1 - 0.32 * min(1, (d - 0.55) / 0.45)
            i = (y * W + x) * 3
            img[i] = int(img[i] * f)
            img[i+1] = int(img[i+1] * f)
            img[i+2] = int(img[i+2] * f)

# grain: a little texture over the flat gradients
for _ in range(90000):
    x = int(rng.uniform(0, W)); y = int(rng.uniform(0, H))
    n = rng.randint(-7, 7)
    i = (y * W + x) * 3
    img[i] = max(0, min(255, img[i] + n))
    img[i+1] = max(0, min(255, img[i+1] + n))
    img[i+2] = max(0, min(255, img[i+2] + n))

# --- PNG encoder: hand-rolled, Sub filter, zlib level 9 ---
def save(path):
    raw = bytearray()
    for y in range(H):
        raw.append(1)
        st = y * W * 3
        prev = (0, 0, 0)
        line = bytearray()
        for i in range(0, W * 3, 3):
            r, g, b = img[st+i], img[st+i+1], img[st+i+2]
            line += bytes(((r - prev[0]) & 255,
                           (g - prev[1]) & 255, (b - prev[2]) & 255))
            prev = (r, g, b)
        raw += line
    comp = zlib.compress(bytes(raw), 9)
    def ck(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    data = b"\x89PNG\r\n\x1a\n"
    data += ck(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    data += ck(b"IDAT", comp)
    data += ck(b"IEND", b"")
    open(path, "wb").write(data)

save(os.path.join(OUT, "entry.png"))
print("wrote", os.path.join(OUT, "entry.png"))










