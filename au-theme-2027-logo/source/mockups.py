"""Three mock-ups per concept: digital card, event backdrop, publication cover."""
import cairosvg
from marks import CONCEPTS, PALETTE as P, reversed_palette, mono
from build import OUT, MW, MH, svg_doc, mark, lockup_h, lockup_v, placed, T

FULL_EN = ["AU at the Dawn of its 25th Anniversary:", "Leveraging the Full Potential of SAATM",
           "and New Technologies for Continental Integration"]


def pattern(key, w, h, step, pal, opacity, uid):
    """Tile the mark as a faint background motif."""
    out = []
    i = 0
    for row, y in enumerate(range(-step // 2, h + step, step)):
        for x in range(-step + (row % 2) * step // 2, w + step, step):
            out.append(placed(mark(key, pal, f"{uid}{i}"), MW, MH, x, y, step * 0.55, step * 0.55))
            i += 1
    return f'<g opacity="{opacity}">{"".join(out)}</g>'


def card(key):
    W = H = 2000
    rp = reversed_palette()
    body = [f'<rect width="{W}" height="{H}" fill="{P["night"]}"/>',
            pattern(key, W, H, 360, mono("#FFFFFF"), 0.05, f"{key}cp"),
            f'<rect x="0" y="{H-24}" width="{W/5}" height="24" fill="{P["green"]}"/>',
            f'<rect x="{W/5}" y="{H-24}" width="{W/5}" height="24" fill="{P["sky"]}"/>',
            f'<rect x="{2*W/5}" y="{H-24}" width="{W/5}" height="24" fill="{P["gold"]}"/>',
            f'<rect x="{3*W/5}" y="{H-24}" width="{W/5}" height="24" fill="{P["coral"]}"/>',
            f'<rect x="{4*W/5}" y="{H-24}" width="{W/5}" height="24" fill="#FFFFFF"/>']
    b, w, h = lockup_v(key, rp, f"{key}-card")
    body.append(placed(b, w, h, 300, 260, 1400, 1150))
    body.append(T("1 MARKET · 1 SKY · 1 DIGITAL AFRICA", W / 2, 1600, 46, "Montserrat-700", P["gold"], "middle", 0.12))
    body.append(T("#AUat25   ·   #SAATM   ·   #Agenda2063", W / 2, 1700, 38, "Montserrat-500", "#FFFFFF", "middle", 0.04))
    return svg_doc(W, H, "".join(body))


def backdrop(key):
    W, H = 4800, 2160
    rp = reversed_palette()
    body = [f'<defs><linearGradient id="bg{key}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="#132A5C"/><stop offset="1" stop-color="{P["night"]}"/></linearGradient></defs>',
            f'<rect width="{W}" height="{H}" fill="url(#bg{key})"/>',
            pattern(key, W, H, 420, mono("#FFFFFF"), 0.045, f"{key}bp")]
    b, w, h = lockup_h(key, rp, f"{key}-bd")
    body.append(placed(b, w, h, 600, 520, 3600, 900))
    for i, line in enumerate(FULL_EN):
        body.append(T(line, W / 2, 1620 + i * 92, 66, "Montserrat-600", "#FFFFFF", "middle"))
    body.append(T("#AUat25  ·  2027", W / 2, 2000, 44, "Montserrat-700", P["gold"], "middle", 0.25))
    return svg_doc(W, H, "".join(body))


def cover(key):
    W, H = 2100, 2970
    body = [f'<rect width="{W}" height="{H}" fill="#F6F4EF"/>',
            f'<rect x="0" y="2150" width="{W}" height="820" fill="{P["night"]}"/>',
            T("AFRICAN UNION · THEME OF THE YEAR 2027", 160, 260, 40, "Montserrat-700", P["green"], trk=0.14)]
    body.append(placed(mark(key, P, f"{key}-cov"), MW, MH, 260, 420, 1580, 1300))
    body.append(T("AU AT 25", 160, 1960, 150, "Montserrat-800", P["night"]))
    for i, line in enumerate(FULL_EN):
        body.append(T(line, 160, 2330 + i * 78, 58, "Montserrat-600", "#FFFFFF"))
    body.append(T("Concept Note & Roadmap", 160, 2700, 46, "Montserrat-500", P["gold"]))
    return svg_doc(W, H, "".join(body))


def build(key):
    paths = {}
    for name, fn, pw in (("card", card, 2000), ("backdrop", backdrop, 4800), ("cover", cover, 2100)):
        svg = fn(key)
        p = f"{OUT}/{key}/png/maquette_{name}.png"
        cairosvg.svg2png(bytestring=svg.encode(), write_to=p, output_width=pw)
        paths[name] = p
    # composite sheet: backdrop on top, card + cover below
    import base64
    W, H = 3000, 2900
    def img(path, x, y, w, h):
        data = base64.b64encode(open(path, "rb").read()).decode()
        return (f'<rect x="{x+12}" y="{y+16}" width="{w}" height="{h}" fill="#000" opacity="0.16"/>'
                f'<image href="data:image/png;base64,{data}" x="{x}" y="{y}" width="{w}" height="{h}"/>')
    body = [f'<rect width="{W}" height="{H}" fill="#E4E5E9"/>',
            T("MAQUETTES — " + CONCEPTS[key][0].upper(), 120, 150, 56, "Montserrat-800", P["night"], trk=0.03),
            img(paths["backdrop"], 120, 230, 2760, 1242),
            T("1 · Toile de fond d'événement (scène, 16:7)", 120, 1540, 32, "Montserrat-600", "#3C4660"),
            img(paths["card"], 120, 1600, 1140, 1140),
            T("2 · Carte numérique (réseaux sociaux, 1:1)", 120, 2810, 32, "Montserrat-600", "#3C4660"),
            img(paths["cover"], 2880 - 806, 1600, 806, 1140),
            T("3 · Couverture de publication (A4)", 2880 - 806, 2810, 32, "Montserrat-600", "#3C4660")]
    cairosvg.svg2png(bytestring=svg_doc(W, H, "".join(body)).encode(),
                     write_to=f"{OUT}/{key}/png/maquettes_3000px.png")


if __name__ == "__main__":
    for k in CONCEPTS:
        build(k)
        print("mockups", k)
