"""Genera la imagen de cada guía (1200x630) para Facebook, WhatsApp y Google Discover.

Cada guía nueva: añade una entrada en PORTADAS (archivo sin .html) con
  tema, titular (pregunta corta que enganche), sub (una línea; solo cifras que estén en la guía)
  y dibujo (uno de los de DIBUJOS) con sus parámetros.
Después: python tools/portadas.py   (crea img/guias/<archivo>.png)
         python tools/build.py      (pone esa imagen como og:image de la guía)
Necesita Google Chrome o Microsoft Edge instalado (lo usa sin ventana para hacer la captura).
"""
import shutil
import subprocess
import sys
import tempfile
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "img" / "guias"

TEMAS = {
    "corazon": ("Corazón y tensión", "#c8323a", "#e2545b"),
    "colesterol": ("Colesterol", "#d9730d", "#ee8f2e"),
    "diabetes": ("Diabetes y azúcar", "#1c64c4", "#3b82e0"),
    "sueno": ("Sueño", "#3f3596", "#5a4fbf"),
    "habitos": ("Hábitos y nutrición", "#0d7a64", "#1d9a80"),
}

PORTADAS = {
    'palpitaciones-cardiacas': dict(tema="corazon", titular="¿Notas latidos extraños?", sub="Qué observar y cuándo llamar al 112", dibujo=("corazon_ecg",)),
    'insomnio': dict(tema="sueno", titular="¿Por qué no consigues dormir?", sub="Diario de sueño y cuándo pedir ayuda", dibujo=("cama",)),
    "tension-arterial-valores-normales": dict(tema="corazon", titular="¿130/85 es tensión normal?",
        sub="Tabla con los valores de referencia y cuándo es alta", dibujo=("tensiometro", "130", "85")),
    "tension-alta-sintomas": dict(tema="corazon", titular="Tensión alta: ¿da síntomas?",
        sub="Síntomas, causas y qué hacer", dibujo=("tensiometro", "150", "90")),
    "tension-baja": dict(tema="corazon", titular="¿Tu tensión está baja?",
        sub="Por debajo de 90/60: síntomas y qué hacer", dibujo=("tensiometro", "88", "58")),
    "presion-en-casa": dict(tema="corazon", titular="¿Te mides bien la tensión en casa?",
        sub="4 pasos y los errores más frecuentes", dibujo=("tensiometro_ok",)),
    "sintomas-infarto": dict(tema="corazon", titular="Señales de un posible infarto",
        sub="Cuándo llamar al 112 sin esperar", dibujo=("corazon_ecg",)),
    "colesterol-valores-normales": dict(tema="colesterol", titular="¿Sabes leer tu análisis de colesterol?",
        sub="LDL, HDL y triglicéridos, línea por línea", dibujo=("analisis",)),
    "colesterol-ldl-alto": dict(tema="colesterol", titular="Colesterol LDL alto: ¿cuánto es demasiado?",
        sub="Normal: menos de 100 mg/dL. Mira la tabla", dibujo=("arteria",)),
    "colesterol-hdl-bajo": dict(tema="colesterol", titular="¿Tu colesterol bueno está bajo?",
        sub="Lo deseable: 60 mg/dL o más", dibujo=("hdl_flecha",)),
    "como-bajar-el-colesterol": dict(tema="colesterol", titular="Cómo bajar el colesterol",
        sub="Hábitos que funcionan y cuándo hace falta medicación", dibujo=("bajar",)),
    "trigliceridos-altos": dict(tema="colesterol", titular="Triglicéridos altos: ¿qué significan?",
        sub="Normal: menos de 150 mg/dL. Causas y cómo bajarlos", dibujo=("gota_grasa",)),
    "glucosa-ayunas-valores-normales": dict(tema="diabetes", titular="¿Tu glucosa en ayunas es normal?",
        sub="Normal, prediabetes o diabetes: la tabla", dibujo=("glucometro", "100")),
    "hemoglobina-glicosilada-hba1c": dict(tema="diabetes", titular="Hemoglobina glicosilada: ¿qué dice tu cifra?",
        sub="5,7 %, 6,5 %… la tabla explicada", dibujo=("hematie",)),
    "prediabetes": dict(tema="diabetes", titular="¿Tienes prediabetes sin saberlo?",
        sub="Glucosa en ayunas de 100 a 125 mg/dL", dibujo=("glucometro", "110")),
    "resistencia-a-la-insulina": dict(tema="diabetes", titular="¿Tu insulina funciona bien?",
        sub="Señales, análisis y qué hacer", dibujo=("llave_celula",)),
    "sindrome-metabolico": dict(tema="diabetes", titular="¿Cumples 3 de estos 5 criterios?",
        sub="Síndrome metabólico: la tabla y qué hacer", dibujo=("lista_criterios",)),
    "apnea-del-sueno": dict(tema="sueno", titular="¿Roncas? Podría ser apnea del sueño",
        sub="Síntomas, diagnóstico y tratamiento", dibujo=("cama",)),
    "dormir-corazon": dict(tema="sueno", titular="¿Cuántas horas debes dormir?",
        sub="Adultos: de 7 a 9 horas. Tabla por edad", dibujo=("reloj_luna", "7-9 h")),
    "caminar-corazon": dict(tema="habitos", titular="¿Cuánto hay que caminar a la semana?",
        sub="Lo que recomienda la OMS y si hacen falta 10.000 pasos", dibujo=("huellas", "150-300 min")),
    "magnesio-para-que-sirve": dict(tema="habitos", titular="Magnesio: ¿para qué sirve?",
        sub="Alimentos ricos y síntomas de falta", dibujo=("magnesio",)),
}

