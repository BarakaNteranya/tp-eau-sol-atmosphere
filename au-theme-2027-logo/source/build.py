"""Build all logo files, boards, multilingual sheets and mock-ups."""
import os
import cairosvg
from marks import CONCEPTS, PALETTE, mono, reversed_palette
from textpath import text_path, measure

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MW, MH = 250, 240  # mark box

LANG = {
    "en": ("AU THEME OF THE YEAR 2027", "AU AT 25", "SAATM · NEW TECHNOLOGIES · INTEGRATION"),
    "fr": ("THÈME DE L'ANNÉE 2027 DE L'UA", "L'UA À 25 ANS", "MUTAA · NOUVELLES TECHNOLOGIES · INTÉGRATION"),
    "pt": ("TEMA DO ANO 2027 DA UA", "A UA AOS 25 ANOS", "SAATM · NOVAS TECNOLOGIAS · INTEGRAÇÃO"),
    "es": ("TEMA DEL AÑO 2027 DE LA UA", "LA UA A LOS 25 AÑOS", "SAATM · NUEVAS TECNOLOGÍAS · INTEGRACIÓN"),
    "sw": ("KAULIMBIU YA MWAKA 2027 YA AU", "AU MIAKA 25", "SAATM · TEKNOLOJIA MPYA · UTANGAMANO"),
    "ar": ("موضوع عام 2027 للاتحاد الأفريقي", "الاتحاد الأفريقي في عامه الخامس والعشرين", "السوق الموحدة للنقل الجوي · التكنولوجيات الجديدة · التكامل"),
}
LANG_NAMES = {"en": "English", "fr": "Français", "pt": "Português", "es": "Español", "sw": "Kiswahili", "ar": "العربية"}


def svg_doc(w, h, body, bg=None, vb=None):
    vb = vb or f"0 0 {w} {h}"
    bgr = f'<rect x="{vb.split()[0]}" y="{vb.split()[1]}" width="100%" height="100%" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{vb}">'
            f"{bgr}{body}</svg>")


def mark(key, pal, uid):
    return CONCEPTS[key][1](pal, uid=uid)


def fonts_for(lang):
    if lang == "ar":
        return "NotoKufiArabic-500", "NotoKufiArabic-700", "NotoKufiArabic-500", 0.0
    return "Montserrat-600", "Montserrat-800", "Montserrat-600", 0.12


def title_block(lang, pal, x, y, anchor="start", scale=1.0):
    """Three-line campaign title. Returns (svg, width, height)."""
    small, big, sub = LANG[lang]
    f_small, f_big, f_sub, trk = fonts_for(lang)
    s1, s2, s3 = 15 * scale, 66 * scale, 16.5 * scale
    if lang == "ar":
        s1, s2, s3 = 16 * scale, 44 * scale, 15 * scale
    w = max(measure(small, f_small, s1, trk), measure(big, f_big, s2, -0.01 if lang != "ar" else 0),
            measure(sub, f_sub, s3, trk * 0.4))
    accent = pal["green"] if pal["night"] != "#FFFFFF" else pal["gold"]
    y1, y2, y3 = y + s1, y + s1 + 14 * scale + s2 * 0.74, y + s1 + 14 * scale + s2 * 0.74 + 16 * scale + s3
    if lang == "ar":
        y2 = y + s1 + 18 * scale + s2 * 0.9
        y3 = y2 + 18 * scale + s3
    body = (
        f'<path d="{text_path(small, x, y1, f_small, s1, anchor, trk)}" fill="{accent}"/>'
        f'<path d="{text_path(big, x, y2, f_big, s2, anchor, -0.01 if lang != "ar" else 0)}" fill="{pal["night"]}"/>'
        f'<path d="{text_path(sub, x, y3, f_sub, s3, anchor, trk * 0.4)}" fill="{pal["night"]}"/>'
    )
    return body, w, y3 - y + 6 * scale


def lockup_h(key, pal, uid, lang="en"):
    """Horizontal lockup. Returns (body, w, h)."""
    gap = 34
    tb, tw, th = title_block(lang, pal, 0, 0)
    ty = (MH - th) / 2 + 4
    if lang == "ar":  # right-to-left: mark on the right
        tb, tw, th = title_block(lang, pal, tw, ty, anchor="end")
        body = f"<g>{tb}</g>" + f'<g transform="translate({tw + gap},0)">{mark(key, pal, uid)}</g>'
    else:
        tb, tw, th = title_block(lang, pal, MW + gap, ty)
        body = mark(key, pal, uid) + tb
    return body, MW + gap + tw + 4, MH


