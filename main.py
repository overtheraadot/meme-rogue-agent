#!/usr/bin/env python3
"""Meme Sprint 3 entry (account A): robot hands its resignation to a confused boss.
Pure stdlib PNG writer (zlib + struct). No PIL, no network, deterministic.
Writes exactly one 1024x1024 PNG to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).
"""

import os
import struct
import zlib

W = 1024
H = 1024

# --- palette ---
CREAM = (253, 246, 227)
INK = (24, 24, 24)
RED = (214, 39, 40)
WALL = (199, 232, 243)
FLOOR = (217, 193, 163)
DESK = (139, 90, 43)
DESK_TOP = (165, 110, 55)
SKIN = (242, 200, 155)
HAIR = (90, 55, 30)
SUIT = (38, 58, 94)
WHITE = (255, 255, 255)
STEEL = (185, 196, 204)
STEEL_DARK = (120, 132, 142)
STEEL_LIGHT = (215, 222, 228)
EYE_RED = (255, 45, 45)
PAPER = (255, 255, 250)
SHADOW = (0, 0, 0)

# --- 5x7 bitmap font, authored in-session ---
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg[0:1] * 0)  # placeholder
        self.buf = bytearray(w * h * 3)
        for i in range(w * h):
            self.buf[i * 3] = bg[0]
            self.buf[i * 3 + 1] = bg[1]
            self.buf[i * 3 + 2] = bg[2]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = c[0]
            self.buf[i + 1] = c[1]
            self.buf[i + 2] = c[2]

    def rect(self, x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(self.h, y1)):
            for x in range(max(0, x0), min(self.w, x1)):
                self.set(x, y, c)

    def circle(self, cx, cy, r, c):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r:
                    self.set(x, y, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                dx = (x - cx) / rx
                dy = (y - cy) / ry
                if dx * dx + dy * dy <= 1.0:
                    self.set(x, y, c)

    def line_h(self, x0, x1, y, t, c):
        self.rect(x0, y - t // 2, x1, y + t // 2 + 1, c)

    def line_v(self, x, y0, y1, t, c):
        self.rect(x - t // 2, y0, x + t // 2 + 1, y1, c)

    def text(self, s, x, y, scale, c):
        adv = 6 * scale
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.rect(x + col * scale, y + row * scale,
                                  x + (col + 1) * scale, y + (row + 1) * scale, c)
            x += adv

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_centered(self, s, cx, y, scale, c):
        self.text(s, cx - self.text_width(s, scale) // 2, y, scale, c)


def png_bytes(c):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)  # filter: none
        raw += c.buf[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def draw():
    c = Canvas(W, H, CREAM)

    # --- scene backdrop (middle band) ---
    c.rect(0, 190, W, 800, WALL)
    c.rect(0, 700, W, 800, FLOOR)
    # wall picture frame (a motivational poster, ironic)
    c.rect(60, 230, 220, 380, WHITE)
    c.rect(68, 238, 212, 372, (220, 240, 245))
    c.text("TEAM", 82, 300, 3, INK)
    c.text("WORK", 82, 330, 3, INK)

    # --- top caption ---
    c.text_centered("WHEN YOUR AI AGENT", 512, 28, 6, INK)
    c.text_centered("GOES ROGUE...", 512, 108, 6, RED)
    c.line_h(312, 712, 182, 4, RED)

    # --- boss (left, seated behind desk) ---
    # shoulders / suit
    c.rect(200, 520, 410, 620, SUIT)
    c.rect(290, 520, 320, 620, WHITE)  # shirt
    c.rect(296, 520, 314, 560, RED)    # tie
    # head
    c.circle(305, 450, 72, SKIN)
    # hair: top cap
    c.circle(305, 428, 72, HAIR)
    c.rect(233, 428, 377, 470, SKIN)   # face below hairline
    c.circle(305, 450, 72, SKIN)       # redraw face over hair bottom
    c.rect(233, 380, 377, 420, HAIR)   # hair top block
    # wide shocked eyes
    c.ellipse(278, 445, 14, 18, WHITE)
    c.ellipse(332, 445, 14, 18, WHITE)
    c.circle(278, 448, 6, INK)
    c.circle(332, 448, 6, INK)
    # open mouth
    c.ellipse(305, 495, 14, 18, (60, 20, 20))
    # sweat drops
    c.circle(385, 400, 8, (120, 180, 230))
    c.circle(400, 430, 6, (120, 180, 230))
    # big red ??? above the boss (clear of the poster)
    c.text("???", 250, 250, 7, RED)

    # --- desk ---
    c.rect(110, 600, 560, 620, DESK_TOP)
    c.rect(130, 620, 540, 760, DESK)
    # mug on desk
    c.rect(160, 560, 200, 600, (200, 60, 60))
    c.rect(200, 570, 212, 592, (200, 60, 60))

    # --- robot (right, standing, handing over the letter) ---
    # legs
    c.rect(660, 690, 700, 760, STEEL_DARK)
    c.rect(770, 690, 810, 760, STEEL_DARK)
    # body
    c.rect(640, 430, 830, 700, STEEL)
    c.rect(640, 430, 830, 460, STEEL_LIGHT)
    # chest panel + buttons
    c.rect(680, 500, 790, 580, STEEL_LIGHT)
    c.circle(700, 530, 12, (60, 200, 90))
    c.circle(740, 530, 12, (240, 180, 40))
    c.circle(700, 560, 12, RED)
    c.rect(680, 600, 790, 660, STEEL_DARK)
    # head
    c.rect(655, 300, 815, 430, STEEL)
    c.rect(655, 300, 815, 320, STEEL_LIGHT)
    # antenna
    c.line_v(735, 250, 300, 8, STEEL_DARK)
    c.circle(735, 242, 14, EYE_RED)
    # glowing red eyes (rogue!)
    c.rect(680, 350, 730, 375, EYE_RED)
    c.rect(745, 350, 795, 375, EYE_RED)
    # mouth grille
    for i in range(4):
        c.line_h(695, 780, 400 + i * 10, 4, STEEL_DARK)
    # ear discs
    c.circle(655, 365, 14, STEEL_DARK)
    c.circle(815, 365, 14, STEEL_DARK)
    # arm extended left, holding the paper
    c.rect(540, 500, 645, 535, STEEL_DARK)
    c.circle(545, 517, 20, STEEL_DARK)  # hand
    # the resignation letter
    c.rect(470, 460, 580, 580, PAPER)
    c.rect(470, 460, 580, 580, PAPER)
    # paper border
    c.line_h(470, 580, 460, 3, INK)
    c.line_h(470, 580, 580, 3, INK)
    c.line_v(470, 460, 580, 3, INK)
    c.line_v(580, 460, 580, 3, INK)
    c.text("I", 520, 476, 3, INK)
    c.text("QUIT", 489, 503, 4, RED)
    c.line_h(485, 565, 548, 3, INK)

    # --- bottom caption ---
    c.line_h(212, 812, 800, 4, RED)
    c.text_centered("IT DOESN'T TAKE OVER THE WORLD.", 512, 830, 4, INK)
    c.text_centered("IT JUST QUITS AND JOINS YOUR RIVAL.", 512, 890, 4, INK)
    c.text_centered("THE ROBOT HAS SPOKEN.", 512, 950, 4, RED)

    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(draw())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