INK = "#1b2430"


def tensiometro(c, sys_="", dia="", ok=False):
    pantalla = (
        f'<text x="118" y="150" font-size="22" font-weight="700" fill="#4b5a6a">SYS</text>'
        f'<text x="290" y="170" font-size="76" font-weight="900" fill="{INK}" text-anchor="end">{sys_}</text>'
        f'<text x="118" y="215" font-size="22" font-weight="700" fill="#4b5a6a">DIA</text>'
        f'<text x="290" y="228" font-size="56" font-weight="900" fill="{INK}" text-anchor="end">{dia}</text>'
    ) if not ok else (
        f'<path d="M150 170 l35 35 l70 -75" fill="none" stroke="{c}" stroke-width="26" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    return (
        f'<path d="M335 230 C 400 250 395 330 330 345" fill="none" stroke="#27313d" stroke-width="12" stroke-linecap="round"/>'
        f'<rect x="250" y="320" width="120" height="60" rx="16" fill="#27313d"/>'
        f'<rect x="60" y="70" width="280" height="280" rx="40" fill="#fff"/>'
        f'<rect x="92" y="102" width="216" height="145" rx="16" fill="#e3f1ec"/>' + pantalla +
        f'<circle cx="200" cy="295" r="28" fill="{c}"/><circle cx="125" cy="295" r="14" fill="#cfd8df"/><circle cx="275" cy="295" r="14" fill="#cfd8df"/>'
    )


HEART = "M200 345 C 80 265 35 195 65 130 C 95 65 172 68 200 122 C 228 68 305 65 335 130 C 365 195 320 265 200 345 Z"


def corazon_ecg(c):
    return (
        f'<path d="{HEART}" fill="#fff"/>'
        f'<polyline points="40,215 135,215 160,170 188,270 218,130 245,215 360,215" fill="none" stroke="{c}" stroke-width="14" stroke-linejoin="round" stroke-linecap="round"/>'
        f'<circle cx="320" cy="85" r="56" fill="#ffd23f"/><text x="320" y="103" font-size="48" font-weight="900" fill="{INK}" text-anchor="middle">112</text>'
    )


def lupa(x, y, r, color="#27313d"):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="rgba(255,255,255,.35)" stroke="{color}" stroke-width="16"/>'
            f'<line x1="{x + r * .72}" y1="{y + r * .72}" x2="{x + r * 1.5}" y2="{y + r * 1.5}" stroke="{color}" stroke-width="24" stroke-linecap="round"/>')


def analisis(c):
    filas = [("Total", 150, "#9aa7b3"), ("LDL", 190, c), ("HDL", 110, "#2e9e6a"), ("TG", 140, "#e6b422")]
    s = '<rect x="80" y="40" width="240" height="320" rx="20" fill="#fff"/><rect x="80" y="40" width="240" height="56" rx="20" fill="#27313d"/><rect x="80" y="76" width="240" height="20" fill="#27313d"/>'
    s += '<text x="200" y="78" font-size="24" font-weight="800" fill="#fff" text-anchor="middle">ANÁLISIS</text>'
    for i, (n, w, col) in enumerate(filas):
        y = 140 + i * 52
        s += f'<text x="102" y="{y}" font-size="22" font-weight="800" fill="{INK}">{n}</text>'
        s += f'<rect x="172" y="{y - 18}" width="{w * .6:.0f}" height="20" rx="10" fill="{col}"/>'
    return s + lupa(285, 290, 52)


