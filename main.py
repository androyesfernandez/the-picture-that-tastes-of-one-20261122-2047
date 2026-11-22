#!/usr/bin/env python3
"""The picture that tastes of one ingredient.

One hero image, drawn entirely in code: a steaming bowl of ramen in a
deep-red lacquer bowl -- golden broth, chilli-oil gloss, wavy noodles,
charred chashu, a soft egg with a molten yolk, spring onions, sesame,
nori, and chopsticks lifting a noodle swirl through rising steam, lit
warm against a dark wooden table.

PIL + standard library only. No network, no stock photos, no text in
the picture. Writes /output/entry.png (1024 x 1024, under 1 MiB).
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

random.seed(20261122)

SIZE = 1024
SS = 2                      # supersampling: draw at 2048, downscale
W = SIZE * SS
OUT = "/output/entry.png"

# The bowl sits dead centre; the broth surface is an ellipse at this
# height, so every topping is placed relative to it.
BX, BY = 512, 612           # broth centre (in 1024-space)
BRX, BRY = 300, 102          # broth radii


def s(v):
    """Scale a 1024-space coordinate to the supersampled canvas."""
    return int(round(v * SS))


def mix(c1, c2, t):
    """Linear blend of two RGB colours."""
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * t)) for i in range(3))


def mixa(c1, c2, t):
    """Linear blend of two RGBA colours."""
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * t)) for i in range(4))


def rect(x0, y0, x1, y1):
    return [s(x0), s(y0), s(x1), s(y1)]


def oval(x0, y0, x1, y1):
    """Corner coordinates of an ellipse's bounding box."""
    return [s(x0), s(y0), s(x1), s(y1)]


def point(x, y):
    return (s(x), s(y))


# ------------------------------------------------------------------ canvas
canvas = Image.new("RGB", (W, W), (20, 11, 6))
pen = ImageDraw.Draw(canvas, "RGBA")

# Backdrop: a warm vertical fall from near-black umber at the top to
# ember brown at the bottom, with a soft golden halo behind the bowl.
for yy in range(W):
    f = yy / W
    if f < 0.5:
        col = mix((16, 9, 5), (44, 23, 10), f / 0.5)
    else:
        col = mix((44, 23, 10), (72, 38, 16), (f - 0.5) / 0.5)
    pen.line([(0, yy), (W, yy)], fill=col)

halo = Image.new("RGBA", (W, W), (0, 0, 0, 0))
hp = ImageDraw.Draw(halo)
for rr in range(580, 0, -10):
    a = int(52 * (1 - rr / 580) ** 2)
    hp.ellipse(oval(512 - rr, 560 - rr * 0.8, 512 + rr, 560 + rr * 0.8),
               fill=(255, 168, 64, a))
halo = halo.filter(ImageFilter.GaussianBlur(s(64)))
canvas.paste(Image.alpha_composite(canvas.convert("RGBA"), halo).convert("RGB"), (0, 0))
pen = ImageDraw.Draw(canvas, "RGBA")

# ------------------------------------------------------------------ table
# Dark wood below y=712, with a soft horizon and faint long grain.
for yy in range(s(712), W):
    f = (yy - s(712)) / (W - s(712))
    col = mix((54, 31, 15), (28, 16, 8), f)
    pen.line([(0, yy), (W, yy)], fill=col)
for _ in range(110):
    gy = random.uniform(724, 1012)
    gx = random.uniform(-60, 1024)
    gl = random.uniform(140, 460)
    pen.line([point(gx, gy), point(gx + gl, gy + random.uniform(-4, 4))],
             fill=(10, 6, 3, random.randint(12, 30)), width=s(2))
# Pool of shadow under the bowl.
sh = Image.new("RGBA", (W, W), (0, 0, 0, 0))
sp = ImageDraw.Draw(sh)
sp.ellipse(oval(512 - 350, 906, 512 + 350, 962), fill=(0, 0, 0, 160))
sh = sh.filter(ImageFilter.GaussianBlur(s(28)))
canvas.paste(Image.alpha_composite(canvas.convert("RGBA"), sh).convert("RGB"), (0, 0))
pen = ImageDraw.Draw(canvas, "RGBA")

