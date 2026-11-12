# Generates concept blueprint sheets for a 40 x 50 ft north-front plot.
# Room sizes are wall-center to wall-center, matching the approved layout.

import os
from xml.sax.saxutils import escape

OUT = os.path.dirname(os.path.abspath(__file__))

INK = "#22282c"
MUTED = "#5c6a72"
ACCENT = "#8f4d38"
PAPER = "#fbf9f6"
HALL = "#f3eee4"
BED = "#f7f4ee"
COOK = "#f6efd8"
BATH = "#e4eef1"
PASS = "#f7f5f1"
STAIR = "#ece6dc"
STORE = "#f1ebe1"
PORCH = "#e9e2d6"
SIT = "#f3eee4"
BALC = "#e6eef3"
TERR = "#e4f0e6"
LINEN = "#f1ebe1"

OUTER = 11
INNER = 6


def fti(feet):
    inches = int(round(float(feet) * 12))
    sign = "-" if inches < 0 else ""
    inches = abs(inches)
    feet_i, inch = divmod(inches, 12)
    return f"{sign}{feet_i}'-{inch}\""


def segments(a, b, gaps):
    gaps = sorted((min(g0, g1), max(g0, g1)) for g0, g1 in gaps)
    out = []
    cur = a
    for g0, g1 in gaps:
        g0 = max(g0, a)
        g1 = min(g1, b)
        if g1 <= g0:
            continue
        if g0 > cur + 0.02:
            out.append((cur, g0))
        cur = max(cur, g1)
    if b > cur + 0.02:
        out.append((cur, b))
    return out


class Sheet:
    def __init__(self, width=1700, height=1180):
        self.w = width
        self.h = height
        self.s = 20
        self.ox = 108
        self.oy = 72
        self.p = []

    def X(self, ft):
        return self.ox + ft * self.s

    def Y(self, ft):
        return self.oy + ft * self.s

    def add(self, svg):
        self.p.append(svg)

    def line(self, x1, y1, x2, y2, stroke=INK, width=2, cap="square", dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<line x1="{self.X(x1):.2f}" y1="{self.Y(y1):.2f}" x2="{self.X(x2):.2f}" '
            f'y2="{self.Y(y2):.2f}" stroke="{stroke}" stroke-width="{width}" '
            f'stroke-linecap="{cap}"{extra}/>'
        )

    def line_px(self, x1, y1, x2, y2, stroke=INK, width=1.4, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{stroke}" stroke-width="{width}" stroke-linecap="square"{extra}/>'
        )

    def rect(self, x, y, w, h, fill="none", stroke="none", sw=1, dash=None, extra=""):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<rect x="{self.X(x):.2f}" y="{self.Y(y):.2f}" width="{w * self.s:.2f}" '
            f'height="{h * self.s:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d} {extra}/>'
        )

    def rect_px(self, x, y, w, h, fill="none", stroke="none", sw=1, extra=""):
        self.add(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'
        )

    def text(self, x, y, value, size=13, fill=INK, anchor="middle", weight="600", extra=""):
        self.add(
            f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" {extra}>{escape(str(value))}</text>'
        )

    def text_ft(self, fx, fy, value, size=13, fill=INK, anchor="middle", weight="600", dy=0):
        self.text(self.X(fx), self.Y(fy) + dy, value, size, fill, anchor, weight)

    def label(self, fx, fy, name, size_txt=None, fs=14):
        self.text_ft(fx, fy, name, size=fs, weight="650")
        if size_txt:
            self.text_ft(fx, fy, size_txt, size=fs - 3, fill=MUTED, weight="500", dy=15)

    def hwall(self, y, x1, x2, gaps=(), weight=INNER):
        for a, b in segments(x1, x2, gaps):
            self.line(a, y, b, y, INK, weight)

    def vwall(self, x, y1, y2, gaps=(), weight=INNER):
        for a, b in segments(y1, y2, gaps):
            self.line(x, a, x, b, INK, weight)

    def window_h(self, y, x1, x2, mullions=0):
        for dy in (-0.13, 0, 0.13):
            self.line(x1 + 0.06, y + dy, x2 - 0.06, y + dy, INK, 1.25, "butt")
        if mullions:
            step = (x2 - x1) / (mullions + 1)
            for i in range(1, mullions + 1):
                mx = x1 + step * i
                self.line(mx, y - 0.28, mx, y + 0.28, INK, 2.2)

    def window_v(self, x, y1, y2, mullions=0):
        for dx in (-0.13, 0, 0.13):
            self.line(x + dx, y1 + 0.06, x + dx, y2 - 0.06, INK, 1.25, "butt")
        if mullions:
            step = (y2 - y1) / (mullions + 1)
            for i in range(1, mullions + 1):
                my = y1 + step * i
                self.line(x - 0.28, my, x + 0.28, my, INK, 2.2)

    def door(self, hx, hy, cdx, cdy, odx, ody):
        """Hinge (hx, hy). Offsets in feet to the closed latch and the open latch."""
        cx, cy = hx + cdx, hy + cdy
        ox, oy = hx + odx, hy + ody
        r = math_hypot(cdx, cdy)
        cross = cdx * ody - cdy * odx
        sweep = 1 if cross > 0 else 0
        self.line(hx, hy, ox, oy, INK, 1.6, "butt")
        self.add(
            f'<path d="M {self.X(cx):.2f} {self.Y(cy):.2f} A {r * self.s:.2f} {r * self.s:.2f} '
            f'0 0 {sweep} {self.X(ox):.2f} {self.Y(oy):.2f}" fill="none" stroke="{MUTED}" '
            f'stroke-width="1.15"/>'
        )

    def column(self, fx, fy, kind="rcc"):
        s = 0.72
        if kind == "rcc":
            self.rect(fx - s / 2, fy - s / 2, s, s, fill=ACCENT, stroke=ACCENT, sw=1)
        else:
            self.rect(fx - s / 2, fy - s / 2, s, s, fill=PORCH, stroke=ACCENT, sw=1.6)

    def dim_h(self, x1, x2, y_feat, y_line, text, ext=18):
        X1, X2 = self.X(x1), self.X(x2)
        yf = self.Y(y_feat)
        self.line_px(X1, yf, X1, y_line, MUTED, 0.8)
        self.line_px(X2, yf, X2, y_line, MUTED, 0.8)
        self.line_px(X1, y_line, X2, y_line, MUTED, 0.9)
        tick(self, X1, y_line)
        tick(self, X2, y_line)
        self.text((X1 + X2) / 2, y_line - 5, text, size=11, fill=MUTED, weight="600")

    def dim_v(self, y1, y2, x_feat, x_line, text):
        Y1, Y2 = self.Y(y1), self.Y(y2)
        xf = self.X(x_feat)
        self.line_px(xf, Y1, x_line, Y1, MUTED, 0.8)
        self.line_px(xf, Y2, x_line, Y2, MUTED, 0.8)
        self.line_px(x_line, Y1, x_line, Y2, MUTED, 0.9)
        tick(self, x_line, Y1, vertical=True)
        tick(self, x_line, Y2, vertical=True)
        cy = (Y1 + Y2) / 2
        tx = x_line - 12
        self.text(tx, cy, text, size=11, fill=MUTED, weight="600",
                  extra=f'transform="rotate(-90 {tx:.1f} {cy:.1f})"')

    def north_arrow(self, cx, cy):
        self.add(f'<circle cx="{cx}" cy="{cy}" r="22" fill="none" stroke="{INK}" stroke-width="1.4"/>')
        self.add(
            f'<polygon points="{cx},{cy - 16} {cx - 7},{cy + 8} {cx},{cy + 2} {cx + 7},{cy + 8}" '
            f'fill="{ACCENT}"/>'
        )
        self.text(cx, cy + 38, "NORTH", size=11, fill=INK, weight="700")

    def scale_bar(self, x, y, feet=10):
        px = feet * self.s
        self.line_px(x, y, x + px, y, INK, 2)
        self.line_px(x, y - 5, x, y + 5, INK, 1.4)
        self.line_px(x + px, y - 5, x + px, y + 5, INK, 1.4)
        mid = x + px / 2
        self.line_px(mid, y - 4, mid, y + 4, INK, 1)
        self.text(x, y + 16, "0", size=10, fill=MUTED, weight="600")
        self.text(mid, y + 16, fti(feet / 2), size=10, fill=MUTED, weight="600")
        self.text(x + px, y + 16, fti(feet), size=10, fill=MUTED, weight="600")

    def chrome(self, sheet_no, sheet_title, sheets=5):
        self.rect_px(16, 16, self.w - 32, self.h - 32, fill="none", stroke=INK, sw=1.6)
        self.rect_px(22, 22, self.w - 44, self.h - 44, fill="none", stroke=INK, sw=0.6)
        top = self.h - 118
        self.rect_px(28, top, self.w - 56, 86, fill="#f7f4ef", stroke=INK, sw=1.1)
        self.rect_px(28, top, 8, 86, fill=ACCENT, stroke="none")
        self.text(48, top + 28, "GROUND FLOOR FOR A FUTURE BUNGALOW", size=18, anchor="start", weight="700")
        self.text(48, top + 50, sheet_title, size=13, anchor="start", weight="600", fill=ACCENT)
        self.text(
            48, top + 72,
            "40 ft × 50 ft plot  ·  road on the north  ·  November 2026  ·  concept drawing, not a permit set",
            size=11, anchor="start", weight="500", fill=MUTED,
        )
        bx = self.w - 118
        self.rect_px(bx, top + 12, 74, 62, fill="none", stroke=INK, sw=1)
        self.text(bx + 37, top + 36, f"{sheet_no:02d}", size=20, weight="700")
        self.text(bx + 37, top + 58, f"of {sheets:02d}", size=11, fill=MUTED, weight="600")

    def save(self, filename):
        body = "\n".join(self.p)
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">
  <rect width="100%" height="100%" fill="{PAPER}"/>
  <style>text {{ font-family: "Segoe UI", Helvetica, Arial, sans-serif; }}</style>
  {body}