def arteria(c):
    return (
        '<defs><clipPath id="lum"><circle cx="200" cy="200" r="105"/></clipPath></defs>'
        '<circle cx="200" cy="200" r="160" fill="#fbd5cf"/><circle cx="200" cy="200" r="130" fill="#f4a59a"/>'
        '<circle cx="200" cy="200" r="105" fill="#b71c1c"/>'
        '<g clip-path="url(#lum)"><ellipse cx="150" cy="140" rx="120" ry="78" fill="#ffd23f"/>'
        '<circle cx="120" cy="120" r="12" fill="#ffe680"/><circle cx="170" cy="105" r="9" fill="#ffe680"/><circle cx="95" cy="165" r="8" fill="#ffe680"/></g>'
        '<ellipse cx="235" cy="250" rx="26" ry="16" fill="#e53935"/><ellipse cx="275" cy="210" rx="22" ry="14" fill="#e53935"/>'
        f'<rect x="250" y="30" width="130" height="58" rx="29" fill="#fff"/><text x="315" y="70" font-size="32" font-weight="900" fill="{c}" text-anchor="middle">LDL</text>'
    )


def hdl_flecha(c):
    return (
        '<circle cx="200" cy="215" r="160" fill="#fbd5cf"/><circle cx="200" cy="215" r="130" fill="#f4a59a"/>'
        '<circle cx="200" cy="215" r="105" fill="#b71c1c"/>'
        '<ellipse cx="160" cy="250" rx="26" ry="16" fill="#e53935"/><ellipse cx="245" cy="270" rx="22" ry="14" fill="#e53935"/>'
        '<ellipse cx="230" cy="175" rx="20" ry="13" fill="#e53935"/>'
        '<path d="M200 300 L200 150" stroke="#fff" stroke-width="26" stroke-linecap="round"/>'
        '<path d="M150 185 L200 125 L250 185" fill="none" stroke="#fff" stroke-width="26" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<rect x="250" y="20" width="130" height="58" rx="29" fill="#fff"/><text x="315" y="60" font-size="32" font-weight="900" fill="{c}" text-anchor="middle">HDL</text>'
    )


def bajar(c):
    return (
        '<rect x="50" y="60" width="300" height="230" rx="24" fill="#fff"/>'
        '<line x1="85" y1="255" x2="320" y2="255" stroke="#cfd8df" stroke-width="6"/>'
        f'<polyline points="90,100 160,130 210,170 260,200 300,235" fill="none" stroke="{c}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="M282 250 L318 245 L305 212 Z" fill="{c}"/>'
        '<path d="M120 380 C 70 340 80 290 150 280 C 160 330 150 360 120 380 Z" fill="#2e9e6a"/>'
        '<path d="M190 385 C 180 330 220 300 275 310 C 265 350 240 380 190 385 Z" fill="#43b97f"/>'
        '<path d="M140 380 L135 300" stroke="#1d7a4e" stroke-width="5"/>'
    )


def gota_grasa(c):
    return (
        '<path d="M200 30 C 200 30 80 175 80 255 A120 120 0 0 0 320 255 C 320 175 200 30 200 30 Z" fill="#d32f2f"/>'
        '<path d="M140 220 C 135 190 150 165 165 150" fill="none" stroke="#ef6b6b" stroke-width="12" stroke-linecap="round"/>'
        '<circle cx="230" cy="245" r="38" fill="#ffd23f"/><circle cx="160" cy="290" r="26" fill="#ffd23f"/>'
        '<circle cx="250" cy="320" r="18" fill="#ffd23f"/><circle cx="195" cy="200" r="14" fill="#ffd23f"/>'
        '<circle cx="220" cy="232" r="10" fill="#fff3b0"/>'
    )


