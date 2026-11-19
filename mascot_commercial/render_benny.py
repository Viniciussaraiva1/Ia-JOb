"""Renders the Benny's Plumbing mascot commercial (fictional business).

Usage: python3 render_benny.py <voiceover.mp3> <out.mp4>
Only the voiceover comes from ElevenLabs; visuals, music and SFX are generated here.
"""
import math
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 720, 1280
SS = 2  # supersampling
WW, HH = W * SS, H * SS
FPS = 24
DUR = 15.0
SR = 44100

FONT_XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FONT_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"

FUR = (156, 96, 54)
FUR_D = (112, 66, 36)
CREAM = (247, 228, 196)
OUT = (64, 38, 20)
CAP = (30, 96, 205)
CAP_D = (20, 66, 150)
GLOVE = (252, 252, 250)
NAVY = (22, 44, 120)


# ---------------------------------------------------------------- helpers
def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def keys(t, ks):
    """Smoothly interpolate between keyframes [(time, value), ...]; values may be tuples."""
    if t <= ks[0][0]:
        return ks[0][1]
    for (t0, v0), (t1, v1) in zip(ks, ks[1:]):
        if t0 <= t <= t1:
            a = smooth((t - t0) / (t1 - t0))
            if isinstance(v0, tuple):
                return tuple(p + (q - p) * a for p, q in zip(v0, v1))
            return v0 + (v1 - v0) * a
    return ks[-1][1]


def ell(d, cx, cy, rx, ry, fill, outline=OUT, w=6):
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill, outline=outline, width=w)


def rot_poly(cx, cy, rx, ry, ang, n=48):
    ca, sa = math.cos(ang), math.sin(ang)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return pts


def font(path, size):
    return ImageFont.truetype(path, size)


def text_center(d, x, y, s, f, fill, stroke=0, stroke_fill=(0, 0, 0)):
    d.text((x, y), s, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=stroke_fill)


