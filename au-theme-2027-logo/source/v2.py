"""V2 - flagship concept 'Envol': full identity system (logo files, board, pattern, mock-ups)."""
import base64
import math
import os
import cairosvg
from marks import PALETTE as P, mono, reversed_palette
from envol import mark_envol, mark_envol_simple
from build import svg_doc, placed, T, MW, MH
from textpath import text_path, measure

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "V2_envol")

# year label (2 lines), theme line, sub-theme (2 lines)
TITLE = {
    "en": (("THEME OF", "THE YEAR"), "AU at the Dawn of its 25th Anniversary",
           ("Leveraging the Full Potential of SAATM and", "New Technologies for Continental Integration")),
    "fr": (("THÈME DE", "L'ANNÉE"), "L'UA à l'aube de son 25e anniversaire",
           ("Tirer pleinement parti du MUTAA et des nouvelles", "technologies pour l'intégration continentale")),
    "pt": (("TEMA", "DO ANO"), "A UA no limiar do seu 25.º aniversário",
           ("Aproveitar todo o potencial do SAATM e das novas", "tecnologias para a integração continental")),
    "es": (("TEMA", "DEL AÑO"), "La UA en los albores de su 25.º aniversario",
           ("Aprovechar todo el potencial del SAATM y de las", "nuevas tecnologías para la integración continental")),
    "sw": (("KAULIMBIU", "YA MWAKA"), "AU katika Mwanzo wa Maadhimisho ya Miaka 25",
           ("Kutumia kikamilifu SAATM na teknolojia mpya", "kwa utangamano wa bara")),
    "ar": (("موضوع", "العام"), "الاتحاد الأفريقي في فجر ذكراه الخامسة والعشرين",
           ("الاستفادة الكاملة من السوق الأفريقية الموحدة للنقل الجوي", "والتكنولوجيات الجديدة من أجل التكامل القاري")),
}
LANG_NAMES = {"en": "English", "fr": "Français", "pt": "Português", "es": "Español", "sw": "Kiswahili", "ar": "العربية"}


def fonts(lang):
    if lang == "ar":
        return dict(year="Montserrat-800", label="NotoKufiArabic-700", theme="NotoKufiArabic-700", sub="NotoKufiArabic-500")
    return dict(year="Montserrat-800", label="Montserrat-800", theme="Montserrat-700", sub="Montserrat-500")