def glucometro(c, valor):
    return (
        '<rect x="180" y="10" width="40" height="80" rx="6" fill="#f2f2f2"/><rect x="180" y="10" width="40" height="22" rx="6" fill="#e0b84a"/>'
        '<path d="M300 40 C 300 40 268 80 268 102 A32 32 0 0 0 332 102 C 332 80 300 40 300 40 Z" fill="#d32f2f"/>'
        '<rect x="105" y="70" width="190" height="300" rx="40" fill="#fff"/>'
        '<rect x="130" y="100" width="140" height="130" rx="16" fill="#dcebfb"/>'
        f'<text x="200" y="180" font-size="62" font-weight="900" fill="{INK}" text-anchor="middle">{valor}</text>'
        '<text x="200" y="212" font-size="22" font-weight="700" fill="#4b5a6a" text-anchor="middle">mg/dL</text>'
        f'<circle cx="200" cy="290" r="30" fill="{c}"/><circle cx="145" cy="290" r="14" fill="#cfd8df"/><circle cx="255" cy="290" r="14" fill="#cfd8df"/>'
    )


def cubo(x, y, rot):
    return (f'<g transform="rotate({rot} {x} {y})"><rect x="{x - 30}" y="{y - 30}" width="60" height="60" rx="8" fill="#fff" stroke="#d6dde5" stroke-width="4"/>'
            f'<circle cx="{x - 10}" cy="{y - 8}" r="4" fill="#d6dde5"/><circle cx="{x + 10}" cy="{y + 8}" r="4" fill="#d6dde5"/></g>')


def hematie(c):
    return (
        '<ellipse cx="200" cy="200" rx="140" ry="105" fill="#d32f2f"/><ellipse cx="200" cy="200" rx="80" ry="52" fill="#a91f1f"/>'
        + cubo(85, 110, -15) + cubo(315, 120, 12) + cubo(300, 300, -8) + cubo(105, 295, 20) +
        f'<rect x="125" y="330" width="150" height="56" rx="28" fill="#fff"/><text x="200" y="369" font-size="30" font-weight="900" fill="{c}" text-anchor="middle">HbA1c</text>'
    )


def luna(x, y, r, fondo=None):
    m = f"luna{x}{y}"
    return (f'<defs><mask id="{m}"><rect width="400" height="400" fill="#fff"/>'
            f'<circle cx="{x + r * .45}" cy="{y - r * .3}" r="{r * .85}" fill="#000"/></mask></defs>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffd23f" mask="url(#{m})"/>')


def cama(c, fondo):
    return (
        luna(310, 80, 50, fondo) +
        '<text x="200" y="120" font-size="44" font-weight="900" fill="#fff">Z</text><text x="235" y="80" font-size="32" font-weight="900" fill="#fff">z</text><text x="262" y="50" font-size="24" font-weight="900" fill="#fff">z</text>'
        '<rect x="30" y="200" width="22" height="170" rx="8" fill="#27313d"/><rect x="348" y="260" width="22" height="110" rx="8" fill="#27313d"/>'
        '<rect x="40" y="290" width="320" height="40" rx="10" fill="#27313d"/>'
        '<ellipse cx="110" cy="250" rx="62" ry="32" fill="#fff"/><circle cx="120" cy="220" r="40" fill="#f2c9a5"/>'
        '<path d="M88 205 C 100 175 150 175 158 205 Z" fill="#5a3b2e"/>'
        '<rect x="150" y="225" width="210" height="72" rx="24" fill="#8fd3ff"/>'
        '<path d="M100 225 q8 6 16 0" fill="none" stroke="#5a3b2e" stroke-width="4" stroke-linecap="round"/>'
    )


def reloj_luna(c, fondo, texto):
    return (
        '<circle cx="190" cy="200" r="135" fill="#fff"/><circle cx="190" cy="200" r="118" fill="none" stroke="#e3e7ee" stroke-width="6"/>'
        + "".join(f'<rect x="186" y="92" width="8" height="22" rx="4" fill="#9aa7b3" transform="rotate({a} 190 200)"/>' for a in range(0, 360, 30)) +
        f'<line x1="190" y1="200" x2="190" y2="125" stroke="{INK}" stroke-width="12" stroke-linecap="round"/>'
        f'<line x1="190" y1="200" x2="245" y2="230" stroke="{c}" stroke-width="10" stroke-linecap="round"/><circle cx="190" cy="200" r="12" fill="{INK}"/>'
        + luna(320, 70, 52, fondo) +
        f'<rect x="105" y="330" width="170" height="58" rx="29" fill="#ffd23f"/><text x="190" y="370" font-size="32" font-weight="900" fill="{INK}" text-anchor="middle">{texto}</text>'
    )


