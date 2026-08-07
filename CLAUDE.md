# Can Costa — web (clon estático de cancosta.art en català)

## Ubicación local
Esta carpeta (`cancosta-repo/`) es la raíz del repo — el único sitio donde se trabaja.

## Repositorio
- https://github.com/bauram/cancosta.git
- rama: `master`
- el push a `master` dispara auto-deploy en Netlify

## URL en producción
https://cancostaweb.netlify.app/

Netlify está conectado directamente a este repo de GitHub — cualquier commit + push a `master` se despliega solo, sin pasos manuales en Netlify.

## Estructura
- 13 páginas HTML en la raíz: `index.html`, `la-casa.html`, `el-projecte.html`, `la-sala-gran.html`, `miquel-costa-i-llobera.html`, `contacte-cat.html`, `festival-de-musica.html`, `privacy-policy.html`, `legal-advise.html`, `fons-museografic-casa-natal-de-miquel-costa-i-llobera-a-pollenca-copy.html`, `el-pi-de-formentor.html`, `la-deixa-del-geni-grec.html`, `a-virgili.html`
- `css/styles.css` → un solo archivo CSS compartido por las 13 páginas (compilado de Webflow, sin reescribir). Cualquier cambio de estilo (tamaños, colores, espaciados) se hace aquí y afecta a todo el sitio.
- `js/` → 3 chunks de `webflow.js` reales (interacciones navbar/menú)
- `images/` → imágenes migradas a local (ya no dependen del CDN de Webflow)

## Notas importantes
- Es un clon estático, sin build step ni framework (no hay npm/webpack). Los cambios en HTML/CSS se ven directo, no hace falta compilar nada.
- Los formularios de contacto no tienen backend real (estructura Webflow, sin conexión a un servicio de envío).
- Clonado en versión desktop (1920px); el responsive mobile/tablet no está verificado.
- El logo del navbar usa la clase `.rl_navbar1_logo` en `css/styles.css`.

## Flujo de trabajo
1. Editar HTML/CSS/JS directamente en esta carpeta.
2. `git add` + `git commit`
3. `git push origin master`
4. Netlify redespliega solo en 1-2 minutos.

## Otras carpetas del directorio padre (no usar)
En `Clon-html/cancosta-art/` existen copias antiguas/duplicadas (`proyecto/`, `proyecto/cancosta-art-netlify/`, `proyecto/cancosta-art-netlify 2/`) de un despliegue anterior. No están conectadas al deploy real y no se deben editar — todo el trabajo va en `cancosta-repo/`.