def title_block(lang, pal, x, y, align="start"):
    """Official title hierarchy: big 2027 + stacked label, theme line, sub-theme.
    align='start' (left), 'end' (right, for Arabic), 'middle'. Returns (svg, w, h)."""
    (l1, l2), theme, (s1, s2) = TITLE[lang]
    f = fonts(lang)
    ink, accent = pal["night"], (pal["green"] if pal["night"] != "#FFFFFF" else pal["gold"])
    ar = lang == "ar"
    YS, LS, TS, SS = 84, 25 if not ar else 23, 25 if not ar else 23, 17 if not ar else 16
    yw = measure("2027", f["year"], YS, -0.02)
    lw = max(measure(l1, f["label"], LS, 0.06 if not ar else 0), measure(l2, f["label"], LS, 0.06 if not ar else 0))
    row1 = yw + 14 + lw
    tw = measure(theme, f["theme"], TS)
    sw = max(measure(s1, f["sub"], SS), measure(s2, f["sub"], SS))
    W = max(row1, tw, sw)
    if align == "start":
        x0 = x
    elif align == "end":
        x0 = x - W
    else:
        x0 = x - W / 2

    def line_x(width):
        return {"start": x0, "end": x0 + W - width, "middle": x0 + (W - width) / 2}[align]

    out = []
    rx = line_x(row1)
    yb = y + YS * 0.72
    lt = 0.06 if not ar else 0
    if ar:  # label to the right of the year? In RTL, label reads first: place it on the right
        out.append(f'<path d="{text_path("2027", rx, yb, f["year"], YS, "start", -0.02)}" fill="{ink}"/>')
        lx = rx + yw + 14
        out.append(f'<path d="{text_path(l1, lx + lw, yb - YS*0.72 + LS*1.05, f["label"], LS, "end", lt)}" fill="{accent}"/>')
        out.append(f'<path d="{text_path(l2, lx + lw, yb + 2, f["label"], LS, "end", lt)}" fill="{accent}"/>')
    else:
        out.append(f'<path d="{text_path("2027", rx, yb, f["year"], YS, "start", -0.02)}" fill="{ink}"/>')
        lx = rx + yw + 14
        out.append(f'<path d="{text_path(l1, lx, yb - YS*0.72 + LS*0.74, f["label"], LS, "start", lt)}" fill="{accent}"/>')
        out.append(f'<path d="{text_path(l2, lx, yb, f["label"], LS, "start", lt)}" fill="{accent}"/>')
    # thin rule in the five colours
    ry = yb + 22
    seg = W / 5
    for i, k in enumerate(["green", "sky", "gold", "coral", "night"]):
        out.append(f'<rect x="{x0 + i*seg:.1f}" y="{ry}" width="{seg:.1f}" height="4" fill="{pal[k]}"/>')
    ty = ry + 18 + TS * (0.75 if not ar else 0.95)
    out.append(f'<path d="{text_path(theme, line_x(tw), ty, f["theme"], TS)}" fill="{ink}"/>')
    sy1 = ty + 14 + SS * (0.95 if not ar else 1.3)
    sy2 = sy1 + SS * (1.35 if not ar else 1.7)
    out.append(f'<path d="{text_path(s1, line_x(measure(s1, f["sub"], SS)), sy1, f["sub"], SS)}" fill="{ink}"/>')
    out.append(f'<path d="{text_path(s2, line_x(measure(s2, f["sub"], SS)), sy2, f["sub"], SS)}" fill="{ink}"/>')
    return "".join(out), W, sy2 - y + SS * 0.4


def lockup_h(pal, uid, lang="en", mark=mark_envol):
    gap = 30
    _, tw, th = title_block(lang, pal, 0, 0)
    ty = (MH - th) / 2
    if lang == "ar":
        tb, tw, th = title_block(lang, pal, tw, ty, "end")
        return tb + f'<g transform="translate({tw + gap},0)">{mark(pal, uid)}</g>', MW + gap + tw, MH
    tb, tw, th = title_block(lang, pal, MW + gap, ty)
    return mark(pal, uid) + tb, MW + gap + tw, MH


def lockup_v(pal, uid, lang="en", mark=mark_envol):
    _, tw, th = title_block(lang, pal, 0, 0)
    W = max(tw, MW)
    tb, _, th = title_block(lang, pal, W / 2, MH + 10, "middle")
    return f'<g transform="translate({(W - MW)/2},0)">{mark(pal, uid)}</g>' + tb, W, MH + 10 + th


