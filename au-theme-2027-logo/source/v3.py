"""V3 - 'Arche d'Intégration' (from the user's brief): logo files, board, multilingual, mock-ups."""
import os
import cairosvg
from arche import mark_arche, ARC_PAL as A, arc_mono, arc_reversed_color
from build import svg_doc, placed, T, MW, MH
from textpath import text_path, measure
from v2 import TITLE, LANG_NAMES, save, embed

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "V3_arche") \
    if os.path.basename(os.path.dirname(os.path.abspath(__file__))) == "source" \
    else "/home/user/tp-eau-sol-atmosphere/au-theme-2027-logo/V3_arche"

KICKER = {
    "en": "AFRICAN UNION · THEME OF THE YEAR 2027",
    "fr": "UNION AFRICAINE · THÈME DE L'ANNÉE 2027",
    "pt": "UNIÃO AFRICANA · TEMA DO ANO 2027",
    "es": "UNIÓN AFRICANA · TEMA DEL AÑO 2027",
    "sw": "UMOJA WA AFRIKA · KAULIMBIU YA MWAKA 2027",
    "ar": "الاتحاد الأفريقي · موضوع عام 2027",
}


def wordmark(lang, pal, x, y, align="middle"):
    """Kicker / main title in caps / two-line subtitle. Returns (svg, w, h)."""
    ar = lang == "ar"
    fk, fm, fs = (("NotoKufiArabic-700", "NotoKufiArabic-700", "NotoKufiArabic-500") if ar
                  else ("Montserrat-700", "Montserrat-800", "Montserrat-500"))
    kick, main = KICKER[lang], TITLE[lang][1].upper() if not ar else TITLE[lang][1]
    s1, s2 = TITLE[lang][2]
    KS, MS, SS = (15, 27, 17.5) if not ar else (15, 25, 16)
    kt = 0.16 if not ar else 0
    ink = pal["blue"]
    accent = pal["gold"] if pal["gold"] != pal["blue"] else ink
    widths = [measure(kick, fk, KS, kt), measure(main, fm, MS, 0.01 if not ar else 0),
              measure(s1, fs, SS), measure(s2, fs, SS)]
    W = max(widths)

    def lx(w):
        return {"start": x, "middle": x - w / 2, "end": x - w}[align]

    lh = 1.0 if not ar else 1.35
    y1 = y + KS * 0.75 * lh
    y2 = y1 + 14 + MS * 0.75 * lh
    y3 = y2 + 14 + SS * 0.95 * lh
    y4 = y3 + SS * 1.35 * lh
    out = [f'<path d="{text_path(kick, lx(widths[0]), y1, fk, KS, "start", kt)}" fill="{accent}"/>',
           f'<path d="{text_path(main, lx(widths[1]), y2, fm, MS, "start", 0.01 if not ar else 0)}" fill="{ink}"/>',
           f'<path d="{text_path(s1, lx(widths[2]), y3, fs, SS)}" fill="{ink}"/>',
           f'<path d="{text_path(s2, lx(widths[3]), y4, fs, SS)}" fill="{ink}"/>']
    return "".join(out), W, y4 - y + SS * 0.4


def lockup_v(pal, uid, lang="en"):
    """Brief layout: symbol on top, wordmark below."""
    _, W, h = wordmark(lang, pal, 0, 0)
    W = max(W, MW)
    tb, _, h = wordmark(lang, pal, W / 2, MH + 22, "middle")
    return f'<g transform="translate({(W - MW)/2},0)">{mark_arche(pal, uid)}</g>' + tb, W, MH + 22 + h


def lockup_h(pal, uid, lang="en"):
    """Horizontal version for banners."""
    gap = 32
    _, W, h = wordmark(lang, pal, 0, 0)
    ty = (MH - h) / 2
    if lang == "ar":
        tb, _, _ = wordmark(lang, pal, W, ty, "end")
        return tb + f'<g transform="translate({W + gap},0)">{mark_arche(pal, uid)}</g>', W + gap + MW, MH
    tb, _, _ = wordmark(lang, pal, MW + gap, ty, "start")
    return mark_arche(pal, uid) + tb, MW + gap + W, MH