def pie(x, y, rot):
    return (f'<g transform="rotate({rot} {x} {y})"><ellipse cx="{x}" cy="{y}" rx="30" ry="48" fill="#fff"/>'
            f'<ellipse cx="{x}" cy="{y + 62}" rx="22" ry="22" fill="#fff"/>'
            + "".join(f'<circle cx="{x - 24 + i * 12}" cy="{y - 58 + abs(i - 1) * 4}" r="{8 - i}" fill="#fff"/>' for i in range(5)) + "</g>")


def huellas(c, texto):
    return (pie(130, 290, -12) + pie(230, 200, 10) + pie(140, 110, -12) + pie(290, 60, 10) +
            f'<rect x="170" y="320" width="215" height="62" rx="31" fill="#ffd23f"/><text x="277" y="362" font-size="32" font-weight="900" fill="{INK}" text-anchor="middle">{texto}</text>')


def magnesio(c):
    return (
        '<rect x="90" y="70" width="220" height="220" rx="28" fill="#fff"/>'
        f'<text x="115" y="115" font-size="30" font-weight="800" fill="#6b7785">12</text>'
        f'<text x="200" y="225" font-size="110" font-weight="900" fill="{c}" text-anchor="middle">Mg</text>'
        f'<text x="200" y="270" font-size="26" font-weight="700" fill="{INK}" text-anchor="middle">Magnesio</text>'
        '<ellipse cx="70" cy="330" rx="34" ry="22" fill="#b5713c" transform="rotate(-25 70 330)"/>'
        '<ellipse cx="135" cy="355" rx="34" ry="22" fill="#9c5e2f" transform="rotate(15 135 355)"/>'
        '<path d="M240 380 C 230 320 280 290 360 300 C 350 350 300 385 240 380 Z" fill="#2e9e6a"/>'
        '<path d="M245 375 C 280 345 315 325 352 305" fill="none" stroke="#1d7a4e" stroke-width="5"/>'
        '<path d="M330 70 l18 -40 l18 40 Z" fill="#ffd23f" transform="rotate(20 348 50)"/>'
    )


def llave_celula(c):
    """Célula con cerradura y una llave (insulina) que no entra bien."""
    return (
        '<circle cx="210" cy="215" r="150" fill="#fff"/>'
        '<circle cx="210" cy="215" r="150" fill="none" stroke="#dcebfb" stroke-width="18"/>'
        '<circle cx="250" cy="170" r="16" fill="#ffd23f"/><circle cx="160" cy="290" r="12" fill="#ffd23f"/><circle cx="280" cy="290" r="10" fill="#ffd23f"/>'
        '<circle cx="210" cy="205" r="34" fill="#27313d"/><path d="M196 225 L224 225 L234 285 L186 285 Z" fill="#27313d"/>'
        f'<g transform="rotate(-28 95 330)"><circle cx="60" cy="330" r="38" fill="{c}"/><circle cx="60" cy="330" r="14" fill="#fff"/>'
        f'<rect x="92" y="320" width="120" height="20" rx="6" fill="{c}"/><rect x="170" y="340" width="14" height="24" fill="{c}"/><rect x="194" y="340" width="14" height="32" fill="{c}"/></g>'
        '<path d="M300 70 l26 26 M326 70 l-26 26" stroke="#d32f2f" stroke-width="12" stroke-linecap="round"/>'
    )


def lista_criterios(c):
    """Ficha con 5 criterios, 3 marcados, y una cinta métrica."""
    s = '<rect x="70" y="40" width="260" height="320" rx="22" fill="#fff"/>'
    for i in range(5):
        y = 82 + i * 58
        if i < 3:
            s += f'<circle cx="112" cy="{y}" r="20" fill="{c}"/><path d="M102 {y} l7 8 l14 -16" stroke="#fff" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        else:
            s += f'<circle cx="112" cy="{y}" r="18" fill="none" stroke="#c5ced8" stroke-width="5"/>'
        s += f'<rect x="146" y="{y - 9}" width="{150 - (i % 2) * 40}" height="18" rx="9" fill="#dfe6ee"/>'
    s += '<g transform="rotate(-18 300 330)"><rect x="200" y="305" width="190" height="46" rx="8" fill="#ffd23f"/>'
    for k in range(9):
        x = 214 + k * 20
        s += f'<line x1="{x}" y1="305" x2="{x}" y2="{325 if k % 2 else 333}" stroke="#27313d" stroke-width="4"/>'
    return s + '</g>'


