#!/usr/bin/env python3
"""Regenera las partes comunes de la web a partir de menu.json.

Qué hace:
  - Cabecera (menú con desplegables por tema) en TODAS las páginas .html.
  - Pie de página común en todas las páginas.
  - Migas de pan de cada guía según su tema.
  - Página guias/index.html («Todas las guías») con buscador.
  - Bloque de temas de la portada (entre <!--TEMAS:inicio--> y <!--TEMAS:fin-->).
  - Añade guias/ al sitemap.xml si falta.

Uso (desde la raíz del repositorio):  python tools/build.py
Si una guía de la carpeta guias/ no está en menu.json, se avisa y se coloca en «Otros temas».
"""
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
GUIAS = ROOT / "guias"
SITE = "https://cuerpobajolalupa.es"
ADS_META = '<meta name="google-adsense-account" content="ca-pub-1492478614433701">'


def esc(t):
    return html.escape(t, quote=True)


def read(p):
    return p.read_text(encoding="utf-8")


def write(p, t):
    p.write_text(t, encoding="utf-8", newline="")


def guide_info(path):
    t = read(path)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S)
    desc = re.search(r'<meta name="description" content="([^"]*)"', t)
    pub = re.search(r'"datePublished"\s*:\s*"([0-9-]+)"', t)
    title = re.sub(r"<[^>]+>", "", h1.group(1)).strip() if h1 else path.stem
    return {
        "titulo": html.unescape(title),
        "descripcion": html.unescape(desc.group(1)) if desc else "",
        "fecha": pub.group(1) if pub else "",
    }


def load_menu():
    menu = json.loads(read(ROOT / "menu.json"))
    temas = menu["temas"]
    files = {p.name for p in GUIAS.glob("*.html") if p.name != "index.html"}
    listed = set()
    for tema in temas:
        keep = []
        for g in tema["guias"]:
            if g["archivo"] not in files:
                print(f"AVISO: {g['archivo']} está en menu.json pero no existe en guias/; se omite.")
                continue
            listed.add(g["archivo"])
            g.update(guide_info(GUIAS / g["archivo"]))
            g.setdefault("corto", g["titulo"].split(":")[0])
            keep.append(g)
        tema["guias"] = keep
    missing = sorted(files - listed)
    if missing:
        print("AVISO: guías sin tema en menu.json (añádelas):", ", ".join(missing))
        otros = {"id": "otros", "nombre": "Otros temas", "descripcion": "Más guías de salud", "guias": []}
        for f in missing:
            g = {"archivo": f, **guide_info(GUIAS / f)}
            g["corto"] = g["titulo"].split(":")[0]
            otros["guias"].append(g)
        temas.append(otros)
    return [t for t in temas if t["guias"]]


SEARCH_ICON = ('<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" '
               'stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/>'
               '<path d="m20 20-3.5-3.5"/></svg>')


def header_html(temas):
    drops = []
    for t in temas:
        links = "".join(f'<a href="/guias/{g["archivo"]}">{esc(g["corto"])}</a>' for g in t["guias"])
        drops.append(
            f'<div class="dropdown"><button class="drop-toggle" type="button" aria-expanded="false">{esc(t["nombre"])}</button>'
            f'<div class="drop-menu">{links}<a class="drop-all" href="/guias/#{t["id"]}">Ver todo el tema →</a></div></div>'
        )
    return (
        '<header class="site-header"><div class="container navbar">'
        '<a class="brand" href="/"><span class="brand-mark">✚</span><span>Cuerpo Bajo la Lupa</span></a>'
        '<button class="menu-button" type="button" aria-controls="main-menu" aria-expanded="false">'
        '<span class="burger" aria-hidden="true"></span>Menú</button>'
        '<nav class="navlinks" id="main-menu" aria-label="Navegación principal">'
        + "".join(drops)
        + '<a class="nav-plain" href="/guias/">Todas las guías</a>'
        '<a class="nav-plain" href="/sobre.html">El proyecto</a>'
        f'<a class="nav-search" href="/guias/#buscar" aria-label="Buscar en la web">{SEARCH_ICON}<span>Buscar</span></a>'
        "</nav></div></header>"
    )


def footer_html(temas):
    tema_links = "".join(f'<a href="/guias/#{t["id"]}">{esc(t["nombre"])}</a>' for t in temas)
    return (
        '<footer class="site-footer"><div class="container"><div class="footer-grid">'
        '<div class="footer-about"><a class="brand" href="/"><span class="brand-mark">✚</span><span>Cuerpo Bajo la Lupa</span></a>'
        "<p>Guías de salud explicadas con claridad y contrastadas con fuentes oficiales. "
        'Divulgación del canal de YouTube <a href="https://www.youtube.com/channel/UCkz1cHuhbO_5uhVJpBQgLeg" '
        'target="_blank" rel="noopener noreferrer">Cuerpo Bajo la Lupa</a>.</p></div>'
        f'<div class="footer-col"><h4>Temas</h4>{tema_links}<a href="/guias/">Todas las guías</a></div>'
        '<div class="footer-col"><h4>Proyecto</h4><a href="/sobre.html">El proyecto</a><a href="/metodo.html">Método editorial</a></div>'
        '<div class="footer-col footer-links"><h4>Legal</h4><a href="/privacidad.html">Privacidad</a>'
        '<a href="/cookies.html">Cookies</a><a href="/aviso-legal.html">Aviso legal</a></div>'
        "</div>"
        '<div class="footer-bottom">© 2026 Cuerpo Bajo la Lupa. Información divulgativa. No sustituye una consulta médica. '
        "Ante una urgencia, llama al 112.</div>"
        "</div></footer>"
    )


