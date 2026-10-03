"""Shape text with HarfBuzz and convert glyphs to SVG outlines (no font dependency)."""
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from functools import lru_cache

import os
FONT_DIR = os.environ.get("AU_FONT_DIR", os.path.join(os.path.dirname(__file__), "fonts"))


@lru_cache(None)
def _load(name):
    path = f"{FONT_DIR}/{name}.ttf"
    blob = hb.Blob.from_file_path(path)
    face = hb.Face(blob)
    font = hb.Font(face)
    tt = TTFont(path)
    return font, tt, tt.getGlyphSet(), tt["head"].unitsPerEm


import re

_ARABIC = re.compile(r"[\u0600-\u06FF]")


def _shape_run(text, font, size, rtl=None):
    hbfont, tt, gs, upem = _load(font)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    if rtl is not None:
        buf.direction = "rtl" if rtl else "ltr"
    hb.shape(hbfont, buf, {"kern": True, "liga": True})
    order = tt.getGlyphOrder()
    s = size / upem
    return [(order[i.codepoint], p.x_advance * s, p.x_offset * s, p.y_offset * s)
            for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


def _glyphs(text, font, size):
    """Glyphs in visual order. Arabic paragraphs keep digit runs left-to-right."""
    if not _ARABIC.search(text):
        return _shape_run(text, font, size)
    runs = [r for r in re.split(r"(\d+)", text) if r]
    out = []
    for r in reversed(runs):
        out += _shape_run(r, font, size, rtl=not r.isdigit())
    return out


def measure(text, font="Montserrat-700", size=10, tracking=0.0):
    g = _glyphs(text, font, size)
    return sum(a for _, a, _, _ in g) + tracking * size * max(len(g) - 1, 0)


def text_path(text, x, y, font="Montserrat-700", size=10, anchor="start", tracking=0.0):
    """Return an SVG path 'd' string for text, baseline at y. tracking in em."""
    hbfont, tt, gs, upem = _load(font)
    s = size / upem
    if anchor == "middle":
        x -= measure(text, font, size, tracking) / 2
    elif anchor == "end":
        x -= measure(text, font, size, tracking)
    pen = SVGPathPen(gs)
    cx = x
    for gname, adv, xo, yo in _glyphs(text, font, size):
        gs[gname].draw(TransformPen(pen, (s, 0, 0, -s, cx + xo, y - yo)))
        cx += adv + tracking * size
    return pen.getCommands()