</svg>
'''
        path = os.path.join(OUT, filename)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(svg)
        return path


def math_hypot(a, b):
    return (a * a + b * b) ** 0.5


def tick(sheet, x, y, vertical=False):
    if vertical:
        sheet.line_px(x - 4, y - 4, x + 4, y + 4, MUTED, 1)
    else:
        sheet.line_px(x - 4, y - 4, x + 4, y + 4, MUTED, 1)


def panel_header(sheet, x, y, title, width=520):
    sheet.rect_px(x, y, width, 26, fill=ACCENT, stroke="none")
    sheet.text(x + 12, y + 18, title, size=12, fill="#fffaf6", anchor="start", weight="700")
    return y + 26


def schedule_table(sheet, x, y, rows, width=520):
    y = panel_header(sheet, x, y, "ROOM SCHEDULE", width)
    sheet.rect_px(x, y, width, 22, fill="#f0ebe3", stroke=INK, sw=0.6)
    sheet.text(x + 12, y + 16, "Room", size=11, anchor="start", weight="700", fill=MUTED)
    sheet.text(x + width - 12, y + 16, "Center to center", size=11, anchor="end", weight="700", fill=MUTED)
    y += 22
    for i, (name, size) in enumerate(rows):
        bg = "#ffffff" if i % 2 == 0 else "#f7f4ef"
        sheet.rect_px(x, y, width, 22, fill=bg, stroke="#e4ddd4", sw=0.6)
        sheet.text(x + 12, y + 16, name, size=12, anchor="start", weight="600")
        sheet.text(x + width - 12, y + 16, size, size=12, anchor="end", weight="500", fill=MUTED)
        y += 22
    return y + 16


def note_block(sheet, x, y, title, lines, width=520):
    y = panel_header(sheet, x, y, title, width)
    sheet.rect_px(x, y, width, 18 * len(lines) + 14, fill="#fffdfb", stroke="#e4ddd4", sw=0.8)
    yy = y + 18
    for line in lines:
        sheet.text(x + 12, yy, line, size=11.5, anchor="start", weight="500", fill=INK)
        yy += 18
    return y + 18 * len(lines) + 28


def legend(sheet, x, y, width=520, posts=True):
    y = panel_header(sheet, x, y, "LEGEND", width)
    height = 78 if posts else 56
    sheet.rect_px(x, y, width, height, fill="#fffdfb", stroke="#e4ddd4", sw=0.8)
    sheet.rect_px(x + 16, y + 14, 12, 12, fill=ACCENT, stroke=ACCENT, sw=1)
    sheet.text(x + 38, y + 25, "RCC column, sized for this floor plus one future floor", size=12, anchor="start", weight="500")
    line_y = y + 66
    if posts:
        sheet.rect_px(x + 16, y + 40, 12, 12, fill=PORCH, stroke=ACCENT, sw=1.4)
        sheet.text(x + 38, y + 51, "Porch post on the beam", size=12, anchor="start", weight="500")
    else:
        line_y = y + 44
    sheet.line_px(x + 16, line_y, x + 32, line_y, INK, 4)
    sheet.text(x + 38, line_y + 4, "Wall    ·    arc shows the door swing    ·    triple line is a window", size=12, anchor="start", weight="500")
    return y + height + 16


def bed(sheet, x, y, w, h, head="s"):
    sheet.rect(x, y, w, h, fill="none", stroke="#9a9186", sw=1.3)
    if head == "s":
        sheet.line(x, y + h - 0.7, x + w, y + h - 0.7, "#9a9186", 1.2, "butt")
    elif head == "n":
        sheet.line(x, y + 0.7, x + w, y + 0.7, "#9a9186", 1.2, "butt")
    elif head == "w":
        sheet.line(x + 0.7, y, x + 0.7, y + h, "#9a9186", 1.2, "butt")
    elif head == "e":
        sheet.line(x + w - 0.7, y, x + w - 0.7, y + h, "#9a9186", 1.2, "butt")


def wc(sheet, x, y):
    sheet.rect(x, y, 1.25, 0.45, fill="none", stroke=MUTED, sw=1.2)
    cx, cy = sheet.X(x + 0.62), sheet.Y(y + 1.25)
    sheet.add(
        f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{0.62 * sheet.s:.1f}" ry="{0.72 * sheet.s:.1f}" '
        f'fill="none" stroke="{MUTED}" stroke-width="1.2"/>'
    )


def basin(sheet, x, y):
    sheet.rect(x, y, 1.6, 1.15, fill="none", stroke=MUTED, sw=1.2)
    cx, cy = sheet.X(x + 0.8), sheet.Y(y + 0.62)
    sheet.add(
        f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{0.42 * sheet.s:.1f}" ry="{0.32 * sheet.s:.1f}" '
        f'fill="none" stroke="{MUTED}" stroke-width="1.1"/>'
    )


def shower(sheet, x, y, s=2.4):
    sheet.rect(x, y, s, s, fill="none", stroke=MUTED, sw=1.2)
    sheet.line(x, y, x + s, y + s, MUTED, 0.8, "butt")
    sheet.line(x + s, y, x, y + s, MUTED, 0.8, "butt")


def counter(sheet, x, y, w, h):
    sheet.rect(x, y, w, h, fill="#f3e7c8", stroke="#a89880", sw=1.1)


def cooktop(sheet, x, y):
    for dx in (0.35, 1.15):
        for dy in (0.35, 1.15):
            cx, cy = sheet.X(x + dx), sheet.Y(y + dy)
            sheet.add(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.28 * sheet.s:.1f}" fill="none" stroke="{MUTED}" stroke-width="1.1"/>'
            )


def stair_well(sheet, x, y, label="UP", flight="west"):
    """Dogleg in a 10 x 10 well. Landing on the south. North end is the entry/exit."""
    sheet.rect(x + 0.55, y + 0.45, 2.9, 6.6, fill="none", stroke="#b5ab9f", sw=0.8)
    sheet.rect(x + 6.55, y + 0.45, 2.9, 6.6, fill="none", stroke="#b5ab9f", sw=0.8)
    for i in range(8):
        yy = y + 0.7 + i * 0.78
        sheet.line(x + 0.7, yy, x + 3.3, yy, "#b5ab9f", 0.9, "butt")
        sheet.line(x + 6.7, yy, x + 9.3, yy, "#b5ab9f", 0.9, "butt")
    sheet.line(x + 0.7, y + 7.3, x + 9.3, y + 7.3, "#9a9186", 1.1, "butt")
    if flight == "west":
        ax = x + 2.0
        sheet.add(
            f'<polygon points="{sheet.X(ax):.1f},{sheet.Y(y + 6.3):.1f} '
            f'{sheet.X(ax - 0.28):.1f},{sheet.Y(y + 5.4):.1f} '
            f'{sheet.X(ax + 0.28):.1f},{sheet.Y(y + 5.4):.1f}" fill="{ACCENT}"/>'
        )
        sheet.line(ax, y + 1.3, ax, y + 5.5, ACCENT, 1.4, "butt")
        sheet.text_ft(x + 5, y + 4.2, label, size=12, fill=ACCENT, weight="700")
    else:
        ax = x + 8.0
        sheet.add(
            f'<polygon points="{sheet.X(ax):.1f},{sheet.Y(y + 6.3):.1f} '
            f'{sheet.X(ax - 0.28):.1f},{sheet.Y(y + 5.4):.1f} '
            f'{sheet.X(ax + 0.28):.1f},{sheet.Y(y + 5.4):.1f}" fill="{ACCENT}"/>'
        )
        sheet.line(ax, y + 1.2, ax, y + 5.5, ACCENT, 1.4, "butt")
        sheet.text_ft(x + 4.2, y + 3.6, label, size=12, fill=ACCENT, weight="700")


def railing_h(sheet, y, x1, x2):
    sheet.line(x1, y - 0.08, x2, y - 0.08, INK, 1.4, "butt")
    sheet.line(x1, y + 0.08, x2, y + 0.08, INK, 1.4, "butt")
    x = x1
    while x <= x2 + 0.01:
        sheet.line(x, y - 0.12, x, y + 0.12, INK, 1.1, "butt")
        x += 0.85


def railing_v(sheet, x, y1, y2):
    sheet.line(x - 0.08, y1, x - 0.08, y2, INK, 1.4, "butt")
    sheet.line(x + 0.08, y1, x + 0.08, y2, INK, 1.4, "butt")
    y = y1
    while y <= y2 + 0.01:
        sheet.line(x - 0.12, y, x + 0.12, y, INK, 1.1, "butt")
        y += 0.85


def columns_for(sheet, extra=True, posts=True):
    xs = (0, 10.5, 15.5, 22, 34)
    ys = (0, 12, 22, 32, 42)
    for x in xs:
        for y in ys:
            sheet.column(x, y, "rcc")
    if extra:
        sheet.column(25.5, 32, "rcc")
        sheet.column(25.5, 42, "rcc")
    if posts:
        sheet.column(23, 0, "post")
        sheet.column(31, 0, "post")


def draw_ground(variant="A"):
    s = Sheet()
    s.s = 20
    s.ox = 96
    s.oy = 64

    b = variant == "B"
    kitchen_name = "Store" if b else "Kitchen"
    se_name = "Kitchen" if b else "Store"
    kitchen_fill = STORE if b else COOK
    se_fill = COOK if b else STORE

    # Rooms
    s.rect(10.5, 0, 23.5, 12, fill=HALL)
    s.rect(23, 0, 8, 4, fill=PORCH)
    s.rect(0, 0, 10.5, 12, fill=BED)
    s.rect(0, 12, 10.5, 10, fill=BED)
    s.rect(0, 22, 10.5, 10, fill=BED)
    s.rect(15.5, 12, 6.5, 10, fill=STORE if b else "#f8f3e8")
    s.rect(22, 12, 12, 10, fill=kitchen_fill)
    s.rect(10.5, 12, 5, 20, fill=PASS)
    s.rect(15.5, 22, 6.5, 3, fill=PASS)
    s.rect(15.5, 25, 6.5, 7, fill=BATH)
    s.rect(22, 22, 12, 10, fill=BED)
    s.rect(0, 32, 10.5, 10, fill=BED)
    s.rect(10.5, 36, 5, 6, fill=BED)
    s.rect(0, 32, 5, 7, fill=BATH)
    s.rect(10.5, 32, 5, 4, fill=PASS)
    s.rect(15.5, 32, 10, 10, fill=STAIR)
    s.rect(25.5, 32, 8.5, 10, fill=se_fill)

    # Steps in the front setback
    s.rect(23.4, -2.15, 7.2, 2.15, fill="#e3ddd4", stroke="#cfc6ba", sw=0.8)
    s.line(23.4, -0.7, 30.6, -0.7, "#cfc6ba", 1, "butt")
    s.line(23.4, -1.4, 30.6, -1.4, "#cfc6ba", 1, "butt")

    # Outer walls
    s.hwall(0, 0, 23, gaps=[(3, 7), (11.2, 14.6), (16.2, 20.4)], weight=OUTER)
    s.hwall(0, 31, 34, weight=OUTER)
    s.hwall(4, 23, 31, gaps=[(25.5, 29)], weight=OUTER)
    s.vwall(23, 0, 4, weight=OUTER)
    s.vwall(31, 0, 4, weight=OUTER)
    s.line(23, 0, 31, 0, INK, 3, "butt")  # porch fascia
    s.vwall(0, 0, 42, gaps=[(2.6, 6.4), (14, 18), (24, 28), (33.2, 35.6)], weight=OUTER)
    east_gaps = [(24.4, 28.6)]
    if b:
        east_gaps += [(14.6, 18.2), (34.4, 38.4)]
    else:
        east_gaps += [(14.4, 18.6)]
    s.vwall(34, 0, 42, gaps=east_gaps, weight=OUTER)
    south_gaps = [(6.4, 11.2), (17.8, 22.2)]
    if b:
        south_gaps.append((27.6, 32.2))
    else:
        south_gaps.append((27.8, 32.2))
    s.hwall(42, 0, 34, gaps=south_gaps, weight=OUTER)

    # Internal walls
    s.hwall(12, 0, 10.5)
    s.hwall(12, 15.5, 22, gaps=[(16.4, 20.6)])
    s.hwall(12, 22, 34, gaps=[(23.3, 26.3)])
    s.hwall(22, 0, 10.5)
    s.hwall(22, 15.5, 22)
    s.hwall(22, 22, 34)
    s.hwall(25, 15.5, 22)
    s.hwall(32, 0, 10.5)
    s.hwall(32, 15.5, 25.5)
    s.hwall(32, 25.5, 34)
    s.hwall(36, 10.5, 15.5)
    s.hwall(39, 0, 5)
    s.vwall(10.5, 0, 12, gaps=[(7.6, 10.6)])
    s.vwall(10.5, 12, 22, gaps=[(13.2, 16.2)])
    s.vwall(10.5, 22, 32, gaps=[(23.2, 26.2)])
    s.vwall(10.5, 32, 36, gaps=[(32.5, 35.5)])
    s.vwall(15.5, 12, 22, gaps=[(13.4, 16.4)])
    s.vwall(15.5, 25, 32, gaps=[(26.2, 29.2)])
    s.vwall(15.5, 36, 42)
    s.vwall(5, 32, 39, gaps=[(33.2, 36.2)])
    s.vwall(22, 12, 22, gaps=[(14.2, 17.2)])
    s.vwall(22, 22, 25, gaps=[(22.25, 24.9)])
    s.vwall(22, 25, 32)
    s.vwall(25.5, 32, 42, gaps=[(38.1, 41.1)])

    # Windows
    s.window_h(0, 3, 7)
    s.window_h(0, 11.2, 14.6)
    s.window_h(0, 16.2, 20.4, mullions=0)
    s.window_v(0, 2.6, 6.4)
    s.window_v(0, 14, 18)
    s.window_v(0, 24, 28)
    s.window_v(0, 33.2, 35.6)
    s.window_h(42, 6.4, 11.2)
    s.window_h(42, 17.8, 22.2)
    if b:
        s.window_v(34, 14.6, 18.2)
        s.window_v(34, 34.4, 38.4)
        s.window_h(42, 27.6, 32.2)
    else:
        s.window_v(34, 14.4, 18.6)
        s.window_h(42, 27.8, 32.2)
    s.window_v(34, 24.4, 28.6)

    # Doors
    s.door(25.5, 4, 3.5, 0, 0, 3.5)          # main door, into the hall
    s.door(10.5, 7.6, 0, 3, -3, 0)           # bed 5
    s.door(10.5, 13.2, 0, 3, -3, 0)          # bed 4
    s.door(10.5, 23.2, 0, 3, -3, 0)          # bed 3
    s.door(23.3, 12, 3, 0, 0, 3)             # hall to kitchen/store
    s.door(22, 14.2, 0, 3, -3, 0)            # pantry to kitchen/store
    s.door(15.5, 13.4, 0, 3, -3, 0)          # passage to pantry
    s.door(15.5, 26.2, 0, 3, 3, 0)           # common bath
    s.door(22, 22.25, 0, 2.65, 2.65, 0)      # bedroom 2
    s.door(10.5, 32.5, 0, 3, -3, 0)          # master
    s.door(5, 33.2, 0, 3, -3, 0)             # master bath
    s.door(25.5, 38.1, 0, 3, 3, 0)           # store or kitchen from the stair landing

    # Furniture and fittings
    s.rect(11.4, 2.4, 1.8, 5.2, fill="none", stroke="#9a9186", sw=1.2)  # sofa
    s.line(12.6, 2.7, 12.6, 7.3, "#9a9186", 1, "butt")
    s.rect(14.2, 3.6, 2.6, 1.6, fill="none", stroke="#9a9186", sw=1.1)  # table
    s.rect(23.6, 7.6, 5.2, 3.4, fill="none", stroke="#9a9186", sw=1.2)  # dining
    s.rect(31.55, 0.55, 2.15, 1.7, fill="#f3e2b8", stroke=ACCENT, sw=1)
    s.text_ft(32.6, 1.55, "Pooja", size=9, fill=ACCENT, weight="700")

    bed(s, 1.3, 6.6, 5.6, 4.6, "s")
    bed(s, 1.4, 16.6, 6.2, 4.6, "s")
    bed(s, 1.4, 26.6, 6.2, 4.6, "s")
    bed(s, 23.2, 23.6, 4.6, 6.4, "w")
    bed(s, 6.6, 37.2, 6.4, 4.2, "s")

    if b:
        # shelves in the store beside the hall
        for i in range(4):
            s.line(32.2, 13 + i * 1.6, 33.7, 13 + i * 1.6, "#c2b6a4", 1, "butt")
        counter(s, 32.1, 32.5, 1.7, 5.2)
        counter(s, 29.2, 40.1, 4.5, 1.7)
        cooktop(s, 32.3, 33.2)
        cx, cy = s.X(31.4), s.Y(40.9)
        s.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="7" fill="none" stroke="{MUTED}" stroke-width="1.1"/>')
    else:
        counter(s, 32.05, 12.5, 1.75, 8.8)
        cooktop(s, 32.25, 13.3)
        cx, cy = s.X(32.9), s.Y(17.2)
        s.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="7" fill="none" stroke="{MUTED}" stroke-width="1.1"/>')

    shower(s, 0.35, 32.35, 2.15)
    wc(s, 2.7, 32.4)
    shower(s, 19.2, 29.2, 2.3)
    wc(s, 16.0, 28.7)
    basin(s, 16.1, 25.45)

    stair_well(s, 15.5, 32, "UP", "west")

    # Labels
    s.label(17.2, 5.15, "Hall", "23'-6\" × 12'-0\"", 16)
    s.text_ft(27, 2.35, "Porch", size=11, fill=MUTED, weight="700")
    s.label(5.25, 3.15, "Bedroom 5", "10'-6\" × 12'-0\"", 12)
    s.label(5.25, 14.15, "Bedroom 4", "10'-6\" × 10'-0\"", 12)
    s.label(5.25, 23.7, "Bedroom 3", "10'-6\" × 10'-0\"", 12)
    s.label(18.75, 16.6, "Pantry", "6'-6\" × 10'-0\"", 12)
    s.label(27.6, 17.3, kitchen_name, "12'-0\" × 10'-0\"", 14)
    s.label(28.4, 26.6, "Bedroom 2", "12'-0\" × 10'-0\"", 13)
    s.label(18.75, 28.7, "Bathroom", "6'-6\" × 7'-0\"", 11)
    s.label(12.8, 39.2, "Master", "about 10'-6\" × 10'", 12)
    s.label(2.5, 36.6, "Bath", "5'-0\" × 7'-0\"", 10)
    s.label(29.8, 36.2, se_name, "8'-6\" × 10'-0\"", 13)
    cx, cy = s.X(13), s.Y(21.5)
    s.text(cx, cy, "Passage  5'-0\"", size=11, fill=MUTED, weight="700",
           extra=f'transform="rotate(-90 {cx:.1f} {cy:.1f})"')

    columns_for(s)

    # Dimensions
    chain = [(0, 10.5, "10'-6\""), (10.5, 15.5, "5'-0\""), (15.5, 22, "6'-6\""), (22, 34, "12'-0\"")]
    for x1, x2, label in chain:
        s.dim_h(x1, x2, 42, 978, label)
    s.dim_h(0, 34, 42, 1018, "34'-0\"  overall")
    vchain = [(0, 12, "12'-0\""), (12, 22, "10'-0\""), (22, 32, "10'-0\""), (32, 42, "10'-0\"")]
    for y1, y2, label in vchain:
        s.dim_v(y1, y2, 0, 74, label)
    s.dim_v(0, 42, 0, 48, "42'-0\"")

    s.north_arrow(1630, 120)
    s.text(1630, 168, "Road side", size=11, fill=MUTED, weight="600")

    # Side panel
    px = 800
    rows = [
        ("Hall", "23'-6\" × 12'-0\""),
        ("Porch, recessed", "8'-0\" × 4'-0\""),
        ("Bedroom 5, northwest", "10'-6\" × 12'-0\""),
        ("Bedroom 4", "10'-6\" × 10'-0\""),
        ("Bedroom 3", "10'-6\" × 10'-0\""),
        ("Bedroom 2", "12'-0\" × 10'-0\""),
        ("Master bedroom", "about 10'-6\" × 10'-0\""),
        ("Master bathroom", "5'-0\" × 7'-0\""),
        ("Common bathroom", "6'-6\" × 7'-0\""),
        ("Pantry", "6'-6\" × 10'-0\""),
        (kitchen_name, "12'-0\" × 10'-0\""),
        (se_name + (" , southeast" if b else ""), "8'-6\" × 10'-0\""),
        ("Staircase, dogleg", "10'-0\" × 10'-0\""),
        ("Passage", "5'-0\" wide"),
    ]
    y = schedule_table(s, px, 64, rows, 760)
    y = legend(s, px, y, 760)
    if b:
        notes = [
            "Same footprint, columns, and stair as Option A. The kitchen and the store trade places.",
            "The kitchen is in the southeast corner, with windows on the east and the south.",
            "Reach it from the hall by the passage, the short link, and the stair landing.",
            "The 12 ft × 10 ft room beside the hall is the store. The pantry stays between them.",
            "Choose this sheet when the cooking place should sit in the southeast.",
            "A 3 ft entry in front of the common bath lets Bedroom 2 open off the passage.",
            "Sizes are center-to-center. Usable carpet is about 6 to 9 inches less each way.",
            "A licensed structural engineer must confirm footings, columns, and the staircase before construction.",
        ]
        title = "OPTION B  ·  KITCHEN IN THE SOUTHEAST"
        note_w = 760
    else:
        notes = [
            "Daily layout. The kitchen opens off the hall, beside the dining table.",
            "Main door on the north, east of center, in a 4 ft recessed porch.",
            "Pooja shelf in the northeast corner of the hall.",
            "A 3 ft entry in front of the common bath lets Bedroom 2 open off the passage.",
            "The common bath is internal. Give it an exhaust fan. The master bath has a west window.",
            "The dogleg stair is built now. It is the way up to the future floor.",
            "Columns sit on the wall grid. Extra columns mark the stair and store corner.",
            "Footings and the plinth beam are for this floor plus one future floor. Leave starter bars above the slab.",
            "Sizes are center-to-center. Usable carpet is about 6 to 9 inches less each way.",
            "A licensed structural engineer must confirm footings, columns, and the staircase before construction.",
        ]
        title = "OPTION A  ·  GROUND FLOOR  ·  THE ONE TO BUILD"
        note_w = 760
    note_block(s, px, y, "NOTES", notes, note_w)

    s.chrome(3 if b else 2, title)
    s.scale_bar(1120, 1110)
    name = "03-ground-floor-option-b.svg" if b else "02-ground-floor-option-a.svg"
    return s.save(name)


def draw_first():
    s = Sheet()
    s.s = 20
    s.ox = 96
    s.oy = 64

    s.rect(0, 0, 10.5, 22, fill=BED)
    s.rect(10.5, 0, 23.5, 4, fill=BALC)
    s.rect(10.5, 4, 23.5, 8, fill=SIT)
    s.rect(10.5, 12, 11.5, 10, fill=SIT)
    s.rect(22, 12, 12, 17, fill=BED)
    s.rect(10.5, 22, 5, 7, fill=PASS)
    s.rect(15.5, 22, 6.5, 7, fill=BATH)
    s.rect(10.5, 29, 23.5, 3, fill=PASS)
    s.rect(0, 22, 10.5, 20, fill=BED)
    s.rect(0, 35, 5, 7, fill=BATH)
    s.rect(10.5, 32, 5, 10, fill=LINEN)
    s.rect(15.5, 32, 10, 10, fill=STAIR)
    s.rect(25.5, 32, 8.5, 10, fill=TERR)

    # terrace hatch
    s.add(
        '<pattern id="terr" patternUnits="userSpaceOnUse" width="9" height="9" patternTransform="rotate(45)">'
        '<line x1="0" y1="0" x2="0" y2="9" stroke="#b7cbb8" stroke-width="1.2"/>'
        "</pattern>"
    )
    s.add(
        f'<rect x="{s.X(25.5):.1f}" y="{s.Y(32):.1f}" width="{8.5 * s.s:.1f}" height="{10 * s.s:.1f}" fill="url(#terr)"/>'
    )

    # Outer walls. North edge of the balcony is a railing.
    s.hwall(0, 0, 10.5, gaps=[(3, 7)], weight=OUTER)
    railing_h(s, 0, 10.5, 34)
    s.vwall(0, 0, 42, gaps=[(3.2, 7.2), (14.2, 18.2), (24, 28), (36.2, 39.4)], weight=OUTER)
    s.vwall(34, 4, 32, gaps=[(6, 10), (15, 19), (22.6, 26.6)], weight=OUTER)
    railing_v(s, 34, 32, 42)
    s.hwall(42, 0, 25.5, gaps=[(6.4, 10.2), (17.8, 22.2)], weight=OUTER)
    railing_h(s, 42, 25.5, 34)

    # Internal
    s.hwall(4, 10.5, 34, gaps=[(15, 28)])
    s.hwall(12, 22, 34)
    s.hwall(22, 0, 10.5)
    s.hwall(22, 15.5, 22)
    s.hwall(29, 15.5, 22)
    s.hwall(29, 22, 34)
    s.hwall(32, 10.5, 15.5)
    s.hwall(32, 15.5, 25.5, gaps=[(21.6, 25.2)])
    s.hwall(32, 25.5, 34, gaps=[(27.6, 30.2)])
    s.hwall(35, 0, 5)
    s.vwall(10.5, 0, 22, gaps=[(7.4, 10.4)])
    s.vwall(10.5, 22, 29, gaps=[(23.4, 26.4)])
    s.vwall(10.5, 32, 42, gaps=[(33.2, 36.2)])
    s.vwall(22, 12, 29, gaps=[(14, 17)])
    s.vwall(15.5, 22, 29, gaps=[(23.3, 26.3)])
    s.vwall(15.5, 32, 42)
    s.vwall(25.5, 32, 42)
    s.vwall(5, 35, 42, gaps=[(36.2, 39.2)])

    # Windows and the sliding door
    s.window_h(0, 3, 7)
    s.window_v(0, 3.2, 7.2)
    s.window_v(0, 14.2, 18.2)
    s.window_v(0, 24, 28)
    s.window_v(0, 36.2, 39.4)
    s.window_h(42, 6.4, 10.2)
    s.window_h(42, 17.8, 22.2)
    s.window_v(34, 6, 10, mullions=1)
    s.window_v(34, 15, 19)
    s.window_v(34, 22.6, 26.6)
    # sliding panels
    s.line(15, 4, 28, 4, INK, 2.4, "butt")
    s.line(21.5, 3.55, 21.5, 4.45, ACCENT, 1.4, "butt")
    s.text_ft(21.5, 5.35, "sliding door", size=10, fill=MUTED, weight="600")

    # Doors
    s.door(10.5, 7.4, 0, 3, -3, 0)       # bed 6
    s.door(22, 14, 0, 3, 3, 0)           # bed 8
    s.door(10.5, 23.4, 0, 3, -3, 0)      # bed 7
    s.door(15.5, 23.3, 0, 3, 3, 0)       # stacked bath
    s.door(5, 36.2, 0, 3, 3, 0)          # bath over master bath
    s.door(10.5, 33.2, 0, 3, -3, 0)      # linen
    s.door(27.6, 32, 2.6, 0, 0, -2.6)    # terrace, swing onto the landing

    stair_well(s, 15.5, 32, "DN", "east")
    shower(s, 16.0, 22.4, 2.2)
    wc(s, 19.3, 22.45)
    basin(s, 16.1, 26.3)
    shower(s, 0.35, 35.4, 2.15)
    wc(s, 2.55, 38.6)

    bed(s, 1.3, 12.4, 6.2, 4.8, "s")
    bed(s, 1.5, 28.4, 6.2, 4.8, "s")
    bed(s, 26.2, 18.5, 4.8, 6.6, "e")

    s.label(5.25, 4.4, "Bedroom 6", "10'-6\" × 22'-0\"", 13)
    s.label(22, 1.9, "Balcony", "recessed 4'-0\"", 13)
    s.label(22, 8.2, "Family sitting", "opens to the balcony", 15)
    s.label(28, 20.2, "Bedroom 8", "12'-0\" × 17'-0\"", 13)
    s.label(18.75, 25.2, "Bathroom", "over the bath below", 11)
    s.label(5.25, 25.4, "Bedroom 7", "10'-6\" × 20'-0\"", 12)
    s.label(2.5, 38.4, "Bath", "over master bath", 10)
    s.label(13, 36.6, "Linen", "5'-0\" × 10'-0\"", 11)
    s.label(29.8, 36.4, "Terrace", "open to sky", 13)
    s.text_ft(20, 30.55, "Landing", size=12, fill=MUTED, weight="700")

    columns_for(s, extra=True, posts=False)

    chain = [(0, 10.5, "10'-6\""), (10.5, 15.5, "5'-0\""), (15.5, 22, "6'-6\""), (22, 34, "12'-0\"")]
    for x1, x2, label in chain:
        s.dim_h(x1, x2, 42, 978, label)
    s.dim_h(0, 34, 42, 1018, "34'-0\"  overall")
    for y1, y2, label in ((0, 4, "4'-0\""), (4, 12, "8'-0\""), (12, 22, "10'-0\""), (22, 32, "10'-0\""), (32, 42, "10'-0\"")):
        s.dim_v(y1, y2, 0, 52, label)

    s.north_arrow(1630, 120)

    rows = [
        ("Balcony, recessed", "23'-6\" × 4'-0\""),
        ("Family sitting", "over the hall"),
        ("Bedroom 6, west front", "10'-6\" × 22'-0\""),
        ("Bedroom 7, west rear", "10'-6\" × 20'-0\""),
        ("Bath in Bedroom 7", "5'-0\" × 7'-0\""),
        ("Bedroom 8, east", "12'-0\" × 17'-0\""),
        ("Bathroom", "6'-6\" × 7'-0\""),
        ("Linen", "5'-0\" × 10'-0\""),
        ("Landing", "3'-0\" deep"),
        ("Staircase", "same well"),
        ("Open terrace", "8'-6\" × 10'-0\""),
    ]
    y = schedule_table(s, 800, 64, rows, 760)
    y = legend(s, 800, y, 760, posts=False)
    note_block(
        s, 800, y, "NOTES",
        [
            "Not built now. Same outer walls and the same column base as Option A.",
            "The balcony steps back 4 ft, so it stays inside today's building line.",
            "The bathroom drops onto the common bathroom. Bedroom 7's bath drops onto the master bath.",
            "The terrace is open over the ground-floor store, with a door from the landing.",
            "If Option B is the ground floor, this terrace sits over the kitchen instead.",
            "Until this floor is built, the ground-floor roof is a waterproof terrace.",
            "The present parapet comes off when these columns continue upward.",
            "A licensed structural engineer must confirm footings, columns, and the staircase before construction.",
        ],
        760,
    )
    s.chrome(4, "FUTURE FIRST FLOOR  ·  ON THE SAME BASE")
    s.scale_bar(1120, 1110)
    return s.save("04-future-first-floor.svg")


def draw_site():
    s = Sheet()
    s.s = 16
    s.ox = 150
    s.oy = 168

    # Road, north of the plot. Plot y = 0 is the north boundary.
    road_top = s.Y(0) - 78
    s.rect_px(s.X(0), road_top, 40 * s.s, 78, fill="#e5e2db", stroke="none")
    s.line_px(s.X(0), road_top + 39, s.X(40), road_top + 39, "#c5bfb4", 1.2, dash="7 8")
    s.text(s.X(20), road_top + 28, "NORTH ROAD", size=16, fill=MUTED, weight="700")
    s.text(s.X(20), road_top + 50, "40 ft frontage", size=12, fill=MUTED, weight="500")

    # Yard
    s.rect(0, 0, 40, 50, fill="#f3f6f0", stroke=INK, sw=2.4)
    # Building
    s.rect(3, 5, 34, 42, fill="#f6f1e8", stroke=INK, sw=2.2)
    # Porch notch, drawn inside the footprint
    s.rect(3 + 23, 5, 8, 4, fill="#e9e2d6", stroke=INK, sw=1.2)
    s.line(3 + 25.5, 5 + 4, 3 + 29, 5 + 4, ACCENT, 2.4, "butt")
    s.text_ft(3 + 17, 5 + 8, "HALL", size=12, fill=MUTED, weight="700")
    s.text_ft(3 + 27, 5 + 2.3, "DOOR", size=10, fill=ACCENT, weight="700")

    # Path and steps
    s.rect(28.2, 0, 4.1, 3.3, fill="#e6e0d6", stroke="none")
    s.rect(26.2, 3.3, 7.6, 1.7, fill="#ddd6cb", stroke="#cfc6ba", sw=0.8)

    # Gate on the north boundary
    s.line(0, 0, 28.2, 0, INK, 2.6, "butt")
    s.line(32.3, 0, 40, 0, INK, 2.6, "butt")
    s.rect(27.85, -0.35, 0.55, 0.7, fill=INK, stroke=INK, sw=0.5)
    s.rect(32.15, -0.35, 0.55, 0.7, fill=INK, stroke=INK, sw=0.5)
    s.door(28.2, 0, 4.1, 0, 0, -4.1)

    # Planters
    for px, label in ((22.4, ""), (35.6, "")):
        cx, cy = s.X(px), s.Y(2.3)
        s.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="14" fill="#d5e0cf" stroke="#7d9478" stroke-width="1.3"/>')
        s.add(f'<circle cx="{cx:.1f}" cy="{cy - 10:.1f}" r="9" fill="#edf3ea" stroke="#7d9478" stroke-width="1"/>')
    s.text_ft(8.5, 2.4, "Scooter", size=12, fill=MUTED, weight="600")

    # Yard labels
    s.text_ft(20, 3.0, "", size=1)
    s.text(s.X(12), s.Y(4.55), "5'-0\" front setback", size=12, fill="#3e6b48", weight="700")
    s.text(s.X(1.5), s.Y(26), "3'-0\"", size=12, fill="#3e6b48", weight="700",
           extra=f'transform="rotate(-90 {s.X(1.5):.1f} {s.Y(26):.1f})"')
    s.text(s.X(38.5), s.Y(26), "3'-0\"", size=12, fill="#3e6b48", weight="700",
           extra=f'transform="rotate(90 {s.X(38.5):.1f} {s.Y(26):.1f})"')
    s.text_ft(20, 48.55, "3'-0\" rear setback", size=12, fill="#3e6b48", weight="700")
    s.text_ft(20, 26, "BUILDING", size=16, weight="700")
    s.text_ft(20, 28.2, "34'-0\"  ×  42'-0\"", size=13, fill=MUTED, weight="600")

    # Dimensions outside the plot
    s.dim_h(0, 40, 0, s.Y(0) - 100, "40'-0\"")
    s.dim_v(0, 50, 0, 70, "50'-0\"")
    s.dim_v(5, 47, 3, 112, "42'-0\"")
    s.dim_h(3, 37, 47, s.Y(50) + 36, "34'-0\"")
    s.dim_h(0, 40, 50, s.Y(50) + 72, "40'-0\"  plot")

    s.north_arrow(s.X(40) + 70, s.Y(8))

    rows = [
        ("Plot", "40'-0\" × 50'-0\""),
        ("Plot area", "2,000 sq ft"),
        ("Road", "north side"),
        ("Front setback", "5'-0\""),
        ("Side setbacks", "3'-0\" each"),
        ("Rear setback", "3'-0\""),
        ("Building footprint", "34'-0\" × 42'-0\""),
        ("Built-up area", "1,428 sq ft"),
        ("Ground coverage", "about 71%"),
        ("Gate", "lined up on the door"),
    ]
    y = schedule_table(s, 980, 150, rows, 660)
    note_block(
        s, 980, y, "NOTES",
        [
            "North is the road. The 40 ft side is the frontage. Depth is 50 ft.",
            "The gate, the path, and the main door share one line, east of center.",
            "The 5 ft front yard holds the steps, two planters, and a scooter.",
            "A car does not fit in this front setback.",
            "Coverage is about 71 percent. If the local rule caps coverage",
            "near 60 to 65 percent, the footprint has to shrink.",
            "Setbacks vary by town. Confirm them before the footings are dug.",
            "A licensed structural engineer must confirm footings, columns,",
            "and the staircase before construction.",
        ],
        660,
    )
    s.chrome(1, "SITE PLAN  ·  SETBACKS, GATE, AND FOOTPRINT")
    s.scale_bar(1180, 1110)
    return s.save("01-site-plan.svg")


def draw_elevation():
    s = Sheet()
    # Elevation uses its own vertical axis (y up). Helpers below use pixels directly.
    sc = 30  # px per foot
    ox = 90
    ground = 860

    def X(ft):
        return ox + ft * sc

    def Y(height):
        return ground - height * sc

    def rect(x, h0, w, h, fill, stroke="none", sw=0):
        s.rect_px(X(x), Y(h0 + h), w * sc, h * sc, fill=fill, stroke=stroke, sw=sw)

    def txt(ft, height, value, size=13, fill=INK, anchor="middle", weight="600"):
        s.text(X(ft), Y(height), value, size=size, fill=fill, anchor=anchor, weight=weight)

    # Ground
    s.line_px(40, ground, 1280, ground, INK, 1.6)
    s.rect_px(40, ground, 1240, 18, fill="#e7efe4", stroke="none")

    future = "#8b99a1"

    # Present plinth
    rect(0, 0, 34, 2, "#a39b90")
    for i, h in enumerate((0.5, 1.05, 1.55)):
        s.line_px(X(0), Y(h), X(34), Y(h), "#8d867c", 0.7)

    # Wall
    rect(0, 2, 34, 10, "#f7f4ee", stroke=INK, sw=1.5)
    # Porch depth cue behind the columns
    rect(23, 2, 8, 7, "#ece4d6")

    # Sandstone sill band
    rect(-0.15, 4.55, 34.3, 0.45, "#c6a36a")

    # Windows
    def window(x, w, sill=5, head=9, panels=1):
        rect(x, sill, w, head - sill, "#d7e4ea", stroke=INK, sw=1.6)
        gap = w / panels
        for i in range(1, panels):
            s.line_px(X(x + gap * i), Y(head), X(x + gap * i), Y(sill), INK, 1.3)
        s.line_px(X(x), Y((sill + head) / 2), X(x + w), Y((sill + head) / 2), INK, 1.1)

    window(3, 4, panels=1)
    window(11.2, 3.4, panels=1)
    window(16.2, 4.2, panels=1)

    # Door
    rect(25.5, 2, 3.5, 7, "#6e422c", stroke="#4a2c1c", sw=1.4)
    s.line_px(X(25.7), Y(5.6), X(28.8), Y(5.6), "#e6d2bf", 1.2)
    s.line_px(X(27.25), Y(8.7), X(27.25), Y(2.3), "#e6d2bf", 1)
    # handle
    s.add(f'<circle cx="{X(28.35):.1f}" cy="{Y(5.2):.1f}" r="2.4" fill="#e6d2bf"/>')

    # Columns in front of the porch
    for cx in (23, 31):
        rect(cx, 2, 0.75, 7, "#f3efe6", stroke=INK, sw=1.4)
        rect(cx - 0.12, 2, 0.99, 0.35, "#a39b90")
        rect(cx - 0.08, 8.65, 0.91, 0.28, "#ded6ca", stroke=INK, sw=0.8)

    # Chajja
    rect(-0.55, 9.0, 35.1, 0.42, "#ddd4c6", stroke=INK, sw=1)
    s.line_px(X(-0.55), Y(9.0), X(34.55), Y(9.0), "#b7aea2", 3)

    # Slab and parapet
    s.line_px(X(-0.2), Y(12), X(34.2), Y(12), INK, 2.4)
    rect(0, 12, 34, 3, "#f7f4ee", stroke=INK, sw=1.4)
    rect(-0.25, 14.65, 34.5, 0.35, "#e4dcd0", stroke=INK, sw=1)

    # Future floor, sitting on this parapet. Drawn after the present house
    # so the dashed storey touches the coping instead of floating above it.
    s.line_px(X(0), Y(15), X(0), Y(25), future, 1.4, dash="5 4")
    s.line_px(X(34), Y(15), X(34), Y(25), future, 1.4, dash="5 4")
    s.line_px(X(10.5), Y(15), X(10.5), Y(22), future, 1.2, dash="4 3")
    s.line_px(X(0), Y(22), X(34), Y(22), future, 1.3, dash="5 4")
    s.line_px(X(0), Y(25), X(34), Y(25), future, 1.5, dash="5 4")
    rect(3, 16.4, 4, 3.6, "#e7eef2", stroke=future, sw=1.3)
    s.line_px(X(5), Y(16.4), X(5), Y(20), future, 1)
    s.line_px(X(3), Y(18.2), X(7), Y(18.2), future, 1)
    s.line_px(X(10.5), Y(16.15), X(34), Y(16.15), future, 1.6, dash="2 3")
    s.text(X(6.8), Y(23.5), "future room", size=11, fill=future, weight="600")
    s.text(X(22), Y(18.4), "future balcony, wall set back 4 ft", size=12, fill=future, weight="600")
    s.text(X(22), Y(23.6), "future parapet", size=11, fill=future, weight="600")

    # Steps
    for i, h in enumerate((0.67, 1.33, 2.0)):
        inset = 0.35 * (2 - i)
        rect(23.4 + inset, 0 if i == 0 else (0.67 if i == 1 else 1.33), 7.2 - 2 * inset, 0.67, "#d9d2c6", stroke="#b7aea2", sw=0.8)

    # Scale figure
    fx = 36.2
    s.line_px(X(fx), ground, X(fx), Y(4.3), MUTED, 1.6)
    s.add(f'<circle cx="{X(fx):.1f}" cy="{Y(5.05):.1f}" r="8" fill="none" stroke="{MUTED}" stroke-width="1.5"/>')
    s.line_px(X(fx - 0.45), Y(3.3), X(fx + 0.45), Y(3.3), MUTED, 1.4)
    s.text(X(fx + 0.9), Y(2.6), "5'-6\"", size=11, fill=MUTED, anchor="start", weight="600")

    # Height dimensions on the left
    def vdim(h1, h2, xpx, text):
        s.line_px(xpx, Y(h1), xpx, Y(h2), MUTED, 0.9)
        s.line_px(X(0), Y(h1), xpx, Y(h1), MUTED, 0.7)
        s.line_px(X(0), Y(h2), xpx, Y(h2), MUTED, 0.7)
        cy = (Y(h1) + Y(h2)) / 2
        s.text(xpx - 8, cy, text, size=12, fill=MUTED, weight="600",
               extra=f'transform="rotate(-90 {xpx - 8:.1f} {cy:.1f})"')

    vdim(0, 2, 58, "2'-0\"")
    vdim(2, 12, 36, "10'-0\"")
    vdim(12, 15, 58, "3'-0\"")

    # Width
    s.line_px(X(0), ground + 36, X(34), ground + 36, MUTED, 0.9)
    s.line_px(X(0), ground, X(0), ground + 36, MUTED, 0.7)
    s.line_px(X(34), ground, X(34), ground + 36, MUTED, 0.7)
    s.text((X(0) + X(34)) / 2, ground + 54, "34'-0\"", size=13, fill=MUTED, weight="700")

    # Callouts
    s.text(X(5), Y(3.1), "Bedroom 5", size=11, fill=MUTED, weight="600")
    s.text(X(17.4), Y(3.3), "Hall", size=12, fill=MUTED, weight="700")
    s.text(X(27.25), Y(5.4), "", size=1)
    s.text(X(27.25), Y(10.55), "teak door", size=11, fill="#6e422c", weight="700")

    # Side notes
    px = 1280
    y = panel_header(s, px, 80, "THIS FRONT", 380)
    lines = [
        ( "Plinth", "grey stone, 2'-0\""),
        ("Walls", "warm white"),
        ("Sill band", "sandstone"),
        ("Hall windows", "split by the column"),
        ("Door", "teak, 3'-6\" × 7'-0\""),
        ("Chajja", "2 ft deep at the lintel"),
        ("Parapet", "3'-0\", with a coping"),
        ("Porch posts", "at 23 ft and 31 ft"),
    ]
    s.rect_px(px, y, 380, 22 * len(lines) + 8, fill="#fffdfb", stroke="#e4ddd4", sw=0.8)
    yy = y + 20
    for name, val in lines:
        s.text(px + 12, yy, name, size=12, anchor="start", weight="700")
        s.text(px + 368, yy, val, size=12, anchor="end", weight="500", fill=MUTED)
        yy += 22
    y = y + 22 * len(lines) + 24
    note_block(
        s, px, y, "NOTES",
        [
            "North elevation of the ground floor,",
            "as it is built now.",
            "Dashed lines are the future floor.",
            "They rise from this roof slab.",
            "The parapet comes off when that",
            "floor is added.",
            "The left bay stays on the front wall.",
            "The hall bay becomes a balcony",
            "set back 4 ft.",
            "The chajja is the line the upper",
            "floor builds on.",
            "A licensed structural engineer must",
            "confirm footings, columns, and the",
            "staircase before construction.",
        ],
        380,
    )

    # Give the elevation sheet a fake scale so the scale bar matches sc
    s.s = sc
    s.ox = ox
    s.scale_bar(90, ground + 86, feet=10)
    s.chrome(5, "NORTH ELEVATION  ·  GROUND FLOOR, READY FOR THE UPPER FLOOR")
    return s.save("05-north-elevation.svg")


def write_index():
    sheets = [
        ("01-site-plan.svg", "Site plan"),
        ("02-ground-floor-option-a.svg", "Option A ground floor"),
        ("03-ground-floor-option-b.svg", "Option B ground floor"),
        ("04-future-first-floor.svg", "Future first floor"),
        ("05-north-elevation.svg", "North elevation"),
    ]
    imgs = "\n".join(
        f'  <section class="sheet"><img src="{name}" alt="{escape(alt)}"></section>'
        for name, alt in sheets
    )
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Ground floor blueprints</title>
  <style>
    body {{ margin: 0; background: #e6e1d8; color: #22282c; font-family: "Segoe UI", Helvetica, Arial, sans-serif; }}
    header {{ padding: 18px 24px 8px; }}
    h1 {{ font-size: 20px; font-weight: 650; margin: 0 0 4px; }}
    p {{ margin: 0; font-size: 14px; }}
    .sheet {{ width: 1700px; margin: 16px auto; background: white; }}
    img {{ width: 100%; height: auto; display: block; }}
    @media print {{
      body {{ background: white; }}
      header {{ display: none; }}
      .sheet {{ width: auto; margin: 0; page-break-after: always; }}
      @page {{ size: landscape; margin: 0.3in; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Ground floor for a future bungalow</h1>
    <p>Five sheets. Print landscape, one sheet to a page. These are concept drawings, not a permit set.</p>
  </header>
{imgs}
</body>
</html>
'''
    path = os.path.join(OUT, "index.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return path


def main():
    paths = [
        draw_site(),
        draw_ground("A"),
        draw_ground("B"),
        draw_first(),
        draw_elevation(),
        write_index(),
    ]
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
