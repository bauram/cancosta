# Can Costa — clon web (català)

Clon en codi real (HTML/CSS/JS) de [cancosta.art](https://www.cancosta.art), en català, 13 pàgines.

## Contingut

- `index.html`, `la-casa.html`, `miquel-costa-i-llobera.html`, `el-projecte.html`, `la-sala-gran.html`, `contacte-cat.html`, `festival-de-musica.html`, `privacy-policy.html`, `legal-advise.html`, `fons-museografic-casa-natal-de-miquel-costa-i-llobera-a-pollenca-copy.html`, `el-pi-de-formentor.html`, `la-deixa-del-geni-grec.html`, `a-virgili.html`
- `css/styles.css` — CSS real compilat de Webflow (sencer, sense reescriure)
- `js/` — els 3 chunks de `webflow.js` reals del lloc (interaccions de navbar/menú)

## Dependències externes (no incloses, es carreguen des del seu origen real)

- jQuery 3.5.1 vía CDN de Webflow/Cloudfront
- Google Fonts (Open Sans) vía `fonts.googleapis.com`
- Typekit/Adobe Fonts vía `use.typekit.net`
- Totes les imatges enllaçades a `cdn.prod.website-files.com` (el mateix CDN que serveix el lloc real — mateixos bytes, no mirroritzades localment)

## Desplegament

Puja tota la carpeta `proyecto/` (aquest directori) tal qual al teu servidor/hosting. Cap ruta és absoluta cap a un domini local: els enllaços interns entre pàgines són relatius (`la-casa.html`, etc.), així que funcionarà des de qualsevol subcarpeta o domini.

Els enllaços cap a `/eng/*` i `/es/home-copy` (no clonats, fora de l'abast) apunten al lloc real `https://www.cancosta.art/...`.

## Limitacions conegudes

- El formulari de contacte (`contacte-cat.html`) i el de sol·licitud del fons museogràfic reprodueixen l'estructura HTML real de Webflow, però no tenen backend — Webflow gestiona l'enviament dels formularis amb el seu propi servei intern, que no forma part d'aquest clon de codi estàtic. Caldria connectar-los a un servei propi (Formspree, backend propi, etc.) si es vol que funcionin.
- Clonat en versió desktop (1920px). No s'ha verificat ni maquetat el responsive per mòbil/tablet.
- Les animacions natives de Webflow (menú mòbil, dropdown d'idioma) haurien de funcionar gràcies als 3 fitxers `js/webflow.*.js` reals inclosos, ja que utilitzen selectors per classe CSS (no per `data-w-id`, que no es va poder extreure per una restricció de seguretat de l'entorn on es va generar aquest clon — vegeu `CLAUDE.md` al directori pare per detalls).