# ------------------------------------------------------------------ bowl
# Lacquer body: a half-ellipse belly under the rim, darkening towards
# the foot, with a glossy sweep of light on the left flank.
belly_top, belly_rx, belly_ry = 648, 336, 268
for yy in range(belly_top, belly_top + belly_ry + 1):
    f = (yy - belly_top) / belly_ry
    half = belly_rx * math.sqrt(max(0.0, 1 - f * f))
    col = mix((158, 38, 18), (58, 10, 6), f)
    pen.line([point(512 - half, yy), point(512 + half, yy)], fill=col, width=s(2))
# Foot ring: a thin dark ellipse where the bowl meets the table.
pen.ellipse(oval(512 - 148, 892, 512 + 148, 916), outline=(30, 8, 5), width=s(5))
pen.ellipse(oval(512 - 148, 892, 512 + 148, 916), outline=(140, 40, 20, 90), width=s(2))
# Gloss on the belly.
gl = Image.new("RGBA", (W, W), (0, 0, 0, 0))
gp = ImageDraw.Draw(gl)
gp.ellipse(oval(232, 668, 428, 856), fill=(255, 122, 72, 56))
gl = gl.filter(ImageFilter.GaussianBlur(s(24)))
canvas.paste(Image.alpha_composite(canvas.convert("RGBA"), gl).convert("RGB"), (0, 0))
pen = ImageDraw.Draw(canvas, "RGBA")

# Rim: dark lacquer edge, cream band, inner shadow ring.
pen.ellipse(oval(512 - 342, 474, 512 + 342, 742), fill=(92, 15, 8))
pen.ellipse(oval(512 - 326, 488, 512 + 326, 728), fill=(240, 216, 178))
pen.ellipse(oval(512 - 310, 500, 512 + 310, 716), fill=(70, 11, 6))

# ------------------------------------------------------------------ broth
# Amber broth: dark spiced edge melting into a glowing golden heart.
for i in range(48):
    f = i / 47
    col = mix((142, 72, 13), (234, 166, 60), f)
    k = 1 - f * 0.30
    pen.ellipse(oval(BX - BRX * k, BY - BRY * k, BX + BRX * k, BY + BRY * k), fill=col)
# Meniscus ring hugging the rim.
pen.ellipse(oval(BX - 296, BY - 98, BX + 296, BY + 98),
            outline=(118, 54, 10), width=s(5))
# Golden oil sheen: bright flecks scattered over the surface.
for _ in range(260):
    a = random.uniform(0, 2 * math.pi)
    r = random.uniform(0.06, 0.92)
    fx = BX + math.cos(a) * BRX * r
    fy = BY + math.sin(a) * BRY * r
    ww = random.uniform(3, 12)
    hh = ww * random.uniform(0.35, 0.6)
    pen.ellipse(oval(fx - ww, fy - hh, fx + ww, fy + hh),
                fill=(255, 216, 132, random.randint(28, 84)))
# Chilli-oil beads: deep red gloss drops with a bright catch-light.
for _ in range(28):
    a = random.uniform(0, 2 * math.pi)
    r = random.uniform(0.15, 0.86)
    fx = BX + math.cos(a) * BRX * r
    fy = BY + math.sin(a) * BRY * r
    ww = random.uniform(4, 10)
    pen.ellipse(oval(fx - ww, fy - ww * 0.55, fx + ww, fy + ww * 0.55),
                fill=(176, 30, 8, 214))
    pen.ellipse(oval(fx - ww * 0.45, fy - ww * 0.42, fx + ww * 0.15, fy - ww * 0.06),
                fill=(255, 122, 72, 190))

# ------------------------------------------------------------------ noodles
def wavy(x0, x1, yb, amp, ph, colour, width, waves=2.3):
    """One wavy noodle strand across the broth."""
    pts = []
    for i in range(45):
        t = i / 44
        pts.append(point(x0 + (x1 - x0) * t,
                         yb + math.sin(t * math.pi * waves + ph) * amp))
    pen.line(pts, fill=colour, width=s(width), joint="curve")


