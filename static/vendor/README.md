# Dependencias frontend autocontenidas

| Biblioteca | Versión | Archivo | Licencia | SHA-256 |
|---|---:|---|---|---|
| Marked | 15.0.12 | `marked/marked-15.0.12.min.js` | MIT | `3e7e7d7feb3e5d58cb6c804f68ab5c24cc7e5eb6270fd6e5cbb9124739217d0c` |
| DOMPurify | 3.2.6 | `dompurify/purify-3.2.6.min.js` | Apache-2.0 / MPL-2.0 | `fc42f9bf6f37e0df85e1a20ee4045983f89c1d04914f50c1113d8c4afe3a1bcb` |
| Bootstrap | 5.3.3 | `bootstrap/bootstrap-5.3.3.min.css` | MIT | `26db49828d6701fcfce37a96da6ec3f0ed481abae49c8c9969a575b064413cad` |
| Bootstrap | 5.3.3 | `bootstrap/bootstrap.bundle-5.3.3.min.js` | MIT | `073254afbfc06331b8b548b7fc0532b4ffe2cfdd588368dcc338e7abd50810e1` |
| Bootstrap Icons | 1.11.3 | `bootstrap-icons/bootstrap-icons-1.11.3.min.css` | MIT | `f643d6fe7e679f9de3e16311600c5ef5cd6b098f7a3a8828fcc29255d2b33e62` |
| Bootstrap Icons | 1.11.3 | `bootstrap-icons/fonts/bootstrap-icons.woff2` | MIT | `476adf42b40325098fcfa8b36ab3e769186bb4f6ce6a249753e2e1a9c22bf99e` |
| Bootstrap Icons | 1.11.3 | `bootstrap-icons/fonts/bootstrap-icons.woff` | MIT | `bb1de989b83970f6f4e54de1cd974c5cba55b73582da5e1b225a6d0edf029483` |

Fuentes de los artefactos:

- `https://cdn.jsdelivr.net/npm/marked@15.0.12/marked.min.js`
- `https://cdn.jsdelivr.net/npm/dompurify@3.2.6/dist/purify.min.js`
- `https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css`
- `https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js`
- `https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css`
- `https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/fonts/bootstrap-icons.woff2`
- `https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/fonts/bootstrap-icons.woff`

Los comentarios `sourceMappingURL` se retiran de los artefactos minificados
cuando el sourcemap no forma parte del paquete versionado. Esa modificación no
afecta la ejecución y evita referencias rotas durante `collectstatic`.

Los archivos se sirven mediante `{% static %}` y no se actualizan en tiempo de
ejecución. Al cambiar una versión se deben actualizar el nombre, este registro,
las referencias del template y las pruebas de descubrimiento de estáticos.