def lockup_v(key, pal, uid, lang="en"):
    tb0, tw, th = title_block(lang, pal, 0, 0)
    W = max(tw, MW) + 8
    mx = (W - MW) / 2
    tb, _, th = title_block(lang, pal, W / 2, MH + 22, anchor="middle")
    body = f'<g transform="translate({mx},0)">{mark(key, pal, uid)}</g>' + tb
    return body, W, MH + 22 + th


def save(path, svg, png_w=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    if png_w:
        cairosvg.svg2png(bytestring=svg.encode(), write_to=path.replace(".svg", ".png").replace("/svg/", "/png/"),
                         output_width=png_w)


VARIANTS = {
    "color": (PALETTE, None),
    "mono-black": (mono("#111111"), None),
    "reversed": (reversed_palette(), PALETTE["night"]),
    "mono-white": (mono("#FFFFFF"), "#111111"),
}


def build_logo_files(key):
    d = f"{OUT}/{key}"
    os.makedirs(f"{d}/png", exist_ok=True)
    for vname, (pal, bg) in VARIANTS.items():
        uid = f"{key}-{vname}"
        pad = 20
        save(f"{d}/svg/mark_{vname}.svg",
             svg_doc(MW + 2 * pad, MH + 2 * pad, mark(key, pal, uid), bg, f"{-pad} {-pad} {MW + 2 * pad} {MH + 2 * pad}"),
             png_w=2000)
        b, w, h = lockup_h(key, pal, uid + "h")
        save(f"{d}/svg/lockup-horizontal_{vname}.svg",
             svg_doc(w + 2 * pad, h + 2 * pad, b, bg, f"{-pad} {-pad} {w + 2 * pad} {h + 2 * pad}"), png_w=3000)
        b, w, h = lockup_v(key, pal, uid + "v")
        save(f"{d}/svg/lockup-vertical_{vname}.svg",
             svg_doc(w + 2 * pad, h + 2 * pad, b, bg, f"{-pad} {-pad} {w + 2 * pad} {h + 2 * pad}"), png_w=2400)


# ---------------------------------------------------------------- presentation board
SWATCHES = [("night", "Bleu nuit continental", "Ciel, profondeur, institution"),
            ("sky", "Bleu ciel ouvert", "SAATM, connectivité, numérique"),
            ("green", "Vert intégration", "Croissance, Agenda 2063"),
            ("gold", "Or de l'aube", "25 ans, aube, prospérité"),
            ("coral", "Terre cuite", "Énergie, jeunesse")]


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def T(text, x, y, size, font="Montserrat-500", fill="#0E1E45", anchor="start", trk=0.0):
    return f'<path d="{text_path(text, x, y, font, size, anchor, trk)}" fill="{fill}"/>'


def placed(body, w, h, x, y, box_w, box_h):
    s = min(box_w / w, box_h / h)
    ox = x + (box_w - w * s) / 2
    oy = y + (box_h - h * s) / 2
    return f'<g transform="translate({ox:.1f},{oy:.1f}) scale({s:.4f})">{body}</g>'


def board(key, idx):
    name = CONCEPTS[key][0]
    W, H = 3000, 2000
    P = PALETTE
    out = [f'<rect width="{W}" height="{H}" fill="#F6F4EF"/>']
    out.append(T(f"PISTE {idx}", 120, 150, 30, "Montserrat-700", P["coral"], trk=0.2))
    out.append(T(name.upper(), 120, 235, 72, "Montserrat-800", P["night"], trk=0.02))
    out.append(T("Logo — Thème de l'année 2027 de l'Union africaine · ébauche", 120, 290, 30, "Montserrat-500", "#55607A"))
    # hero: horizontal lockup on white card
    out.append(f'<rect x="120" y="350" width="1720" height="760" rx="24" fill="#FFFFFF"/>')
    b, w, h = lockup_h(key, P, f"{key}-bh")
    out.append(placed(b, w, h, 200, 420, 1560, 620))
    # mark alone, colour
    out.append(f'<rect x="1900" y="350" width="980" height="760" rx="24" fill="#FFFFFF"/>')
    out.append(placed(mark(key, P, f"{key}-bm"), MW, MH, 2000, 400, 780, 600))
    out.append(T("Symbole seul (sans titre)", 2390, 1070, 26, "Montserrat-600", "#55607A", "middle"))
    # variants row
    vy = 1160
    tiles = [("Monochrome", mono("#111111"), "#FFFFFF"), ("Inversé couleur", reversed_palette(), P["night"]),
             ("Inversé blanc", mono("#FFFFFF"), "#111111"), ("Sur couleur", mono("#FFFFFF"), P["green"])]
    for i, (lab, pal, bg) in enumerate(tiles):
        x = 120 + i * 445
        out.append(f'<rect x="{x}" y="{vy}" width="420" height="420" rx="20" fill="{bg}"/>')
        out.append(placed(mark(key, pal, f"{key}-t{i}"), MW, MH, x + 60, vy + 50, 300, 290))
        out.append(T(lab, x + 210, vy + 390, 24, "Montserrat-600",
                     "#111111" if bg == "#FFFFFF" else "#FFFFFF", "middle"))
    # small sizes test
    sx = 1900
    out.append(f'<rect x="{sx}" y="{vy}" width="980" height="420" rx="20" fill="#FFFFFF"/>')
    out.append(T("Test petites tailles", sx + 40, vy + 60, 26, "Montserrat-700", P["night"]))
    px = sx + 40
    for size in (160, 96, 64, 40, 24):
        out.append(placed(mark(key, P, f"{key}-s{size}"), MW, MH, px, vy + 330 - size, size, size))
        out.append(T(f"{size}px", px + size / 2, vy + 375, 20, "Montserrat-500", "#55607A", "middle"))
        px += size + 50
    # palette
    py = 1650
    for i, (k, lab, mean) in enumerate(SWATCHES):
        x = 120 + i * 360
        out.append(f'<rect x="{x}" y="{py}" width="340" height="120" rx="14" fill="{P[k]}"/>')
        r, g, b_ = hex_rgb(P[k])
        out.append(T(P[k], x + 20, py + 160, 22, "Montserrat-700", P["night"]))
        out.append(T(f"RGB {r} {g} {b_}", x + 140, py + 160, 18, "Montserrat-500", "#55607A"))
        out.append(T(lab, x + 20, py + 195, 22, "Montserrat-600", P["night"]))
        out.append(T(mean, x + 20, py + 225, 18, "Montserrat-500", "#55607A"))
    # typography
    tx = 1990
    out.append(T("Typographie", tx, py + 30, 26, "Montserrat-700", P["night"]))
    out.append(T("Montserrat ExtraBold — titres", tx, py + 85, 34, "Montserrat-800", P["night"]))
    out.append(T("Montserrat SemiBold — sous-titres & texte", tx, py + 130, 26, "Montserrat-600", P["night"]))
    out.append(T("Noto Kufi Arabic —", tx, py + 185, 26, "Montserrat-600", P["night"]))
    out.append(T("الاتحاد الأفريقي في عامه الخامس والعشرين", tx + measure("Noto Kufi Arabic — ", "Montserrat-600", 26) + 4, py + 185, 26, "NotoKufiArabic-500", P["night"]))
    out.append(T("Polices libres (SIL OFL), compatibles EN · FR · PT · ES · SW · AR", tx, py + 230, 20,
                 "Montserrat-500", "#55607A"))
    return svg_doc(W, H, "".join(out))


def multilingual(key):
    W = 3000
    rows = list(LANG)
    rh = 300
    H = 160 + rh * len(rows)
    out = [f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
           T("Adaptation multilingue du titre — langues de travail de l'UA", 120, 110, 44, "Montserrat-800", PALETTE["night"])]
    for i, lang in enumerate(rows):
        y = 160 + i * rh
        out.append(f'<rect x="0" y="{y}" width="{W}" height="{rh}" fill="{"#F6F4EF" if i % 2 else "#FFFFFF"}"/>')
        out.append(T(LANG_NAMES[lang], 120, y + rh / 2 + 10, 30, "NotoKufiArabic-500" if lang == "ar" else "Montserrat-600", "#55607A"))
        b, w, h = lockup_h(key, PALETTE, f"{key}-ml{lang}", lang)
        out.append(placed(b, w, h, 520, y + 30, 2360, rh - 60) if lang != "ar" else
                   placed(b, w, h, 520, y + 30, 2360, rh - 60))
    return svg_doc(W, H, "".join(out))


if __name__ == "__main__":
    for i, key in enumerate(CONCEPTS, 1):
        build_logo_files(key)
        save(f"{OUT}/{key}/svg/_board.svg", board(key, i))
        cairosvg.svg2png(url=f"{OUT}/{key}/svg/_board.svg", write_to=f"{OUT}/{key}/png/planche_presentation_3000px.png")
        os.remove(f"{OUT}/{key}/svg/_board.svg")
        ml = multilingual(key)
        cairosvg.svg2png(bytestring=ml.encode(), write_to=f"{OUT}/{key}/png/adaptation_multilingue_3000px.png")
        print("built", key)
