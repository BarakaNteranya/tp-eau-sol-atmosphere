"""Three logo concepts for the AU Theme of the Year 2027. Each mark is drawn in a 240x240 box.

Every mark function takes a palette dict `c` so the same geometry yields
colour, monochrome and reversed versions.
"""

PALETTE = {
    "night": "#0E1E45",   # Bleu nuit continental - ciel, profondeur, institution
    "gold": "#F4A51C",    # Or de l'aube - 25 ans, aube, prospérité
    "coral": "#E8552D",   # Terre cuite - énergie, jeunesse, chaleur
    "green": "#12925A",   # Vert intégration - croissance, Agenda 2063
    "sky": "#1BA3E0",     # Bleu ciel ouvert - SAATM, connectivité, numérique
    "amber": "#F7C04A",
    "orange": "#EF7A22",
    "bg": "#FFFFFF",
}


def mono(ink):
    keys = ["night", "gold", "coral", "green", "sky", "amber", "orange"]
    d = {k: ink for k in keys}
    d["bg"] = "#000000" if ink.upper() == "#FFFFFF" else "#FFFFFF"
    return d


def reversed_palette():
    """Colour on dark background: the 'night' ink becomes white."""
    d = dict(PALETTE)
    d["night"] = "#FFFFFF"
    d["bg"] = PALETTE["night"]
    return d


# ---------------------------------------------------------------------------
# Concept A - "Trajectoire 25" : the numeral 25 drawn as one continuous flight path
# ---------------------------------------------------------------------------
PATH_25 = (
    "M 40 104 "
    "C 40 82, 56 66, 78 66 "
    "C 100 66, 116 82, 116 102 "
    "C 116 118, 106 130, 94 142 "
    "L 46 188 "
    "L 160 188 "
    "C 186 188, 202 170, 202 148 "
    "C 202 126, 186 110, 164 110 "
    "C 152 110, 143 113, 136 118 "
    "L 140 66 "
    "L 196 66 "
    "C 214 66, 224 58, 230 42"
)


def mark_trajectoire(c, uid="a"):
    grad = c["green"] != c["sky"]
    stroke = f"url(#{uid}-g)" if grad else c["night"]
    defs = ""
    if grad:
        defs = (
            f'<defs><linearGradient id="{uid}-g" x1="30" y1="0" x2="232" y2="0" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="{c["green"]}"/>'
            f'<stop offset="0.55" stop-color="{c["sky"]}"/>'
            f'<stop offset="1" stop-color="{c["sky"]}"/></linearGradient></defs>'
        )
    return (
        defs
        # dawn sun rising behind the "5"
        + f'<path d="{PATH_25}" fill="none" stroke="{stroke}" stroke-width="17" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
        # origin node and destination node
        + f'<circle cx="231" cy="22" r="14" fill="{c["gold"]}"/>'
    )


# ---------------------------------------------------------------------------
# Concept B - "Aube Connectée" : sunrise of five open arcs, cut by an ascending route
# ---------------------------------------------------------------------------
def _arc(cx, cy, r):
    return f"M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}"


def mark_aube(c, uid="b"):
    cx, cy = 120, 168
    radii = [22, 44, 66, 88, 110]
    cols = [c["gold"], c["amber"], c["orange"], c["coral"], c["night"]]
    # the core is a solid half disc; the outer four are open arcs
    core = f'<path d="M {cx-30} {cy} A 30 30 0 0 1 {cx+30} {cy} Z" fill="{c["gold"]}"/>'
    arcs = ""
    for r, col in zip([50, 72, 94], [c["orange"], c["coral"], c["night"]]):
        arcs += f'<path d="{_arc(cx, cy, r)}" fill="none" stroke="{col}" stroke-width="13" stroke-linecap="round"/>'
    route = "M 30 185 C 96 182, 160 124, 222 34"
    mask = (
        f'<mask id="{uid}-m" maskUnits="userSpaceOnUse" x="0" y="0" width="240" height="240">'
        '<rect width="240" height="240" fill="#fff"/>'
        f'<path d="{route}" fill="none" stroke="#000" stroke-width="22" stroke-linecap="round"/>'
        "</mask>"
    )
    return (
        f"<defs>{mask}</defs>"
        f'<g mask="url(#{uid}-m)">{core}{arcs}'
        f'<rect x="{cx-118}" y="{cy+12}" width="236" height="11" rx="5.5" fill="{c["green"]}"/></g>'
        f'<path d="{route}" fill="none" stroke="{c["sky"]}" stroke-width="7" stroke-linecap="round"/>'
        f'<circle cx="224" cy="30" r="11" fill="{c["sky"]}"/>'
    )


# ---------------------------------------------------------------------------
# Concept C - "Piste 2063" : an 'A' that is also a runway in perspective under a rising sun
# ---------------------------------------------------------------------------
def mark_piste(c, uid="c"):
    return (
        # left edge (ground, growth)
        f'<path d="M 30 214 L 104 70" fill="none" stroke="{c["green"]}" stroke-width="20" stroke-linecap="round"/>'
        # right edge (sky, connectivity)
        f'<path d="M 210 214 L 136 70" fill="none" stroke="{c["sky"]}" stroke-width="20" stroke-linecap="round"/>'
        # crossbar = horizon
        f'<path d="M 82 150 L 158 150" fill="none" stroke="{c["night"]}" stroke-width="12" stroke-linecap="round"/>'
        # centre-line packets (runway marks / data)
        f'<path d="M 113 214 L 127 214 L 125 192 L 115 192 Z" fill="{c["night"]}"/>'
        f'<path d="M 116 180 L 124 180 L 123 166 L 117 166 Z" fill="{c["night"]}"/>'
        # rising sun in the open apex
        f'<circle cx="120" cy="40" r="22" fill="{c["gold"]}"/>'
    )


CONCEPTS = {
    "A_trajectoire25": ("Trajectoire 25", mark_trajectoire),
    "B_aube_connectee": ("Aube Connectée", mark_aube),
    "C_piste2063": ("Piste 2063", mark_piste),
}