for col, wd in (((150, 96, 30), 7), ((246, 208, 130), 5), ((255, 238, 182), 2)):
    n = 34 if wd == 7 else (30 if wd == 5 else 18)
    for _ in range(n):
        wavy(random.uniform(248, 422), random.uniform(598, 772),
             random.uniform(548, 654), random.uniform(6, 15),
             random.uniform(0, 6.28), col, wd)

# ------------------------------------------------------------------ toppings
# Nori: a dark green-black sheet standing at the back, tilted, with a
# faint sheen stripe down its face.
nori = Image.new("RGBA", (W, W), (0, 0, 0, 0))
np_ = ImageDraw.Draw(nori)
np_.rounded_rectangle(rect(650, 424, 726, 558), radius=s(9),
                      fill=(16, 34, 19, 236))
np_.line([point(666, 434), point(666, 550)], fill=(72, 112, 72, 72), width=s(5))
nori = nori.rotate(-4, resample=Image.BICUBIC, center=point(688, 558))
canvas.paste(Image.alpha_composite(canvas.convert("RGBA"), nori).convert("RGB"), (0, 0))
pen = ImageDraw.Draw(canvas, "RGBA")


def chashu(cx, cy, r):
    """One seared pork round: pink-brown heart, caramelised edge,
    pale fat marbling and a gloss catch-light."""
    for i in range(28):
        f = i / 27
        col = mix((144, 82, 50), (224, 160, 114), f)
        k = 1 - f * 0.24
        pen.ellipse(oval(cx - r * k, cy - r * 0.82 * k,
                         cx + r * k, cy + r * 0.82 * k), fill=col)
    pen.ellipse(oval(cx - r, cy - r * 0.82, cx + r, cy + r * 0.82),
                outline=(94, 46, 25), width=s(4))
    # Caramelised outer ring: a darker band just inside the edge.
    pen.ellipse(oval(cx - r * 0.94, cy - r * 0.77, cx + r * 0.94, cy + r * 0.77),
                outline=(122, 62, 30, 200), width=s(7))
    for a0 in (25, 135, 255):
        pen.arc(oval(cx - r * 0.62, cy - r * 0.5, cx + r * 0.62, cy + r * 0.5),
                a0, a0 + 68, fill=(242, 206, 172, 190), width=s(5))
    pen.ellipse(oval(cx - r * 0.36, cy - r * 0.52, cx - r * 0.04,
                     cy - r * 0.28), fill=(255, 222, 182, 170))


chashu(392, 600, 76)
chashu(452, 636, 62)

# Soft egg: ivory white with a glossy molten yolk.
pen.ellipse(oval(598, 550, 720, 644), fill=(250, 244, 228))
pen.ellipse(oval(598, 550, 720, 644), outline=(212, 194, 166), width=s(3))
for i in range(24):
    f = i / 23
    col = mix((224, 108, 15), (255, 180, 62), f)
    k = 1 - f * 0.26
    pen.ellipse(oval(659 - 35 * k, 597 - 31 * k, 659 + 35 * k, 597 + 31 * k), fill=col)
pen.ellipse(oval(642, 574, 668, 590), fill=(255, 234, 172, 224))
pen.ellipse(oval(598, 550, 720, 644), outline=(118, 88, 58, 90), width=s(2))

# Spring-onion rings: bright green discs with a paler heart.
for _ in range(17):
    a = random.uniform(0, 2 * math.pi)
    r = random.uniform(0.2, 0.9)
    fx = BX + math.cos(a) * BRX * r
    fy = BY + math.sin(a) * BRY * r
    rr = random.uniform(6, 10)
    pen.ellipse(oval(fx - rr, fy - rr * 0.7, fx + rr, fy + rr * 0.7),
                fill=(44, 126, 50))
    pen.ellipse(oval(fx - rr * 0.55, fy - rr * 0.38, fx + rr * 0.55, fy + rr * 0.38),
                fill=(142, 202, 92))
    pen.ellipse(oval(fx - rr * 0.2, fy - rr * 0.14, fx + rr * 0.2, fy + rr * 0.14),
                fill=(58, 138, 58))