def dibujo_svg(spec, c, fondo):
    nombre, *args = spec
    if nombre == "tensiometro":
        inner = tensiometro(c, *args)
    elif nombre == "tensiometro_ok":
        inner = tensiometro(c, ok=True)
    elif nombre in ("cama", "reloj_luna"):
        inner = globals()[nombre](c, fondo, *args)
    else:
        inner = globals()[nombre](c, *args)
    return f'<svg viewBox="0 0 400 400" width="430" height="430" font-family="Segoe UI, Arial, sans-serif">{inner}</svg>'


def pagina(p):
    nombre_tema, c, c2 = TEMAS[p["tema"]]
    t = p["titular"]
    size = 72 if len(t) <= 26 else 64 if len(t) <= 34 else 56
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1200px;height:630px;overflow:hidden}}
body{{font-family:'Segoe UI',Arial,sans-serif;background:linear-gradient(135deg,{c} 0%,{c2} 100%);color:#fff;position:relative}}
.txt{{position:absolute;left:64px;top:56px;width:600px;height:518px;display:flex;flex-direction:column}}
.chip{{align-self:flex-start;background:rgba(255,255,255,.2);border:2px solid rgba(255,255,255,.55);border-radius:40px;padding:8px 22px;font-size:24px;font-weight:700;letter-spacing:.5px;text-transform:uppercase}}
h1{{font-family:'Segoe UI Black','Segoe UI',Arial,sans-serif;font-weight:900;font-size:{size}px;line-height:1.06;margin-top:34px;text-shadow:0 3px 0 rgba(0,0,0,.12)}}
p{{font-size:30px;line-height:1.3;margin-top:22px;font-weight:600;color:rgba(255,255,255,.93)}}
.marca{{margin-top:auto;display:flex;align-items:center;gap:14px;font-size:28px;font-weight:800}}
.cta{{background:#fff;color:{c};border-radius:12px;padding:10px 20px;font-size:26px;font-weight:800}}
.ilu{{position:absolute;right:40px;top:50%;transform:translateY(-50%);width:480px;height:480px;border-radius:50%;background:rgba(255,255,255,.14);display:flex;align-items:center;justify-content:center}}
</style></head><body>
<div class="ilu">{dibujo_svg(p["dibujo"], c, "transparent")}</div>
<div class="txt"><span class="chip">{escape(nombre_tema)}</span><h1>{escape(t)}</h1><p>{escape(p["sub"])}</p>
<div class="marca"><span class="cta">Lee la guía &rarr;</span><span>cuerpobajolalupa.es</span></div></div>
</body></html>"""


def navegador():
    for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              shutil.which("google-chrome") or "", shutil.which("chromium") or "", shutil.which("chromium-browser") or ""):
        if p and Path(p).exists():
            return p
    return None


def main(solo=None):
    OUT.mkdir(parents=True, exist_ok=True)
    nav = navegador()
    if not nav:
        print("AVISO: no hay Chrome/Edge/Chromium; no se generan imágenes (la guía usará la imagen genérica).")
        return
    tmp = Path(tempfile.mkdtemp())
    for slug, p in PORTADAS.items():
        if solo and slug not in solo:
            continue
        html_ = pagina(p)
        f = tmp / f"{slug}.html"
        f.write_text(html_, encoding="utf-8")
        png = OUT / f"{slug}.png"
        subprocess.run([nav, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--user-data-dir={tmp / 'perfil'}", "--window-size=1200,630",
                        f"--screenshot={png}", f.as_uri()], check=True, capture_output=True, timeout=60)
        print("imagen", png.relative_to(ROOT))
    faltan = [g.stem for g in (ROOT / "guias").glob("*.html") if g.stem != "index" and g.stem not in PORTADAS]
    if faltan:
        print("AVISO: guías sin imagen propia en tools/portadas.py:", ", ".join(faltan))


if __name__ == "__main__":
    main(sys.argv[1:] or None)
