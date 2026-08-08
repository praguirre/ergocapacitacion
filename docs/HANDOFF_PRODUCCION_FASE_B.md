# Handoff de producción — Fase B del Chat IA

**Iniciativa:** Chat IA — contexto de pantalla y acceso de lectura  
**Roadmap:** `docs/ROADMAP_CHAT_IA_CONTEXTO_Y_DATOS.md`  
**Rama documental:** `codex/docs-chat-ia-handoff-produccion`  
**Responsable del puente:** Pablo R. Aguirre  
**Estado:** B.0 cerrado en desarrollo; B.1 detenido antes de modificar
`MIDDLEWARE`.

---

## Decisión de Arquitectura DA-B-HANDOFF-1

La coordinación con producción se hace mediante una rama exclusivamente
documental y Pablo actúa como puente entre asistentes. El asistente de
producción ejecuta sólo diagnósticos explícitos y devuelve salida literal. No
modifica archivos, servicios, variables de entorno ni datos mientras el pedido
esté marcado como diagnóstico.

Esta separación evita que leer instrucciones operativas implique desplegar el
código local de B.0 o cambiar la rama activa del servidor.

## Cómo leer esta documentación sin desplegarla

Desde el clon de producción:

```bash
cd /srv/ergocapacitacion/app
git fetch origin codex/docs-chat-ia-handoff-produccion
git show origin/codex/docs-chat-ia-handoff-produccion:docs/HANDOFF_PRODUCCION_FASE_B.md
```

`git fetch` actualiza referencias remotas, pero no cambia el commit desplegado
ni el árbol de trabajo. Para este handoff están prohibidos `git pull`,
`git checkout`, `git switch`, `git reset` y cualquier despliegue.

---

## Pedido vigente — B.1 / P-4

### Objetivo

Confirmar que nginx sirve `/static/` directamente desde `STATIC_ROOT` antes de
retirar WhiteNoise del `MIDDLEWARE` de producción. Si nginx no lo sirve, sacar
WhiteNoise dejaría el sitio sin CSS ni JavaScript.

### Alcance autorizado

Sólo lectura y diagnóstico. No ejecutar `sudo systemctl restart/reload`, no
editar nginx, no tocar `.env`, no ejecutar `collectstatic` y no cambiar Git.

### Comandos exactos

Ejecutar en producción, en este orden:

```bash
date -Is
hostname

readlink -f /etc/nginx/sites-enabled/ergocapacitacion

grep -n -A8 -B2 "location /static/" \
  /etc/nginx/sites-enabled/ergocapacitacion

sudo nginx -T 2>/dev/null \
  | grep -n -A8 -B2 "location /static/"

sudo test -f \
  /srv/ergocapacitacion/static/ayuda/css/help_widget.css
echo "archivo_static_exit=$?"

sudo stat -c '%A %U:%G %s %n' \
  /srv/ergocapacitacion/static/ayuda/css/help_widget.css

curl -sS -D - -o /dev/null \
  https://www.ergosolutions.com.ar/static/ayuda/css/help_widget.css \
  | sed -n '1,15p'

curl -sS -o /dev/null \
  -w 'http_code=%{http_code} content_type=%{content_type} size=%{size_download}\n' \
  https://www.ergosolutions.com.ar/static/ayuda/css/help_widget.css
```

### Criterio para habilitar B.1

La respuesta es **APTO** únicamente si toda esta evidencia coincide:

1. La configuración efectiva de `nginx -T` contiene `location /static/`.
2. Ese bloque usa `alias /srv/ergocapacitacion/static/;` o una ruta equivalente
   que contiene el archivo comprobado.
3. El archivo existe y `stat` puede leerlo.
4. La URL pública responde HTTP 200 y un tipo de contenido CSS.

Si algo difiere, responder **NO APTO** sin corregirlo. Desarrollo actualizará
el roadmap antes de autorizar cualquier cambio de producción.

### Formato obligatorio de respuesta

Copiar la salida literal, sin resumir ni ocultar errores no sensibles:

```text
RESPUESTA PRODUCCIÓN — B.1 / P-4

Resultado: APTO | NO APTO

$ date -Is
<salida literal>

$ hostname
<salida literal>

$ readlink -f /etc/nginx/sites-enabled/ergocapacitacion
<salida literal>

$ grep -n -A8 -B2 "location /static/" /etc/nginx/sites-enabled/ergocapacitacion
<salida literal, incluido código de salida si no encontró coincidencias>

$ sudo nginx -T 2>/dev/null | grep -n -A8 -B2 "location /static/"
<salida literal>

$ sudo test -f ... ; echo "archivo_static_exit=$?"
<salida literal>

$ sudo stat -c ...
<salida literal>

$ curl -sS -D - -o /dev/null ... | sed -n '1,15p'
<salida literal>

$ curl -sS -o /dev/null -w ...
<salida literal>

Conclusión técnica:
<una frase: nginx sirve /static/ directamente, o la discrepancia exacta>

Cambios realizados en producción: NINGUNO
```

## Reglas permanentes para próximos pedidos de Fase B

- No incluir secretos, contraseñas, cookies, tokens ni contenido del `.env`.
- No ejecutar tests Django en producción.
- No realizar acciones destructivas ni irreversibles.
- No reiniciar ni recargar servicios sin una autorización P-4 nueva y
  explícita.
- Registrar identificadores y métricas; nunca payloads del Chat IA.
- Ante una discrepancia, informar y detenerse: no improvisar una corrección.