# Sesame seeds and chilli flakes.
for _ in range(36):
    a = random.uniform(0, 2 * math.pi)
    r = random.uniform(0.1, 0.9)
    fx = BX + math.cos(a) * BRX * r
    fy = BY + math.sin(a) * BRY * r
    pen.ellipse(oval(fx - 3, fy - 1.6, fx + 3, fy + 1.6),
                fill=(246, 230, 192, 224))
for _ in range(11):
    a = random.uniform(0, 2 * math.pi)
    r = random.uniform(0.15, 0.85)
    fx = BX + math.cos(a) * BRX * r
    fy = BY + math.sin(a) * BRY * r
    pen.polygon([point(fx, fy - 5), point(fx + 4, fy + 2), point(fx - 4, fy + 3)],
                fill=(192, 42, 14, 232))

# ------------------------------------------------------------------ chopsticks
# Two wooden chopsticks sweeping in from the top right, lifting a
# swirl of noodles out of the broth.
def stick(x0, y0, x1, y1):
    pen.line([point(x0, y0), point(x1, y1)], fill=(86, 50, 21), width=s(17),
             joint="curve")
    pen.line([point(x0, y0 - 4), point(x1, y1 - 4)], fill=(200, 142, 82), width=s(6),
             joint="curve")
    pen.ellipse(oval(x1 - 8, y1 - 8, x1 + 8, y1 + 8), fill=(86, 50, 21))


stick(752, 104, 602, 450)
stick(794, 128, 630, 468)

# Lifted swirl: strands hanging from the chopstick tips, catching the
# light along their length.
for k in range(9):
    off = (k - 4) * 7
    pts = []
    for i in range(41):
        t = i / 40
        pts.append(point(608 + off + math.sin(t * math.pi * 1.2 + k * 0.7) * 9,
                         454 + (568 - 454) * t))
    pen.line(pts, fill=(246, 208, 130) if k % 2 else (226, 178, 96),
             width=s(6), joint="curve")
for k in range(5):
    off = (k - 2) * 8
    pts = []
    for i in range(31):
        t = i / 30
        pts.append(point(610 + off + math.sin(t * math.pi * 1.2 + k) * 7,
                         456 + 108 * t))
    pen.line(pts, fill=(255, 240, 188), width=s(2), joint="curve")

# ------------------------------------------------------------------ steam
# Four soft white ribbons rising from the broth, each with one slow
# S-curve, blurred until they are breath rather than line.
steam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
sd = ImageDraw.Draw(steam)
for sx, sway, wd, al in [(398, 16, 30, 72), (472, 20, 38, 88),
                         (548, 18, 34, 78), (622, 14, 28, 64)]:
    pts = []
    for i in range(61):
        t = i / 60
        pts.append(point(sx + math.sin(t * math.pi * 1.1 + sx * 0.7) * sway,
                         482 - t * 302))
    sd.line(pts, fill=(255, 255, 255, al), width=s(wd), joint="curve")
steam = steam.filter(ImageFilter.GaussianBlur(s(20)))
canvas.paste(Image.alpha_composite(canvas.convert("RGBA"), steam).convert("RGB"), (0, 0))

# ------------------------------------------------------------------ finish
# Warm vignette: darken the corners so the eye stays on the bowl.
vig = Image.new("L", (W, W), 0)
vd = ImageDraw.Draw(vig)
vd.ellipse(oval(512 - 642, 512 - 642, 512 + 642, 512 + 642), fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(s(180)))
dark = Image.new("RGB", (W, W), (8, 4, 2))
canvas = Image.composite(canvas, dark, vig.point(lambda v: 255 - int((255 - v) * 0.42)))

canvas = canvas.resize((SIZE, SIZE), Image.LANCZOS)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT, optimize=True)
print("wrote", OUT, os.path.getsize(OUT), "bytes,", canvas.size)