VARIANTS = {
    "color": (A, None),
    "mono-black": (arc_mono("#111111", "#FFFFFF"), None),
    "reversed-white": (arc_mono("#FFFFFF", "#123C8C"), "#123C8C"),
    "reversed-color": (arc_reversed_color(), "#123C8C"),
}


def build_files():
    pad = 20
    for v, (pal, bg) in VARIANTS.items():
        vb = lambda w, h: f"{-pad} {-pad} {w + 2*pad} {h + 2*pad}"
        save(f"{OUT}/svg/mark_{v}.svg", svg_doc(MW + 2*pad, MH + 2*pad, mark_arche(pal, f"m{v}"), bg, vb(MW, MH)), 2000)
        b, w, h = lockup_v(pal, f"v{v}")
        save(f"{OUT}/svg/lockup-vertical_{v}.svg", svg_doc(w + 2*pad, h + 2*pad, b, bg, vb(w, h)), 2400)
        b, w, h = lockup_h(pal, f"h{v}")
        save(f"{OUT}/svg/lockup-horizontal_{v}.svg", svg_doc(w + 2*pad, h + 2*pad, b, bg, vb(w, h)), 3000)


def board():
    W, H = 3000, 2100
    out = [f'<rect width="{W}" height="{H}" fill="#F4F6FA"/>',
           T("PISTE V3 · D'APRÈS VOTRE BRIEF", 120, 140, 30, "Montserrat-700", A["red"], trk=0.2),
           T("L'ARCHE D'INTÉGRATION", 120, 235, 80, "Montserrat-800", A["blue"], trk=0.02),
           T("Le pont des 25 ans, traversé par une trajectoire aérienne et numérique.", 120, 295, 32,
             "Montserrat-500", "#55607A")]
    out.append(f'<rect x="120" y="350" width="1280" height="1270" rx="24" fill="#FFFFFF"/>')
    b, w, h = lockup_v(A, "bv")
    out.append(placed(b, w, h, 200, 420, 1120, 1130))
    out.append(f'<rect x="1440" y="350" width="1440" height="620" rx="24" fill="#FFFFFF"/>')
    b, w, h = lockup_h(A, "bh")
    out.append(placed(b, w, h, 1500, 400, 1320, 520))
    tiles = [("Monochrome", arc_mono("#111111", "#FFFFFF"), "#FFFFFF"),
             ("Inversé blanc", arc_mono("#FFFFFF", "#123C8C"), "#123C8C"),
             ("Inversé couleur", arc_reversed_color(), "#123C8C"),
             ("Blanc sur noir", arc_mono("#FFFFFF", "#111111"), "#111111")]
    for i, (lab, pal, bg) in enumerate(tiles):
        x = 1440 + i * 365
        out.append(f'<rect x="{x}" y="1010" width="345" height="345" rx="20" fill="{bg}"/>')
        out.append(placed(mark_arche(pal, f"bt{i}"), MW, MH, x + 50, 1040, 245, 230))
        out.append(T(lab, x + 172, 1325, 22, "Montserrat-600", "#111111" if bg == "#FFFFFF" else "#FFFFFF", "middle"))
    out.append(f'<rect x="1440" y="1395" width="1440" height="225" rx="20" fill="#FFFFFF"/>')
    out.append(T("Petites tailles", 1480, 1450, 24, "Montserrat-700", A["blue"]))
    px = 1800
    for size in (128, 64, 40, 24, 16):
        out.append(placed(mark_arche(A, f"bs{size}"), MW, MH, px, 1590 - size, size, size))
        out.append(T(f"{size}px", px + size / 2, 1610, 18, "Montserrat-500", "#55607A", "middle"))
        px += size + 70
    py = 1690
    sw = [("blue", "Bleu institutionnel", "Arche, texte : autorité, confiance"),
          ("gold", "Or", "Trajectoire : innovation, prospérité"),
          ("green", "Vert émeraude", "Point de connexion : croissance"),
          ("red", "Rouge", "Pointe : énergie, urgence d'agir")]
    for i, (k, lab, mean) in enumerate(sw):
        x = 120 + i * 470
        out.append(f'<rect x="{x}" y="{py}" width="440" height="140" rx="14" fill="{A[k]}"/>')
        out.append(T(f"{lab}  {A[k]}", x + 10, py + 185, 24, "Montserrat-700", A["blue"]))
        out.append(T(mean, x + 10, py + 222, 20, "Montserrat-500", "#55607A"))
    tx = 2040
    out.append(T("Montserrat ExtraBold — TITRE", tx, py + 50, 38, "Montserrat-800", A["blue"]))
    out.append(T("Montserrat Medium — sous-titre", tx, py + 105, 28, "Montserrat-500", A["blue"]))
    out.append(T("Noto Kufi Arabic", tx, py + 160, 26, "Montserrat-600", "#55607A"))
    out.append(T("الاتحاد الأفريقي", tx + 260, py + 162, 30, "NotoKufiArabic-700", A["blue"]))
    out.append(T("Polices libres SIL OFL", tx, py + 210, 20, "Montserrat-500", "#55607A"))
    return svg_doc(W, H, "".join(out))


