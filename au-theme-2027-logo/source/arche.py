"""Concept V3 'Arche d'Intégration': rising arch (bridge, 25 years) crossed by a tapered
air/data trajectory, with a connection point at the crossing."""

ARC_PAL = {
    "blue": "#123C8C",   # Bleu institutionnel (arche + texte)
    "gold": "#F4A51C",   # Or (trajectoire)
    "green": "#12925A",  # Vert émeraude (point de connexion)
    "red": "#D7262E",    # Rouge (pointe)
    "bg": "#FFFFFF",
}


def arc_mono(ink, bg):
    return {"blue": ink, "gold": ink, "green": ink, "red": ink, "bg": bg}


def arc_reversed_color():
    return {"blue": "#FFFFFF", "gold": "#F4A51C", "green": "#2BC07A", "red": "#FF5A4F", "bg": "#123C8C"}


OUTER = [((6, 206), (30, 108), (100, 54), (160, 54)), ((160, 54), (208, 54), (230, 120), (234, 206))]
INNER = [((216, 206), (212, 134), (194, 88), (160, 88)), ((160, 88), (112, 88), (64, 132), (40, 206))]


def _bez(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u**3*a + 3*u*u*t*b + 3*u*t*t*c + t**3*d for a, b, c, d in zip(p0, p1, p2, p3))


TRAJ = ((58, 199), (124, 194), (180, 148), (244, 18))


def _ribbon(t0, t1, wmax=13.0, n=80):
    """Tapered ribbon polygon along TRAJ: hair-thin tail, widening, sharp point."""
    import math
    def width(t):
        if t < 0.86:
            return 2.2 + (wmax - 2.2) * (t / 0.86) ** 1.3
        return wmax * max(0.0, (1 - t) / 0.14) ** 0.9
    L, R = [], []
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        x, y = _bez(*TRAJ, t)
        x2, y2 = _bez(*TRAJ, min(t + 1e-3, 1))
        x1, y1 = _bez(*TRAJ, max(t - 1e-3, 0))
        dx, dy = x2 - x1, y2 - y1
        l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        w = width(t) / 2
        L.append((x + nx * w, y + ny * w))
        R.append((x - nx * w, y - ny * w))
    pts = L + R[::-1]
    return "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in pts) + " Z"


def crossing():
    """Approximate intersection of the trajectory with the arch's centre line (right leg)."""
    # sample arch centre = midpoint of outer and inner curves on the right side
    outer = OUTER[1]
    ir = INNER[0]
    inner = (ir[3], ir[2], ir[1], ir[0])
    best = None
    for i in range(400):
        s = i / 399
        ox, oy = _bez(*outer, s)
        ix, iy = _bez(*inner, s)
        cx, cy = (ox + ix) / 2, (oy + iy) / 2
        for j in range(400):
            t = j / 399
            x, y = _bez(*TRAJ, t)
            dd = (x - cx) ** 2 + (y - cy) ** 2
            if best is None or dd < best[0]:
                best = (dd, cx, cy, t)
    return best[1], best[2], best[3]


CX, CY, CT = crossing()


def _pts(d_ribbon):
    nums = d_ribbon.replace("M", "").replace("L", "").replace("Z", "").split()
    v = list(map(float, nums))
    return list(zip(v[0::2], v[1::2]))


def _arch_poly():
    from shapely.geometry import Polygon
    pts = []
    for seg in OUTER + INNER:
        pts += [_bez(*seg, i / 40) for i in range(41)]
    return Polygon(pts)


def _d(geom):
    """Shapely (Multi)Polygon -> SVG path d (evenodd)."""
    polys = getattr(geom, "geoms", [geom])
    out = []
    for p in polys:
        for ring in [p.exterior, *p.interiors]:
            c = list(ring.coords)
            out.append("M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in c[:-1]) + " Z")
    return " ".join(out)


def mark_arche(c, uid="ar", gap=5.0):
    from shapely.geometry import Polygon, Point
    ribbon = Polygon(_pts(_ribbon(0, 1)))
    cut = ribbon.buffer(gap, join_style=1).union(Point(CX, CY).buffer(12.5 + gap, 64))
    arch = _arch_poly().difference(cut)
    split = 0.88
    return (f'<path d="{_d(arch)}" fill="{c["blue"]}" fill-rule="evenodd"/>'
            f'<path d="{_ribbon(0, split + 0.004)}" fill="{c["gold"]}"/>'
            f'<path d="{_ribbon(split, 1)}" fill="{c["red"]}"/>'
            f'<circle cx="{CX:.2f}" cy="{CY:.2f}" r="12.5" fill="{c["green"]}"/>')
