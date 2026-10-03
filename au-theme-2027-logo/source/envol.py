import math


def mark_envol(c, uid="e", pixels=True):
    """'Envol': a young African with arms raised; the arms are wings of three
    feather bands (chevron motif); the head is the rising sun; the top feathers
    break into pixels (tradition becoming technology)."""
    ang = math.radians(32)
    ux, uy = math.cos(ang), -math.sin(ang)
    sx, sy = 120, 132                      # shoulder centre
    feathers = [(0, 100), (25, 80), (50, 58)]
    left = [c["green"], c["sky"], c["night"]]
    right = [c["coral"], c["gold"], c["night"]]
    out = ""
    for i, ((off, ln), cl, cr) in enumerate(zip(feathers, left, right)):
        for side, col in ((-1, cl), (1, cr)):
            bx, by = sx + side * 13, sy + off / math.cos(ang)
            ex, ey = bx + side * ux * ln, by + uy * ln
            out += (f'<path d="M {bx:.1f} {by:.1f} L {ex:.1f} {ey:.1f}" stroke="{col}" stroke-width="17" '
                    f'stroke-linecap="round" fill="none"/>')
            if pixels and i < 2:
                # pixel squares continuing the feather line
                for j, (gap, size) in enumerate(((20, 12), (37, 8))[: 2 - i]):
                    qx, qy = ex + side * ux * gap, ey + uy * gap
                    rot = -32 * side
                    out += (f'<rect x="{qx - size/2:.1f}" y="{qy - size/2:.1f}" width="{size}" height="{size}" '
                            f'rx="1.5" fill="{col}" transform="rotate({rot} {qx:.1f} {qy:.1f})"/>')
    out += f'<circle cx="120" cy="74" r="25" fill="{c["gold"]}"/>'
    return f'<g transform="translate(120 120) scale(0.9) translate(-120 -138)">{out}</g>'


def mark_envol_simple(c, uid="es"):
    """Simplified version for sizes under 32 px (no pixels)."""
    return mark_envol(c, uid, pixels=False)
