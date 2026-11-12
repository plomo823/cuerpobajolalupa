# Diario del agente CEO

## 2026-11-10 — Migración
- Web exportada de ChatGPT Sites y subida a GitHub (plomo823/cuerpobajolalupa), con 4 guías: presión en casa, caminar, infarto y sueño.
- Canonical cambiados a https://cuerpobajolalupa.es, añadidos CNAME y sitemap.xml.
- Pendiente: activar GitHub Pages, apuntar el DNS de OVH a GitHub Pages, datos del titular para el aviso legal y verificar las 4 guías.
- Plan para mañana: verificar las guías existentes con sus fuentes y publicar el primer artículo nuevo.

## 2026-11-11 — Colesterol
- **Comprobación de la web**: no se pudo comprobar desde el entorno del agente (el proxy bloquea cuerpobajolalupa.es y plomo823.github.io; el DNS no resolvió el dominio). Sigue pendiente confirmar que GitHub Pages está activo y que el DNS de OVH apunta a GitHub. Enlaces internos revisados con script: 0 rotos.
- **Publicado**: https://cuerpobajolalupa.es/guias/colesterol-valores-normales.html (≈1.380 palabras). Datos verificados abriendo MedlinePlus (niveles de colesterol y prueba de triglicéridos), NHLBI (diagnóstico, franjas de no-HDL) y la ficha de colesterol de la Fundación Española del Corazón. Tema elegido por RPM alto (colesterol) y búsquedas frecuentes en España y Latinoamérica.
- **Mejorado**: las 4 guías existentes no tenían enlace al canal de YouTube (obligatorio según el manual) ni guías relacionadas. Añadida sección «Sigue aprendiendo» con enlaces cruzados entre todas las guías + enlace al canal, y enlace a la nueva guía en el aside. `dateModified` actualizado.
- Portada (tarjeta nueva en #guias) y sitemap.xml actualizados.
- Lanzamiento: sigue con noindex y robots bloqueado (faltan HTTPS confirmado, datos del titular y verificación de las 4 guías iniciales).
- **Plan para mañana**: verificar fuentes de 1-2 guías iniciales (presión en casa e infarto) y quitar sus avisos de revisión si cuadran; nuevo artículo de alto RPM (p. ej. «tensión arterial: valores normales por edad» o «glucosa en ayunas: valores normales»).

## 2026-11-12 — Tensión arterial normal
- **Comprobación de la web**: sigue sin poder comprobarse desde el entorno del agente (el proxy rechaza cuerpobajolalupa.es). Además, el repositorio **no tiene ninguna ejecución de GitHub Pages** («pages-build-deployment»: 0 ejecuciones), lo que indica que GitHub Pages probablemente aún no está activado. Necesita a José: Settings → Pages → rama `main`, carpeta raíz, dominio `cuerpobajolalupa.es`, y los registros DNS en OVH. Enlaces internos revisados con script: 0 rotos.
- **Publicado**: https://cuerpobajolalupa.es/guias/tension-arterial-valores-normales.html (≈1.450 palabras). Tabla con criterios OMS/ESC 2024 (140/90; categoría «elevada» 120-139/70-89) y CDC (130/80), explicación de por qué no hay «tensión normal por edad», objetivos en hipertensos y signos de urgencia (180/120). Datos verificados abriendo: nota descriptiva de la OMS (25-09-2025), CDC en español, MedlinePlus (definición sistólica/diastólica), ficha de la Fundación Española del Corazón y resumen de las guías ESC 2024 en PubMed Central. Cifra de sal de la OMS omitida a propósito: su versión en español dice «2 gramos de sal», que parece confundir sal con sodio; no se publica hasta poder aclararla.
- **Mejorado**: guía «Medir la presión en casa» verificada frente a AHA News y la infografía de la AHA. Corregidas dos frases (muñeca vs. brazo; manguito pequeño eleva la lectura), añadido lo de la vejiga llena, dos fuentes nuevas y **quitado el aviso «requiere revisión clínica»**. Quedan por verificar: caminar, infarto y sueño.
- Enlaces cruzados a la nueva guía en las 5 guías; añadida sección «Sigue aprendiendo» a la de colesterol. Portada (tarjeta nueva) y sitemap.xml actualizados.
- Lanzamiento: sigue con noindex y robots bloqueado (faltan GitHub Pages/HTTPS, datos del titular y verificar 3 guías iniciales).
- **Plan para mañana**: verificar «Señales de un posible infarto» (OMS/MedlinePlus/FEC) y quitar su aviso; nuevo artículo de alto RPM: «glucosa en ayunas: valores normales y prediabetes».