def card(g, tema):
    return (
        f'<a class="guide-card" href="/guias/{g["archivo"]}" data-search="{esc((g["titulo"] + " " + g["descripcion"] + " " + tema["nombre"]).lower())}">'
        f'<span class="tag">{esc(tema["nombre"])}</span><h3>{esc(g["titulo"])}</h3>'
        f'<p>{esc(g["descripcion"])}</p></a>'
    )


def guias_index(temas, header, footer):
    total = sum(len(t["guias"]) for t in temas)
    chips = "".join(f'<a href="#{t["id"]}">{esc(t["nombre"])} <span>{len(t["guias"])}</span></a>' for t in temas)
    secciones = "".join(
        f'<section class="topic-section" id="{t["id"]}"><h2>{esc(t["nombre"])}</h2>'
        f'<p class="topic-desc">{esc(t["descripcion"])}</p>'
        f'<div class="guide-grid">{"".join(card(g, t) for g in t["guias"])}</div></section>'
        for t in temas
    )
    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">{ADS_META}<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="index,follow">
<meta name="description" content="Todas las guías de salud de Cuerpo Bajo la Lupa ordenadas por temas: tensión arterial, colesterol, diabetes, sueño y nutrición.">
<title>Todas las guías de salud | Cuerpo Bajo la Lupa</title><link rel="stylesheet" href="/styles.css"><link rel="canonical" href="{SITE}/guias/"></head>
<body>{header}<main>
<section class="pagehead"><div class="container"><div class="breadcrumbs"><a href="/">Inicio</a> / Guías</div>
<h1>Todas las guías</h1><p class="lead">{total} guías de salud ordenadas por temas, con sus fuentes oficiales.</p>
<form class="search" id="buscar" role="search" onsubmit="return false"><label class="sr-only" for="q">Buscar</label>
<input type="search" id="q" name="q" placeholder="Busca: colesterol, tensión, glucosa…" autocomplete="off"></form>
<p class="search-empty" hidden>No hay ninguna guía con esas palabras todavía.</p>
<nav class="topic-chips" aria-label="Temas">{chips}</nav></div></section>
<div class="container all-guides">{secciones}</div>
</main>{footer}<script src="/site.js" defer></script></body></html>
"""


def home_topics(temas):
    tiles = "".join(
        f'<a class="topic-tile" href="/guias/#{t["id"]}"><h3>{esc(t["nombre"])}</h3>'
        f'<p>{esc(t["descripcion"])}</p><span>{len(t["guias"])} guías →</span></a>'
        for t in temas
    )
    return f'<div class="topic-grid">{tiles}</div>'


def main():
    temas = load_menu()
    header, footer = header_html(temas), footer_html(temas)
    tema_de = {g["archivo"]: t for t in temas for g in t["guias"]}

    write(GUIAS / "index.html", guias_index(temas, header, footer))

    pages = [p for p in ROOT.glob("*.html")] + [p for p in GUIAS.glob("*.html")]
    for p in pages:
        t = read(p)
        o = t
        t = re.sub(r"<header\b.*?</header>", header, t, count=1, flags=re.S)
        t = re.sub(r"<footer\b.*?</footer>", footer, t, count=1, flags=re.S)
        if ADS_META not in t:
            t = t.replace('<meta charset="utf-8">', '<meta charset="utf-8">' + ADS_META, 1)
        if p.parent == GUIAS and p.name in tema_de:
            tm = tema_de[p.name]
            crumbs = (f'<div class="breadcrumbs"><a href="/">Inicio</a> / <a href="/guias/">Guías</a> / '
                      f'<a href="/guias/#{tm["id"]}">{esc(tm["nombre"])}</a></div>')
            t = re.sub(r'<div class="breadcrumbs">.*?</div>', crumbs, t, count=1, flags=re.S)
        if p.name == "index.html" and p.parent == ROOT:
            t = re.sub(r"<!--TEMAS:inicio-->.*?<!--TEMAS:fin-->",
                       "<!--TEMAS:inicio-->" + home_topics(temas) + "<!--TEMAS:fin-->", t, count=1, flags=re.S)
        if t != o:
            write(p, t)
            print("actualizada", p.relative_to(ROOT))

    sm = ROOT / "sitemap.xml"
    s = read(sm)
    if f"<loc>{SITE}/guias/</loc>" not in s:
        s = s.replace("</urlset>", f"<url><loc>{SITE}/guias/</loc></url></urlset>")
        write(sm, s)
        print("sitemap: añadida /guias/")
    for f in GUIAS.glob("*.html"):
        if f.name != "index.html" and f"/guias/{f.name}</loc>" not in s:
            print(f"AVISO: {f.name} no está en sitemap.xml")
    print("OK:", sum(len(t["guias"]) for t in temas), "guías en", len(temas), "temas")


if __name__ == "__main__":
    sys.exit(main())
