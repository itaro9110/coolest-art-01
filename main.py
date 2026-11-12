"""Coolest art, make.fun coolest-art-01: a lone astronaut drifts before a
colossal ringed planet. Pure Python 3.13 stdlib: the scene is drawn
procedurally (gradients, noise, capsules, ellipses) and encoded as PNG
by hand. Deterministic: fixed seed, no clock, no network."""
import math
import os
import random
import struct
import zlib

W = H = 1024
PX = bytearray(W * H * 3)


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def sm(t):
    t = clamp(t)
    return t * t * (3.0 - 2.0 * t)


def put(x, y, r, g, b):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        PX[i] = r
        PX[i + 1] = g
        PX[i + 2] = b


def blend(x, y, r, g, b, a):
    if 0 <= x < W and 0 <= y < H and a > 0.0:
        i = (y * W + x) * 3
        if a >= 1.0:
            PX[i] = r
            PX[i + 1] = g
            PX[i + 2] = b
        else:
            PX[i] = int(PX[i] + (r - PX[i]) * a)
            PX[i + 1] = int(PX[i + 1] + (g - PX[i + 1]) * a)
            PX[i + 2] = int(PX[i + 2] + (b - PX[i + 2]) * a)


def get(x, y):
    i = (y * W + x) * 3
    return PX[i], PX[i + 1], PX[i + 2]


def h2(ix, iy, s=0):
    n = (ix * 374761393 + iy * 668265263 + s * 974634211) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFFFFFF) / 4294967295.0


def vnoise(x, y, s=0):
    ix = math.floor(x)
    iy = math.floor(y)
    fx = x - ix
    fy = y - iy
    ux = sm(fx)
    uy = sm(fy)
    a = h2(ix, iy, s)
    b = h2(ix + 1, iy, s)
    c = h2(ix, iy + 1, s)
    d = h2(ix + 1, iy + 1, s)
    return lerp(lerp(a, b, ux), lerp(c, d, ux), uy)


def fbm(x, y, s=0, oct=3):
    v = 0.0
    amp = 0.5
    f = 1.0
    for _ in range(oct):
        v += amp * vnoise(x * f, y * f, s)
        amp *= 0.5
        f *= 2.03
    return v


def sky():
    # Vertical gradient: near-black indigo at top, deep violet at bottom.
    # Nebula evaluated on a coarse grid, then bilinearly sampled per pixel.
    gw = gh = 96
    grid = []
    for gy in range(gh + 1):
        row = []
        for gx in range(gw + 1):
            a = fbm(gx * 0.055, gy * 0.055, 7, 3)
            b = fbm(gx * 0.055 + 40.0, gy * 0.055 + 9.0, 21, 3)
            row.append((a, b))
        grid.append(row)
    for y in range(H):
        t = y / (H - 1)
        br = lerp(4, 16, t)
        bg = lerp(6, 10, t)
        bb = lerp(18, 38, t)
        gyf = y / (H - 1) * gh
        gy0 = int(gyf)
        gy1 = min(gy0 + 1, gh)
        wy = gyf - gy0
        base = y * W * 3
        for x in range(W):
            gxf = x / (W - 1) * gw
            gx0 = int(gxf)
            gx1 = min(gx0 + 1, gw)
            wx = gxf - gx0
            a0 = lerp(grid[gy0][gx0][0], grid[gy0][gx1][0], wx)
            a1 = lerp(grid[gy1][gx0][0], grid[gy1][gx1][0], wx)
            na = lerp(a0, a1, wy)
            b0 = lerp(grid[gy0][gx0][1], grid[gy0][gx1][1], wx)
            b1 = lerp(grid[gy1][gx0][1], grid[gy1][gx1][1], wx)
            nb = lerp(b0, b1, wy)
            # Teal-violet nebula where the noise is high, warm ember
            # where the second field peaks; both fade to the gradient.
            na2 = sm((na - 0.52) * 3.2)
            nb2 = sm((nb - 0.60) * 3.0)
            r = br + 42 * nb2 + 8 * na2
            g = bg + 26 * na2 + 14 * nb2
            bl = bb + 58 * na2 + 6 * nb2
            i = base + x * 3
            PX[i] = int(min(255, r))
            PX[i + 1] = int(min(255, g))
            PX[i + 2] = int(min(255, bl))