# ---------------------------------------------------------------- mascot
def draw_beaver(d, cx, cy, s, p):
    """p: dict with mouth (0-1), lhand/rhand (unit coords), brow ('worried'|'happy'),
    blink (0-1), look (x offset), wrench (angle or None), thumbs (bool for right hand)."""
    U = lambda x, y: (cx + x * s, cy + y * s)
    lw = max(4, int(0.022 * s))

    # tail (behind)
    tx, ty = U(0.95, 0.75)
    d.polygon(rot_poly(tx, ty, 0.62 * s, 0.26 * s, -0.55), fill=FUR_D, outline=OUT, width=lw)
    for k in (-0.25, 0.0, 0.25):
        a, b = U(0.95 + k - 0.12, 0.75 + k * 0.6 - 0.05), U(0.95 + k + 0.12, 0.75 + k * 0.6 + 0.05)
        d.line([a, b], fill=OUT, width=max(2, lw // 2))

    # feet
    for sx in (-1, 1):
        fx, fy = U(sx * 0.45, 1.13)
        ell(d, fx, fy, 0.36 * s, 0.18 * s, FUR_D, w=lw)

    # body + belly
    bx, by = U(0, 0)
    ell(d, bx, by, 0.9 * s, 1.1 * s, FUR, w=lw)
    ell(d, *U(0, 0.18), 0.6 * s, 0.78 * s, CREAM, outline=None)
    # tool belt
    d.rounded_rectangle([*U(-0.8, 0.45), *U(0.8, 0.6)], radius=int(0.05 * s), fill=CAP, outline=OUT, width=lw)
    d.rectangle([*U(-0.12, 0.43), *U(0.12, 0.62)], fill=(240, 200, 60), outline=OUT, width=lw)

    # head
    hx, hy = U(0, -1.55)
    for sx in (-1, 1):
        ell(d, *U(sx * 0.66, -2.2), 0.2 * s, 0.2 * s, FUR_D, w=lw)
        ell(d, *U(sx * 0.66, -2.2), 0.1 * s, 0.1 * s, (200, 140, 110), outline=None)
    ell(d, hx, hy, 0.85 * s, 0.8 * s, FUR, w=lw)
    ell(d, *U(0, -1.22), 0.52 * s, 0.38 * s, CREAM, outline=None)

    # eyes
    blink = p.get("blink", 0.0)
    look = p.get("look", 0.0)
    for sx in (-1, 1):
        ex, ey = U(sx * 0.3, -1.72)
        ry = 0.19 * s * (1 - 0.92 * blink)
        ell(d, ex, ey, 0.17 * s, ry, (255, 255, 255), w=lw)
        if blink < 0.6:
            ix = ex + look * 0.06 * s
            ell(d, ix, ey + 0.02 * s, 0.1 * s, min(0.11 * s, ry), (60, 130, 210), outline=None)
            ell(d, ix, ey + 0.02 * s, 0.055 * s, min(0.06 * s, ry), (15, 15, 25), outline=None)
            ell(d, ix - 0.03 * s, ey - 0.03 * s, 0.025 * s, 0.025 * s, (255, 255, 255), outline=None)
        # brows
        if p.get("brow") == "worried":
            a, b = U(sx * 0.14, -2.0), U(sx * 0.44, -1.93)
        else:
            a, b = U(sx * 0.14, -1.97), U(sx * 0.44, -2.0)
        d.line([a, b], fill=OUT, width=int(0.045 * s))

    # nose
    ell(d, *U(0, -1.42), 0.16 * s, 0.1 * s, (40, 25, 20), outline=None)
    ell(d, *U(-0.05, -1.45), 0.04 * s, 0.025 * s, (120, 110, 110), outline=None)

    # mouth + buck teeth
    m = p.get("mouth", 0.0)
    mx, my = U(0, -1.2)
    if m > 0.08:
        mh = (0.06 + 0.16 * m) * s
        d.ellipse([mx - 0.2 * s, my - 0.02 * s, mx + 0.2 * s, my + mh], fill=(110, 30, 40), outline=OUT, width=lw)
        ell(d, mx, my + mh * 0.7, 0.1 * s, mh * 0.3, (230, 110, 120), outline=None)
    else:
        happy = p.get("brow") != "worried"
        box = [mx - 0.2 * s, my - 0.12 * s, mx + 0.2 * s, my + 0.08 * s]
        if happy:
            d.arc(box, 20, 160, fill=OUT, width=lw)
        else:
            d.arc([mx - 0.15 * s, my + 0.0 * s, mx + 0.15 * s, my + 0.15 * s], 200, 340, fill=OUT, width=lw)
    for sx in (-1, 1):
        x0 = mx + (0.005 if sx > 0 else -0.085) * s
        d.rounded_rectangle([x0, my - 0.06 * s, x0 + 0.08 * s, my + 0.06 * s], radius=int(0.02 * s),
                            fill=(255, 255, 255), outline=OUT, width=max(2, lw // 2))

    # cap
    d.chord([*U(-0.78, -2.48), *U(0.78, -1.72)], 180, 360, fill=CAP, outline=OUT, width=lw)
    d.rounded_rectangle([*U(-0.82, -2.12), *U(0.95, -2.0)], radius=int(0.05 * s), fill=CAP_D, outline=OUT, width=lw)
    ell(d, *U(0, -2.32), 0.13 * s, 0.09 * s, (255, 255, 255), outline=None)
    text_center(d, *U(0, -2.32), "B", font(FONT_XB, int(0.13 * s)), CAP)

    # arms
    for side, key in ((-1, "lhand"), (1, "rhand")):
        sh = U(side * 0.72, -0.55)
        hx_, hy_ = p[key]
        hp = U(hx_, hy_)
        d.line([sh, hp], fill=OUT, width=int(0.3 * s) + 2 * lw)
        d.line([sh, hp], fill=FUR, width=int(0.3 * s))
        ell(d, *sh, 0.15 * s, 0.15 * s, FUR, outline=None)
        if side == 1 and p.get("wrench") is not None:
            ang = p["wrench"]
            ca, sa = math.cos(ang), math.sin(ang)
            L, wdt = 0.75 * s, 0.07 * s
            ex_, ey_ = hp[0] + ca * L, hp[1] + sa * L
            poly = [(hp[0] - sa * wdt, hp[1] + ca * wdt), (ex_ - sa * wdt, ey_ + ca * wdt),
                    (ex_ + sa * wdt, ey_ - ca * wdt), (hp[0] + sa * wdt, hp[1] - ca * wdt)]
            d.polygon(poly, fill=(170, 175, 185), outline=(60, 60, 70), width=lw)
            ell(d, ex_, ey_, 0.15 * s, 0.15 * s, (170, 175, 185), outline=(60, 60, 70), w=lw)
            ell(d, ex_ + ca * 0.08 * s, ey_ + sa * 0.08 * s, 0.07 * s, 0.07 * s, p["bg_at_jaw"], outline=None)
        ell(d, *hp, 0.2 * s, 0.2 * s, GLOVE, w=lw)
        if side == 1 and p.get("thumbs"):
            ell(d, hp[0] + 0.02 * s, hp[1] - 0.24 * s, 0.08 * s, 0.14 * s, GLOVE, w=lw)


# ---------------------------------------------------------------- backgrounds
def kitchen():
    im = Image.new("RGB", (WW, HH), (250, 241, 226))
    d = ImageDraw.Draw(im)
    # window with sky
    d.rectangle([90, 300, 640, 1000], fill=(255, 255, 255))
    d.rectangle([115, 325, 615, 975], fill=(170, 215, 245))
    ell(d, 470, 470, 70, 40, (255, 255, 255), outline=None)
    ell(d, 530, 450, 60, 35, (255, 255, 255), outline=None)
    d.line([365, 325, 365, 975], fill=(255, 255, 255), width=18)
    d.line([115, 650, 615, 650], fill=(255, 255, 255), width=18)
    # upper cabinets
    for x in range(760, 1440, 330):
        d.rounded_rectangle([x, 120, x + 300, 820], radius=12, fill=(255, 255, 255), outline=(215, 205, 190), width=6)
        d.rounded_rectangle([x + 125, 720, x + 175, 740], radius=8, fill=(180, 170, 160))
    # backsplash tiles
    for y in range(900, 1580, 70):
        d.line([0, y, WW, y], fill=(232, 222, 205), width=3)
    # counter
    d.rectangle([0, 1580, WW, 1640], fill=(165, 170, 178))
    d.rectangle([0, 1640, WW, 2260], fill=(255, 255, 255))
    for x in range(0, WW, 360):
        d.rectangle([x + 10, 1670, x + 350, 2230], outline=(215, 205, 190), width=6)
        d.rounded_rectangle([x + 150, 1700, x + 210, 1720], radius=8, fill=(180, 170, 160))
    d.rectangle([0, 2260, WW, HH], fill=(196, 152, 110))
    for x in range(0, WW, 240):
        d.line([x, 2260, x, HH], fill=(176, 134, 95), width=4)
    # sink basin + faucet (gooseneck)
    d.rounded_rectangle([880, 1560, 1360, 1610], radius=20, fill=(120, 125, 135))
    d.rectangle([1090, 1380, 1130, 1580], fill=(190, 195, 205), outline=(90, 95, 105), width=5)
    d.arc([1090, 1280, 1290, 1480], 180, 360, fill=(190, 195, 205), width=40)
    d.rectangle([1250, 1380, 1290, 1420], fill=(190, 195, 205), outline=(90, 95, 105), width=5)
    d.rounded_rectangle([1060, 1555, 1160, 1585], radius=10, fill=(150, 155, 165))
    # plant
    d.rectangle([180, 1440, 300, 1580], fill=(220, 120, 80))
    for a in range(-60, 61, 30):
        r = math.radians(a - 90)
        d.polygon(rot_poly(240 + 90 * math.cos(r), 1420 + 90 * math.sin(r), 90, 28, r), fill=(80, 160, 90))
    return im


FAUCET_TIP = (1270, 1430)
FAUCET_BASE = (1110, 1500)


def living_room():
    im = Image.new("RGB", (WW, HH), (244, 238, 228))
    d = ImageDraw.Draw(im)
    for i, x in enumerate((180, 620, 1060)):
        d.rectangle([x, 900, x + 260, 1220], fill=(255, 255, 255), outline=(200, 185, 165), width=12)
        d.rectangle([x + 30, 930, x + 230, 1190], fill=[(200, 220, 230), (225, 215, 200), (205, 225, 210)][i])
    d.rounded_rectangle([60, 1500, 1380, 1900], radius=60, fill=(225, 222, 216))
    for x, c in ((180, (240, 200, 90)), (480, (150, 180, 215)), (860, (150, 180, 215)), (1160, (240, 200, 90))):
        d.rounded_rectangle([x, 1400, x + 220, 1620], radius=40, fill=c)
    d.rectangle([0, 1900, WW, HH], fill=(190, 150, 112))
    return im.filter(ImageFilter.GaussianBlur(28))


# ---------------------------------------------------------------- audio
def read_wav(path):
    with wave.open(path) as w:
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return data


def build_audio(vo_path, tmp):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", vo_path, "-ac", "1", "-ar", str(SR), f"{tmp}/vo.wav"], check=True)
    vo = read_wav(f"{tmp}/vo.wav")
    n = int(DUR * SR)
    voice = np.zeros(n, np.float32)

    # split the voiceover at its pauses: L1 | L2 | L3
    env = np.convolve(np.abs(vo), np.ones(int(0.03 * SR)) / int(0.03 * SR), mode="same")
    def quiet_point(a, b):
        i0, i1 = int(a * SR), int(b * SR)
        return (i0 + int(np.argmin(env[i0:i1]))) / SR
    c1 = quiet_point(1.4, 1.8)
    c2 = quiet_point(5.2, 5.7)
    c_mid = quiet_point(2.8, 4.0)  # "fixes it fast." | "No mess, no stress!"
    segs = [(0.0, c1, 0.6), (c1, c2, 5.0), (c2, len(vo) / SR, 11.0)]
    for a, b, at in segs:
        chunk = vo[int(a * SR):int(b * SR)]
        i = int(at * SR)
        voice[i:i + len(chunk)] += chunk[: n - i]
    l2_mid = 5.0 + (c_mid - c1)
    l2_end = 5.0 + (c2 - c1)
    l1_end = 0.6 + c1

    # music: I-V-vi-IV in C, 120 bpm
    t = np.arange(n) / SR
    music = np.zeros(n, np.float32)
    beat = 0.5
    chords = [[261.6, 329.6, 392.0], [196.0, 246.9, 293.7], [220.0, 261.6, 329.6], [174.6, 220.0, 261.6]]
    for k in range(int(DUR / beat)):
        t0 = k * beat
        i0 = int(t0 * SR)
        seg = t[i0:i0 + int(beat * SR)] - t0
        ch = chords[(k // 4) % 4]
        env_p = np.exp(-seg * 6)
        tone = sum(np.sin(2 * np.pi * f * seg) + 0.3 * np.sin(4 * np.pi * f * seg) for f in ch) / 3
        music[i0:i0 + len(seg)] += 0.22 * env_p * tone
        bass = ch[0] / 2
        music[i0:i0 + len(seg)] += 0.25 * np.exp(-seg * 4) * np.sin(2 * np.pi * bass * seg)
        # kick
        kick = np.sin(2 * np.pi * (60 + 120 * np.exp(-seg * 30)) * seg) * np.exp(-seg * 14)
        music[i0:i0 + len(seg)] += 0.35 * kick
        # hat on off-beat
        h0 = i0 + int(beat / 2 * SR)
        hl = int(0.05 * SR)
        if h0 + hl < n:
            music[h0:h0 + hl] += 0.06 * np.random.default_rng(k).standard_normal(hl) * np.exp(-np.arange(hl) / SR * 80)
    fade = np.clip(np.minimum(t / 0.3, (DUR - t) / 1.0), 0, 1)
    music *= fade

    # duck music under the voice
    venv = np.convolve(np.abs(voice), np.ones(int(0.2 * SR)) / int(0.2 * SR), mode="same")
    duck = 1 - 0.55 * np.clip(venv / 0.03, 0, 1)

    sfx = np.zeros(n, np.float32)
    for td in DRIP_TIMES:
        i = int((td + DRIP_FALL) * SR)
        L = int(0.12 * SR)
        s_ = np.arange(L) / SR
        sfx[i:i + L] += 0.25 * np.sin(2 * np.pi * (1400 - 4000 * s_) * s_) * np.exp(-s_ * 30)
    for k, f in enumerate((1318.5, 1568.0, 2093.0)):  # sparkle "ding" when fixed
        i = int((FIX_T + 0.08 * k) * SR)
        L = int(0.6 * SR)
        s_ = np.arange(L) / SR
        sfx[i:i + L] += 0.12 * np.sin(2 * np.pi * f * s_) * np.exp(-s_ * 6)

    mix = voice * 1.0 + music * 0.32 * duck + sfx
    mix /= max(1.0, np.abs(mix).max() / 0.95)
    with wave.open(f"{tmp}/mix.wav", "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())

    # per-frame mouth openness from the voice envelope
    fr = np.arange(int(DUR * FPS))
    menv = np.array([np.abs(voice[int(f / FPS * SR): int((f + 1) / FPS * SR)]).mean() for f in fr])
    mouth = np.clip(menv / (menv.max() * 0.55), 0, 1)
    return mouth, (l1_end, l2_mid, l2_end)


DRIP_TIMES = [0.3, 1.3, 2.3, 3.3, 4.6, 5.6]  # drip stops after the fix
DRIP_FALL = 0.45
FIX_T = 7.0


# ---------------------------------------------------------------- captions
def caption(d, s, t, t0, y):
    """Pop-in caption."""
    a = smooth((t - t0) / 0.18)
    size = int((70 + 18 * (1 - a)) * SS) if a < 1 else 70 * SS
    f = font(FONT_XB, size)
    lines = s.split("\n")
    for i, line in enumerate(lines):
        text_center(d, WW / 2, y + i * 92 * SS, line, f, (255, 255, 255), stroke=7 * SS, stroke_fill=(15, 15, 20))


# ---------------------------------------------------------------- render
def main():
    vo_path, out = sys.argv[1], sys.argv[2]
    tmp = "/".join(out.split("/")[:-1]) or "."
    mouth, (l1_end, l2_mid, l2_end) = build_audio(vo_path, tmp)
    kit = kitchen()
    room = living_room()

    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-i", f"{tmp}/mix.wav", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
         "-c:a", "aac", "-b:a", "192k", "-shortest", out], stdin=subprocess.PIPE)

    phone = "555.014.2200"
    for fi in range(int(DUR * FPS)):
        t = fi / FPS
        blink = 1.0 if (t % 3.1) < 0.12 else 0.0
        bob = math.sin(t * 2 * math.pi * 0.9) * 0.02
        p = dict(mouth=float(mouth[fi]), blink=blink)
        zoom = 1.0

        if t < 4.5:  # scene 1: worried next to dripping faucet
            im = kit.copy()
            d = ImageDraw.Draw(im)
            cx, cy, s = 0.36 * WW, 0.71 * HH + bob * 340, 340
            p.update(brow="worried", look=keys(t, [(0, 1.0), (1.6, 1.0), (2.0, 0.0)]),
                     lhand=keys(t, [(0, (-1.0, 0.25)), (1.6, (-1.0, 0.25)), (2.1, (-0.22, -1.02))]),
                     rhand=(1.0, 0.25))
            zoom = 1.0 + 0.04 * t / 4.5
        elif t < 10.0:  # scene 2: fixes the faucet with a wrench
            im = kit.copy()
            d = ImageDraw.Draw(im)
            cx, cy, s = 0.5 * WW, 0.71 * HH + bob * 340, 340
            fixing = t < FIX_T + 0.4
            reach = ((FAUCET_BASE[0] - cx) / s - 0.62, (FAUCET_BASE[1] - cy) / s + 0.12)
            rest_thumb = (0.98, -0.75)
            rh = keys(t, [(4.5, (1.0, 0.25)), (4.9, reach), (FIX_T + 0.4, reach), (FIX_T + 1.0, rest_thumb)])
            p.update(brow="happy" if t >= FIX_T else "worried", look=1.0 if fixing else 0.0,
                     lhand=(-0.98, 0.15), rhand=rh,
                     wrench=(math.sin((t - 4.9) * 9) * 0.35 - 0.2) if (4.9 < t < FIX_T + 0.4) else None,
                     thumbs=t > FIX_T + 0.9, bg_at_jaw=(250, 241, 226))
            zoom = 1.06 + 0.03 * (t - 4.5) / 5.5
        else:  # scene 3: end card
            im = room.copy()
            d = ImageDraw.Draw(im)
            cx, cy, s = 0.5 * WW, 0.86 * HH + bob * 380, 380
            g = math.sin((t - 10) * 5)
            p.update(brow="happy", look=0.0,
                     lhand=keys(t, [(10, (-1.0, 0.2)), (10.4, (-1.15, -0.7 + 0.15 * g))]) if t < 13.4 else (-1.0, 0.2),
                     rhand=keys(t, [(10, (1.0, 0.2)), (10.5, (1.1, -0.4)), (13.3, (1.1, -0.4)), (13.7, (0.98, -0.75))]),
                     thumbs=t > 13.6)

        draw_beaver(d, cx, cy, s, p)

        # drips + water (scenes 1-2)
        if t < 10.0:
            for td in DRIP_TIMES:
                k = (t - td) / DRIP_FALL
                if 0 <= k <= 1:
                    y = FAUCET_TIP[1] + 20 + k * k * 120
                    ell(d, FAUCET_TIP[0], y, 12, 18, (110, 180, 235), outline=(60, 120, 190), w=3)
                elif 1 < k < 1.5:
                    r = (k - 1) * 120
                    d.arc([FAUCET_TIP[0] - r, 1560 - r * 0.3, FAUCET_TIP[0] + r, 1560 + r * 0.3], 180, 360,
                          fill=(110, 180, 235), width=5)
        if FIX_T <= t < FIX_T + 1.2:  # sparkles
            k = (t - FIX_T) / 1.2
            for j, (ox, oy) in enumerate(((-90, -80), (80, -120), (130, 30), (-40, 60))):
                r = 40 * math.sin(k * math.pi)
                x, y = FAUCET_TIP[0] + ox, FAUCET_TIP[1] + oy
                d.polygon([(x, y - r), (x + r * 0.25, y), (x, y + r), (x - r * 0.25, y)], fill=(255, 230, 80))
                d.polygon([(x - r, y), (x, y - r * 0.25), (x + r, y), (x, y + r * 0.25)], fill=(255, 230, 80))

        # captions (top area, away from IG UI)
        cap_y = 330 * SS
        if 0.6 <= t < l1_end + 0.5:
            caption(d, "LEAKY SINK?", t, 0.6, cap_y)
        elif 5.0 <= t < l2_mid:
            caption(d, "FIXED FAST!", t, 5.0, cap_y)
        elif l2_mid <= t < l2_end + 0.6:
            caption(d, "NO MESS.\nNO STRESS.", t, l2_mid, cap_y)

        # end-card graphics
        if t >= 10.0:
            a = smooth((t - 10.0) / 0.35)
            band_y = 0.17 * HH
            d.rectangle([0, band_y - 70 * SS, WW * a, band_y + 70 * SS], fill=(28, 62, 170))
            if a > 0.6:
                sc = smooth((t - 10.2) / 0.3)
                ow, oh = 300 * SS * sc, 120 * SS * sc
                d.ellipse([WW / 2 - ow, band_y - oh, WW / 2 + ow, band_y + oh], fill=(255, 255, 255),
                          outline=(28, 62, 170), width=8 * SS)
                if sc > 0.9:
                    text_center(d, WW / 2, band_y - 22 * SS, "Benny's", font(FONT_XB, 92 * SS), (28, 62, 170))
                    text_center(d, WW / 2, band_y + 62 * SS, "PLUMBING", font(FONT_XB, 34 * SS), (232, 120, 30))
            n_chars = int(max(0, min(len(phone), (t - 11.0) / 1.2 * len(phone))))
            if n_chars:
                text_center(d, WW / 2, 0.31 * HH, phone[:n_chars], font(FONT_B, 62 * SS), NAVY)
            if t >= 13.0:
                k = smooth((t - 13.0) / 0.25)
                text_center(d, WW / 2, 0.385 * HH, "Call Today", font(FONT_XB, int(56 * SS * (0.6 + 0.4 * k))), NAVY)

        if zoom != 1.0:
            cw, ch = WW / zoom, HH / zoom
            x0, y0 = (WW - cw) / 2, (HH - ch) * 0.45
            im = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch)))
        frame = im.resize((W, H), Image.LANCZOS)
        ff.stdin.write(frame.tobytes())

    ff.stdin.close()
    ff.wait()


if __name__ == "__main__":
    main()