def multilingual():
    rows = list(TITLE)
    rh, W = 330, 3000
    H = 170 + rh * len(rows)
    out = [f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
           T("Adaptation multilingue — langues de travail de l'UA", 120, 115, 46, "Montserrat-800", A["blue"])]
    for i, lang in enumerate(rows):
        y = 170 + i * rh
        out.append(f'<rect y="{y}" width="{W}" height="{rh}" fill="{"#F4F6FA" if i % 2 else "#FFFFFF"}"/>')
        out.append(T(LANG_NAMES[lang], 120, y + rh / 2 + 10, 30,
                     "NotoKufiArabic-500" if lang == "ar" else "Montserrat-600", "#55607A"))
        b, w, h = lockup_h(A, f"ml{lang}", lang)
        out.append(placed(b, w, h, 520, y + 30, 2360, rh - 60))
    return svg_doc(W, H, "".join(out))


def arc_lines(w, h, color, opacity):
    """Background motif: echoes of the arch and trajectory."""
    out = []
    for i in range(7):
        r = 300 + i * 160
        out.append(f'<path d="M {w*0.62 - r:.0f} {h + 40} A {r} {r*0.95:.0f} 0 0 1 {w*0.62 + r*0.8:.0f} {h + 40}" '
                   f'fill="none" stroke="{color}" stroke-width="3"/>')
    return f'<g opacity="{opacity}">{"".join(out)}</g>'


def web_banner():
    W, H = 3000, 1250
    rc = arc_reversed_color()
    out = [f'<defs><linearGradient id="bb" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1A4BA8"/>'
           f'<stop offset="1" stop-color="#0B2A66"/></linearGradient></defs>',
           f'<rect width="{W}" height="{H}" fill="url(#bb)"/>', arc_lines(W, H, "#FFFFFF", 0.07)]
    out.append(placed(mark_arche(rc, "wb"), MW, MH, 220, 230, 820, 780))
    x = 1180
    out.append(T(KICKER["en"], x, 360, 40, "Montserrat-700", A["gold"], trk=0.12))
    out.append(T("AU AT THE DAWN OF ITS", x, 490, 90, "Montserrat-800", "#FFFFFF"))
    out.append(T("25TH ANNIVERSARY", x, 600, 90, "Montserrat-800", "#FFFFFF"))
    out.append(T("Leveraging the Full Potential of SAATM and", x, 720, 46, "Montserrat-500", "#FFFFFF"))
    out.append(T("New Technologies for Continental Integration", x, 785, 46, "Montserrat-500", "#FFFFFF"))
    hw = measure("#AUat25", "Montserrat-800", 42) + 50
    out.append(f'<rect x="{x}" y="860" width="{hw}" height="72" fill="{A["gold"]}"/>')
    out.append(T("#AUat25", x + 25, 912, 42, "Montserrat-800", "#0B2A66"))
    return svg_doc(W, H, "".join(out))