def stars():
    rng = random.Random(20261113)
    for _ in range(750):
        x = rng.randrange(W)
        y = rng.randrange(H)
        m = rng.random()
        if m < 0.72:
            v = rng.randint(150, 235)
            put(x, y, v, v, int(v * 0.92))
        elif m < 0.9:
            v = rng.randint(180, 255)
            put(x, y, v, v, v)
            if rng.random() < 0.5:
                blend(x + 1, y, v // 2, v // 2, v // 2, 0.5)
                blend(x, y + 1, v // 2, v // 2, v // 2, 0.5)
        else:  # rare bright star with a cross flare
            v = 255
            put(x, y, v, v, v)
            for d in range(1, 7):
                a = 0.55 * (1 - d / 7.0)
                blend(x + d, y, v, v, v, a)
                blend(x - d, y, v, v, v, a)
                blend(x, y + d, v, v, v, a)
                blend(x, y - d, v, v, v, a)


# Planet: huge, centre upper-right, radius 400; light from upper-left.
PCX, PCY, PR = 745, 300, 400
LX, LY = -0.62, -0.55  # sun direction (normalised below)
_LN = math.hypot(LX, LY)
LX, LY = LX / _LN, LY / _LN

# Warm band palette, dark rust -> gold -> pale cream.
BANDS = [
    (52, 26, 14), (122, 62, 22), (196, 116, 40), (238, 176, 84),
    (150, 88, 34), (214, 148, 62), (96, 48, 22), (232, 190, 120),
    (176, 104, 44), (70, 36, 18),
]


def planet():
    x0 = max(0, PCX - PR)
    x1 = min(W, PCX + PR + 1)
    y0 = max(0, PCY - PR)
    y1 = min(H, PCY + PR + 1)
    for y in range(y0, y1):
        dy = (y - PCY) / PR
        for x in range(x0, x1):
            dx = (x - PCX) / PR
            d2 = dx * dx + dy * dy
            if d2 >= 1.0:
                continue
            dz = math.sqrt(1.0 - d2)
            # Turbulent horizontal bands.
            turb = fbm(x * 0.012, y * 0.05, 3, 2) - 0.5
            t = clamp(0.5 + dy * 0.5 + turb * 0.55)
            fi = t * (len(BANDS) - 1)
            i0 = int(fi)
            i1 = min(i0 + 1, len(BANDS) - 1)
            ft = fi - i0
            c0 = BANDS[i0]
            c1 = BANDS[i1]
            r = lerp(c0[0], c1[0], ft)
            g = lerp(c0[1], c1[1], ft)
            b = lerp(c0[2], c1[2], ft)
            # Diffuse light from the sun direction; night side falls
            # to near-black with the bands just barely visible.
            dif = clamp(dx * LX + dy * LY + dz * 0.55)
            lit = 0.24 + 0.95 * dif
            # Bright limb on the sun side.
            limb = sm((dz - 0.82) * 6.0) * sm((dx * LX + dy * LY + 0.35) * 2.0)
            r = r * lit + 120 * limb
            g = g * lit + 70 * limb
            b = b * lit + 26 * limb
            put(x, y, int(min(255, r)), int(min(255, g)), int(min(255, b)))


def rings(front):
    # Tilted ellipse around the planet: semi-major 640, semi-minor 165,
    # tilt -18 degrees. front=True draws the near half (v >= 0), which
    # crosses in front of the planet; the far half goes behind it.
    ang = math.radians(-18)
    ca = math.cos(ang)
    sa = math.sin(ang)
    for y in range(max(0, PCY - 200), min(H, PCY + 201)):
        for x in range(max(0, PCX - 660), min(W, PCX + 661)):
            dx = x - PCX
            dy = y - PCY
            u = ca * dx + sa * dy
            v = -sa * dx + ca * dy
            if front != (v >= 0):
                continue
            rn = math.sqrt((u / 640.0) ** 2 + (v / 165.0) ** 2)
            if rn < 0.66 or rn > 1.0:
                continue
            # Banded, slightly turbulent ring material with gaps.
            band = 0.5 + 0.5 * math.sin(rn * 46.0 + 2.5 * fbm(x * 0.02, y * 0.02, 5, 2))
            gap = sm((band - 0.42) * 2.6)
            if gap <= 0.02:
                continue
            # Sun side (upper-left) brighter; far half dimmer overall.
            sun = clamp(0.55 + 0.45 * (-(u / 640.0) * 0.7 + -(v / 165.0) * 0.3))
            bright = (0.8 if not front else 1.0) * sun
            a = gap * 0.85 * bright * sm((rn - 0.66) * 10.0) * sm((1.0 - rn) * 10.0)
            r = 238 * bright + 12
            g = 198 * bright + 8
            b = 138 * bright + 4
            blend(x, y, int(min(255, r)), int(min(255, g)), int(min(255, b)), a)


def seg_dist(px, py, ax, ay, bx, by):
    vx = bx - ax
    vy = by - ay
    wx = px - ax
    wy = py - ay
    dd = vx * vx + vy * vy
    t = 0.0 if dd == 0 else clamp((wx * vx + wy * vy) / dd)
    cx = ax + t * vx
    cy = ay + t * vy
    return math.hypot(px - cx, py - cy)


def capsule(ax, ay, bx, by, r, col, alpha=1.0):
    x0 = max(0, int(min(ax, bx) - r - 1))
    x1 = min(W - 1, int(max(ax, bx) + r + 1))
    y0 = max(0, int(min(ay, by) - r - 1))
    y1 = min(H - 1, int(max(ay, by) + r + 1))
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if seg_dist(x + 0.5, y + 0.5, ax, ay, bx, by) <= r:
                if alpha >= 1.0:
                    put(x, y, col[0], col[1], col[2])
                else:
                    blend(x, y, col[0], col[1], col[2], alpha)


def disc(cx, cy, r, col, alpha=1.0):
    capsule(cx, cy, cx, cy, r, col, alpha)


def astronaut():
    # Local frame, torso centre at origin; rotate -12 deg, move to (400, 720).
    ang = math.radians(-12)
    ca = math.cos(ang)
    sa = math.sin(ang)
    ox, oy = 400, 720

    def tr(lx, ly):
        return ox + (ca * lx - sa * ly) * 1.6, oy + (sa * lx + ca * ly) * 1.6

    suit = (26, 30, 48)
    rim = (255, 196, 110)
    # (endpoints local, radius, colour) — rim pass offset toward the planet.
    parts = [
        ((0, -18), (0, 28), 20),      # torso
        ((-22, -2), (-24, 24), 13),   # backpack
        ((14, -8), (38, 18), 9),      # arm reaching toward the planet
        ((-14, -6), (-34, 22), 9),    # other arm
        ((6, 26), (26, 62), 10),      # leg
        ((-8, 26), (-22, 58), 10),    # leg
    ]
    for off, col in (((7, -5), rim), ((0, 0), suit)):
        for (a, b, r) in parts:
            ax, ay = tr(a[0] + off[0], a[1] + off[1])
            bx, by = tr(b[0] + off[0], b[1] + off[1])
            capsule(ax, ay, bx, by, r, col)
    # Helmet: dark shell, then a visor burning with reflected planet light.
    hx, hy = tr(2, -48)
    disc(hx, hy, 40, suit)
    vx, vy = tr(10, -50)
    disc(vx, vy, 27, (250, 176, 84))
    disc(vx - 5, vy - 6, 14, (255, 226, 160))
    disc(vx + 10, vy + 8, 6, (255, 244, 214))
    # Tether: a slack curve from the backpack down and away off-frame.
    bx, by = tr(-24, 20)
    cx, cy = 560, 800
    ex, ey = 640, 930
    prev = (bx, by)
    for i in range(1, 41):
        t = i / 40.0
        x = (1 - t) * (1 - t) * bx + 2 * (1 - t) * t * cx + t * t * ex
        y = (1 - t) * (1 - t) * by + 2 * (1 - t) * t * cy + t * t * ey
        capsule(prev[0], prev[1], x, y, 1.4, (150, 152, 168), 0.75)
        prev = (x, y)


def ridge():
    # Jagged asteroid ridge along the bottom, near-black with a warm
    # rim on its upper edge where the planet light catches it.
    tops = []
    for x in range(W):
        tops.append(H - 46 - fbm(x * 0.008, 0.0, 11, 3) * 110)
    for x in range(W):
        t = int(tops[x])
        for y in range(max(0, t), H):
            put(x, y, 9, 8, 16)
        # Rim light on the crest, stronger toward the planet (right).
        warm = 0.25 + 0.75 * (x / W)
        for dy in range(3):
            yy = t + dy
            if 0 <= yy < H:
                a = (0.55 - dy * 0.18) * warm
                blend(x, yy, 214, 138, 62, a)


def finish():
    # Vignette + a whisper of grain, one pass over the whole frame.
    for y in range(H):
        ny = (y / (H - 1) - 0.5)
        base = y * W * 3
        for x in range(W):
            nx = (x / (W - 1) - 0.5)
            d = nx * nx + ny * ny
            vig = 1.0 - 0.34 * sm(d * 1.6)
            g = (h2(x // 2, y // 2, 99) - 0.5) * 3.0
            i = base + x * 3
            PX[i] = int(clamp(PX[i] * vig + g, 0, 255))
            PX[i + 1] = int(clamp(PX[i + 1] * vig + g, 0, 255))
            PX[i + 2] = int(clamp(PX[i + 2] * vig + g, 0, 255))


def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def png_bytes():
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        row = PX[y * stride:(y + 1) * stride]
        # Sub filter: smooth art compresses far better than raw rows.
        filt = bytearray(stride)
        for i in range(stride):
            left = row[i - 3] if i >= 3 else 0
            filt[i] = (row[i] - left) & 0xFF
        raw.append(1)
        raw.extend(filt)
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


def main():
    sky()
    stars()
    rings(False)
    planet()
    rings(True)
    astronaut()
    ridge()
    finish()
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes())
    print("wrote", path)


if __name__ == "__main__":
    main()