# ------------------------------------------------------------------ pattern
def chevron_pattern(w, h, cell, colors, opacity=1.0, stroke=None):
    """Repeating feather/chevron frieze derived from the wings, with pixel accents."""
    sw = stroke or cell * 0.12
    out = []
    rows = int(h / (cell * 0.62)) + 3
    cols = int(w / cell) + 3
    for r in range(-1, rows):
        y = r * cell * 0.62
        for k in range(-1, cols):
            x = k * cell + (r % 2) * cell / 2
            col = colors[(r * 2 + k) % len(colors)]
            d = cell * 0.36
            out.append(f'<path d="M {x - d:.1f} {y - d*0.62:.1f} L {x:.1f} {y:.1f} L {x + d:.1f} {y - d*0.62:.1f}" '
                       f'fill="none" stroke="{col}" stroke-width="{sw:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
            if (r + k) % 3 == 0:
                q = sw * 0.9
                out.append(f'<rect x="{x - q/2:.1f}" y="{y + cell*0.16:.1f}" width="{q:.1f}" height="{q:.1f}" '
                           f'fill="{col}" transform="rotate(45 {x:.1f} {y + cell*0.16 + q/2:.1f})"/>')
    return f'<g opacity="{opacity}">{"".join(out)}</g>'


def save(path, svg, png_w=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(svg)
    if png_w:
        png = path.replace("/svg/", "/png/").replace(".svg", ".png")
        os.makedirs(os.path.dirname(png), exist_ok=True)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=png, output_width=png_w)


def on_gold():
    d = dict(P)
    d["gold"] = "#FFFFFF"   # sun turns white on the gold ground
    d["bg"] = P["gold"]
    return d


VARIANTS = {
    "color": (P, None),
    "mono-black": (mono("#111111"), None),
    "reversed": (reversed_palette(), P["night"]),
    "mono-white": (mono("#FFFFFF"), "#111111"),
    "on-gold": (on_gold(), P["gold"]),
}


def build_files():
    pad = 20
    for v, (pal, bg) in VARIANTS.items():
        uid = f"v2{v}"
        vb = lambda w, h: f"{-pad} {-pad} {w + 2*pad} {h + 2*pad}"
        save(f"{OUT}/svg/mark_{v}.svg", svg_doc(MW + 2*pad, MH + 2*pad, mark_envol(pal, uid), bg, vb(MW, MH)), 2000)
        b, w, h = lockup_h(pal, uid + "h")
        save(f"{OUT}/svg/lockup-horizontal_{v}.svg", svg_doc(w + 2*pad, h + 2*pad, b, bg, vb(w, h)), 3000)
        b, w, h = lockup_v(pal, uid + "v")
        save(f"{OUT}/svg/lockup-vertical_{v}.svg", svg_doc(w + 2*pad, h + 2*pad, b, bg, vb(w, h)), 2400)
    save(f"{OUT}/svg/mark_small-sizes.svg",
         svg_doc(MW + 2*pad, MH + 2*pad, mark_envol_simple(P, "v2s"), None, f"{-pad} {-pad} {MW + 2*pad} {MH + 2*pad}"), 512)
    tile = chevron_pattern(600, 600, 100, [P["green"], P["sky"], P["night"], P["coral"], P["gold"]])
    save(f"{OUT}/svg/motif_chevrons.svg", svg_doc(600, 600, tile, "#FFFFFF"), 1500)


# ------------------------------------------------------------------ board
def board():
    W, H = 3000, 2100
    out = [f'<rect width="{W}" height="{H}" fill="#F6F4EF"/>',
           T("PISTE PRINCIPALE · V2", 120, 140, 30, "Montserrat-700", P["coral"], trk=0.2),
           T("ENVOL", 120, 235, 84, "Montserrat-800", P["night"], trk=0.04),
           T("Une jeunesse africaine qui prend son envol : bras levés, ailes de chevrons, soleil de l'aube.",
             120, 295, 32, "Montserrat-500", "#55607A")]
    out.append(f'<rect x="120" y="350" width="1840" height="800" rx="24" fill="#FFFFFF"/>')
    b, w, h = lockup_h(P, "bdh")
    out.append(placed(b, w, h, 190, 420, 1700, 660))
    out.append(f'<rect x="2000" y="350" width="880" height="800" rx="24" fill="#FFFFFF"/>')
    out.append(placed(mark_envol(P, "bdm"), MW, MH, 2080, 400, 720, 640))
    out.append(T("Symbole seul", 2440, 1110, 26, "Montserrat-600", "#55607A", "middle"))
    tiles = [("Monochrome", mono("#111111"), "#FFFFFF"), ("Inversé couleur", reversed_palette(), P["night"]),
             ("Sur fond or", on_gold(), P["gold"]), ("Blanc sur couleur", mono("#FFFFFF"), P["green"])]
    vy = 1200
    for i, (lab, pal, bg) in enumerate(tiles):
        x = 120 + i * 465
        out.append(f'<rect x="{x}" y="{vy}" width="440" height="420" rx="20" fill="{bg}"/>')
        out.append(placed(mark_envol(pal, f"bt{i}"), MW, MH, x + 60, vy + 40, 320, 300))
        out.append(T(lab, x + 220, vy + 385, 24, "Montserrat-600", "#111111" if bg == "#FFFFFF" else "#FFFFFF", "middle"))
    sx = 2000
    out.append(f'<rect x="{sx}" y="{vy}" width="880" height="420" rx="20" fill="#FFFFFF"/>')
    out.append(T("Petites tailles", sx + 40, vy + 60, 26, "Montserrat-700", P["night"]))
    px = sx + 50
    for size in (160, 96, 64, 40, 24):
        fn = mark_envol if size >= 40 else mark_envol_simple
        out.append(placed(fn(P, f"bs{size}"), MW, MH, px, vy + 320 - size, size, size))
        out.append(T(f"{size}px", px + size / 2, vy + 375, 20, "Montserrat-500", "#55607A", "middle"))
        px += size + 46
    # palette
    py = 1680
    sw = [("night", "Bleu nuit"), ("sky", "Bleu ciel"), ("green", "Vert"), ("gold", "Or de l'aube"), ("coral", "Terre cuite")]
    for i, (k, lab) in enumerate(sw):
        x = 120 + i * 300
        out.append(f'<rect x="{x}" y="{py}" width="280" height="150" rx="14" fill="{P[k]}"/>')
        out.append(T(lab, x + 18, py + 190, 24, "Montserrat-700", P["night"]))
        out.append(T(P[k], x + 18, py + 225, 20, "Montserrat-500", "#55607A"))
    # pattern swatch
    out.append(f'<clipPath id="pc"><rect x="1660" y="{py}" width="560" height="260" rx="14"/></clipPath>')
    out.append(f'<rect x="1660" y="{py}" width="560" height="260" rx="14" fill="#FFFFFF"/>')
    out.append(f'<g clip-path="url(#pc)"><g transform="translate(1660,{py})">'
               + chevron_pattern(560, 260, 70, [P["green"], P["sky"], P["night"], P["coral"], P["gold"]]) + "</g></g>")
    out.append(T("Motif « plumes-chevrons »", 1660, py + 300, 22, "Montserrat-600", "#55607A"))
    tx = 2300
    out.append(T("Montserrat ExtraBold", tx, py + 50, 40, "Montserrat-800", P["night"]))
    out.append(T("Montserrat Medium — texte courant", tx, py + 100, 26, "Montserrat-500", P["night"]))
    out.append(T("الاتحاد الأفريقي", tx, py + 160, 34, "NotoKufiArabic-700", P["night"]))
    out.append(T("Noto Kufi Arabic", tx, py + 205, 22, "Montserrat-500", "#55607A"))
    out.append(T("Polices libres SIL OFL", tx, py + 240, 20, "Montserrat-500", "#55607A"))
    return svg_doc(W, H, "".join(out))


def multilingual():
    rows = list(TITLE)
    rh, W = 330, 3000
    H = 170 + rh * len(rows)
    out = [f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
           T("Adaptation multilingue — langues de travail de l'UA", 120, 115, 46, "Montserrat-800", P["night"])]
    for i, lang in enumerate(rows):
        y = 170 + i * rh
        out.append(f'<rect y="{y}" width="{W}" height="{rh}" fill="{"#F6F4EF" if i % 2 else "#FFFFFF"}"/>')
        out.append(T(LANG_NAMES[lang], 120, y + rh / 2 + 10, 30,
                     "NotoKufiArabic-500" if lang == "ar" else "Montserrat-600", "#55607A"))
        b, w, h = lockup_h(P, f"ml{lang}", lang)
        out.append(placed(b, w, h, 520, y + 25, 2360, rh - 50))
    return svg_doc(W, H, "".join(out))


# ------------------------------------------------------------------ mock-ups
def web_banner():
    """Same format family as the official 2025 web banner, warm gold ground."""
    W, H = 3000, 1250
    out = [f'<defs><radialGradient id="wg" cx="0.3" cy="0.4" r="0.9"><stop offset="0" stop-color="#F7B733"/>'
           f'<stop offset="1" stop-color="#D98A0B"/></radialGradient></defs>',
           f'<rect width="{W}" height="{H}" fill="url(#wg)"/>',
           chevron_pattern(W, H, 150, ["#FFFFFF"], 0.10, 10)]
    out.append(f'<circle cx="720" cy="625" r="470" fill="#FFFFFF"/>')
    out.append(f'<circle cx="720" cy="625" r="470" fill="none" stroke="{P["night"]}" stroke-width="6" opacity="0.15"/>')
    out.append(placed(mark_envol(P, "wb"), MW, MH, 380, 300, 680, 650))
    x = 1330
    out.append(f'<rect x="{x}" y="250" width="{measure("2027", "Montserrat-800", 190) + 60}" height="200" fill="{P["night"]}"/>')
    out.append(T("2027", x + 30, 420, 190, "Montserrat-800", "#FFFFFF"))
    lx = x + measure("2027", "Montserrat-800", 190) + 100
    out.append(T("THEME OF", lx, 330, 62, "Montserrat-800", P["night"], trk=0.04))
    out.append(T("THE YEAR", lx, 410, 62, "Montserrat-800", P["night"], trk=0.04))
    out.append(T("AU at the Dawn of its", x, 560, 70, "Montserrat-800", "#FFFFFF"))
    out.append(T("25th Anniversary", x, 645, 70, "Montserrat-800", "#FFFFFF"))
    out.append(T("Leveraging the Full Potential of SAATM and", x, 745, 44, "Montserrat-600", P["night"]))
    out.append(T("New Technologies for Continental Integration", x, 805, 44, "Montserrat-600", P["night"]))
    hw = measure("#AUat25", "Montserrat-800", 42) + 50
    out.append(f'<rect x="{x}" y="870" width="{hw}" height="72" fill="#FFFFFF"/>')
    out.append(T("#AUat25", x + 25, 922, 42, "Montserrat-800", P["night"]))
    return svg_doc(W, H, "".join(out))


def card():
    W = H = 2000
    rp = reversed_palette()
    out = [f'<rect width="{W}" height="{H}" fill="{P["night"]}"/>',
           chevron_pattern(W, H, 160, ["#FFFFFF"], 0.05, 10)]
    b, w, h = lockup_v(rp, "cd")
    out.append(placed(b, w, h, 260, 220, 1480, 1340))
    out.append(T("ONE MARKET · ONE SKY · ONE DIGITAL AFRICA", W / 2, 1720, 44, "Montserrat-700", P["gold"], "middle", 0.1))
    out.append(T("#AUat25   #SAATM   #Agenda2063", W / 2, 1810, 36, "Montserrat-500", "#FFFFFF", "middle", 0.04))
    for i, k in enumerate(["green", "sky", "gold", "coral"]):
        out.append(f'<rect x="{i*W/4}" y="{H-26}" width="{W/4}" height="26" fill="{P[k]}"/>')
    return svg_doc(W, H, "".join(out))


def backdrop():
    W, H = 4800, 2160
    out = [f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
           f'<rect x="0" y="0" width="1500" height="{H}" fill="{P["night"]}"/>',
           f'<g clip-path="url(#bk)">{chevron_pattern(1500, H, 190, [P["green"], P["sky"], P["coral"], P["gold"]], 0.9, 14)}</g>',
           f'<clipPath id="bk"><rect width="1500" height="{H}"/></clipPath>']
    b, w, h = lockup_v(P, "bkd")
    out.append(placed(b, w, h, 1800, 220, 2800, 1700))
    return svg_doc(W, H, "".join(out))


def cover():
    W, H = 2100, 2970
    out = [f'<rect width="{W}" height="{H}" fill="#F6F4EF"/>',
           f'<clipPath id="cv"><rect y="2180" width="{W}" height="790"/></clipPath>',
           f'<rect y="2180" width="{W}" height="790" fill="{P["night"]}"/>',
           f'<g clip-path="url(#cv)"><g transform="translate(0,2180)">'
           f'{chevron_pattern(W, 790, 150, ["#FFFFFF"], 0.06, 10)}</g></g>',
           T("AFRICAN UNION", 160, 250, 40, "Montserrat-800", P["green"], trk=0.2)]
    out.append(placed(mark_envol(P, "cv"), MW, MH, 260, 340, 1580, 1300))
    out.append(T("2027", 160, 1900, 200, "Montserrat-800", P["night"]))
    out.append(T("THEME OF", 160 + measure("2027", "Montserrat-800", 200) + 40, 1790, 62, "Montserrat-800", P["green"], trk=0.04))
    out.append(T("THE YEAR", 160 + measure("2027", "Montserrat-800", 200) + 40, 1898, 62, "Montserrat-800", P["green"], trk=0.04))
    lines = ["AU at the Dawn of its 25th Anniversary", "Leveraging the Full Potential of SAATM and",
             "New Technologies for Continental Integration"]
    out.append(T(lines[0], 160, 2330, 64, "Montserrat-800", "#FFFFFF"))
    out.append(T(lines[1], 160, 2430, 48, "Montserrat-500", "#FFFFFF"))
    out.append(T(lines[2], 160, 2495, 48, "Montserrat-500", "#FFFFFF"))
    out.append(T("Concept Note & Roadmap", 160, 2780, 44, "Montserrat-700", P["gold"]))
    return svg_doc(W, H, "".join(out))


def embed(path, x, y, w, h):
    data = base64.b64encode(open(path, "rb").read()).decode()
    return (f'<rect x="{x+12}" y="{y+16}" width="{w}" height="{h}" fill="#000" opacity="0.16"/>'
            f'<image href="data:image/png;base64,{data}" x="{x}" y="{y}" width="{w}" height="{h}"/>')


def build_mockups():
    p = {}
    for name, fn, pw in (("banniere-web", web_banner, 3000), ("carte-numerique", card, 2000),
                         ("toile-de-fond", backdrop, 4800), ("couverture", cover, 2100)):
        p[name] = f"{OUT}/png/maquette_{name}.png"
        cairosvg.svg2png(bytestring=fn().encode(), write_to=p[name], output_width=pw)
    W, H = 3000, 4300
    body = [f'<rect width="{W}" height="{H}" fill="#E4E5E9"/>',
            T("MAQUETTES — ENVOL", 120, 150, 56, "Montserrat-800", P["night"], trk=0.03),
            embed(p["toile-de-fond"], 120, 230, 2760, 1242),
            T("1 · Toile de fond d'événement", 120, 1540, 32, "Montserrat-600", "#3C4660"),
            embed(p["banniere-web"], 120, 1620, 2760, 1150),
            T("2 · Bannière web (même format que celle de 2025)", 120, 2840, 32, "Montserrat-600", "#3C4660"),
            embed(p["carte-numerique"], 120, 2920, 1240, 1240),
            T("3 · Carte numérique (réseaux sociaux)", 120, 4230, 32, "Montserrat-600", "#3C4660"),
            embed(p["couverture"], 2880 - 877, 2920, 877, 1240),
            T("4 · Couverture de publication (A4)", 2880 - 877, 4230, 32, "Montserrat-600", "#3C4660")]
    cairosvg.svg2png(bytestring=svg_doc(W, H, "".join(body)).encode(), write_to=f"{OUT}/png/maquettes_3000px.png")


if __name__ == "__main__":
    build_files()
    cairosvg.svg2png(bytestring=board().encode(), write_to=f"{OUT}/png/planche_presentation_3000px.png")
    cairosvg.svg2png(bytestring=multilingual().encode(), write_to=f"{OUT}/png/adaptation_multilingue_3000px.png")
    build_mockups()
    print("V2 built")