def card():
    W = H = 2000
    out = [f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>', arc_lines(W, H, A["blue"], 0.06)]
    b, w, h = lockup_v(A, "cd")
    out.append(placed(b, w, h, 220, 200, 1560, 1480))
    out.append(f'<rect y="{H-150}" width="{W}" height="150" fill="{A["blue"]}"/>')
    out.append(T("#AUat25   ·   #SAATM   ·   #Agenda2063", W / 2, H - 58, 44, "Montserrat-700", "#FFFFFF", "middle"))
    return svg_doc(W, H, "".join(out))


def backdrop():
    W, H = 4800, 2160
    out = [f'<rect width="{W}" height="{H}" fill="#123C8C"/>', arc_lines(W, H, "#FFFFFF", 0.06)]
    b, w, h = lockup_h(arc_reversed_color(), "bk")
    out.append(placed(b, w, h, 500, 500, 3800, 1160))
    out.append(f'<rect y="{H-60}" width="{W}" height="60" fill="{A["gold"]}"/>')
    return svg_doc(W, H, "".join(out))


def cover():
    W, H = 2100, 2970
    out = [f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
           f'<rect y="1900" width="{W}" height="1070" fill="{A["blue"]}"/>', arc_lines(W, 1900, A["blue"], 0.05)]
    out.append(placed(mark_arche(A, "cv"), MW, MH, 330, 300, 1440, 1380))
    out.append(T(KICKER["en"], 160, 2080, 38, "Montserrat-700", A["gold"], trk=0.12))
    out.append(T("AU AT THE DAWN OF ITS", 160, 2210, 92, "Montserrat-800", "#FFFFFF"))
    out.append(T("25TH ANNIVERSARY", 160, 2320, 92, "Montserrat-800", "#FFFFFF"))
    out.append(T("Leveraging the Full Potential of SAATM and", 160, 2440, 46, "Montserrat-500", "#FFFFFF"))
    out.append(T("New Technologies for Continental Integration", 160, 2502, 46, "Montserrat-500", "#FFFFFF"))
    out.append(T("Concept Note & Roadmap", 160, 2780, 44, "Montserrat-700", A["gold"]))
    return svg_doc(W, H, "".join(out))


def build_mockups():
    p = {}
    for name, fn, pw in (("banniere-web", web_banner, 3000), ("carte-numerique", card, 2000),
                         ("toile-de-fond", backdrop, 4800), ("couverture", cover, 2100)):
        p[name] = f"{OUT}/png/maquette_{name}.png"
        cairosvg.svg2png(bytestring=fn().encode(), write_to=p[name], output_width=pw)
    W, H = 3000, 4300
    body = [f'<rect width="{W}" height="{H}" fill="#E4E7EE"/>',
            T("MAQUETTES — L'ARCHE D'INTÉGRATION", 120, 150, 56, "Montserrat-800", A["blue"], trk=0.03),
            embed(p["toile-de-fond"], 120, 230, 2760, 1242),
            T("1 · Toile de fond d'événement", 120, 1540, 32, "Montserrat-600", "#3C4660"),
            embed(p["banniere-web"], 120, 1620, 2760, 1150),
            T("2 · Bannière web", 120, 2840, 32, "Montserrat-600", "#3C4660"),
            embed(p["carte-numerique"], 120, 2920, 1240, 1240),
            T("3 · Carte numérique", 120, 4230, 32, "Montserrat-600", "#3C4660"),
            embed(p["couverture"], 2880 - 877, 2920, 877, 1240),
            T("4 · Couverture de publication (A4)", 2880 - 877, 4230, 32, "Montserrat-600", "#3C4660")]
    cairosvg.svg2png(bytestring=svg_doc(W, H, "".join(body)).encode(), write_to=f"{OUT}/png/maquettes_3000px.png")


if __name__ == "__main__":
    build_files()
    cairosvg.svg2png(bytestring=board().encode(), write_to=f"{OUT}/png/planche_presentation_3000px.png")
    cairosvg.svg2png(bytestring=multilingual().encode(), write_to=f"{OUT}/png/adaptation_multilingue_3000px.png")
    build_mockups()
    print("V3 built")
