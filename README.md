# ErgoSolutions

**Plataforma integral para profesionales de Seguridad e Higiene, Salud Ocupacional y Ergonomía.**

## Descripción

ErgoSolutions permite a profesionales gestionar capacitaciones laborales en dos modalidades:

- **Presencial**: Video + Chat IA + Quiz grupal + Planilla PDF de asistencia
- **Online**: Links compartibles + Registro individual + Quiz con reglas + Certificado PDF automático

## Tecnologías

- **Backend**: Django 5.2+ / PostgreSQL
- **Frontend**: Bootstrap 5 / Bootstrap Icons
- **IA**: OpenAI GPT (Ergobot AI) con streaming SSE
- **PDF**: ReportLab
- **Async**: ASGI + Uvicorn

## Instalación

```bash
# 1. Clonar
git clone https://github.com/praguirre/ergocapacitacion.git
cd ergocapacitacion

# 2. Entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Dependencias
pip install -r requirements.txt

# 4. Variables de entorno
cp .env.example .env
# Editar .env con datos de DB y API keys

# 5. Base de datos
python manage.py migrate

# 6. Datos iniciales
python manage.py seed_quiz         # Preguntas del quiz
python manage.py seed_modules      # Módulos de capacitación

# 7. Superusuario
python manage.py createsuperuser

# 8. Iniciar
python manage.py runserver
```

## Estructura de URLs

| URL | Descripción |
|-----|-------------|
| `/` | Landing institucional |
| `/auth/` | Login/Registro profesionales |
| `/dashboard/` | Panel de profesionales |
| `/dashboard/presencial/` | Modo presencial |
| `/dashboard/capacitaciones/` | Menú de capacitaciones |
| `/acceso/` | Login/Registro trabajadores |
| `/capacitacion/` | Capacitación online (trainees) |
| `/c/<slug>/` | Acceso vía link compartido |
| `/quiz/` | Sistema de evaluaciones |
| `/ai/` | Chatbot Ergobot (SSE) |
| `/admin/` | Panel de administración |

## Documentación

La documentación técnica y operativa está centralizada en
[docs/README.md](docs/README.md). Allí se encuentran los roadmaps, planes de
implementación, runbook de despliegue, mapa conceptual e inventario del
proyecto.

El documento de referencia vigente es el
[**Estado técnico consolidado del 01/08/2026**](docs/ESTADO_TECNICO_CONSOLIDADO_2026-08-01.md):
consolida la auditoría de producción con el estado real del código en
`release/beta`, verifica hallazgo por hallazgo qué sigue vigente y qué cambió, y
define el plan de trabajo priorizado para retomar el desarrollo.

La [auditoría técnica de producción del 30/07/2026](docs/INFORME_TECNICO_AUDITORIA_PRODUCCION_2026-07-30.md)
se conserva íntegra como fotografía histórica del despliegue auditado.

### Integración del módulo de Ergonomía SRT 886/15

- **02/08/2026 — Commit 0.0:** se abrió la rama
  `feature/ergonomia-886` y se creó
  `docs/BITACORA_INTEGRACION_886.md`. El estado de partida quedó verificado con
  160 pruebas del módulo y 32 de ErgoSolutions en `OK`, sin cambios de modelos
  pendientes de migración.
- **02/08/2026 — Commit 0.1:** se consolidó el árbol documental pendiente:
  cuatro documentos de la raíz quedaron verificados bajo `docs/`, se incorporó
  el resto de la documentación técnica preparada y se actualizó `.gitignore`.
  `manage.py check` no reportó issues y el smoke test de `GET /` respondió 200.
- **02/08/2026 — Commit 0.2:** se corrigieron cinco nombres de URL inexistentes
  en los decoradores de cuentas. Los accesos anónimos de profesionales,
  empresas y trabajadores ahora resuelven al login correspondiente, cerrando
  la causa raíz de la regresión N1.
- **02/08/2026 — Commit 0.3:** se restauró `@login_required` como capa exterior
  en once vistas de empresa y dos profesionales. Las ocho rutas anónimas
  verificadas redirigen con HTTP 302 y ninguna devuelve 500.
- **02/08/2026 — Commit 0.4:** se calificaron los settings profesionales de
  login y redirección con sus namespaces reales. Los cuatro settings de
  autenticación resuelven correctamente y el login profesional responde 200.

### Registro de cambios documentales

- **30/07/2026:** se creó `docs/`, se incorporó el informe técnico de auditoría
  de producción y se centralizaron los documentos Markdown de arquitectura,
  planificación, operación e inventario que estaban en la raíz. `README.md` y
  `AGENTS.md` permanecen en la raíz por su función operativa.
- **01/08/2026:** se incorporó el **Estado técnico consolidado**, que contrasta
  la auditoría de producción (`v0.1.3-beta`) con el código de desarrollo
  (`v0.1.7-beta`). Resultado del contraste: los 27 hallazgos de la auditoría
  siguen vigentes (4 agravados) y se documentaron 13 hallazgos nuevos de la
  Etapa 3, dos de ellos bloqueantes para el despliegue. El documento pasa a ser
  la referencia de estado del proyecto.

## Tests

```bash
python manage.py test apps.accounts apps.dashboard apps.presencial
```

## Autor

**Lic. Pablo Aguirre** — MN 10.027  
Kinesiólogo y Especialista en Ergonomía

## Roadmap técnico (beta)

- Etapa 3A — Commit 29 completado: soporte base de `user_type='company'` en `CustomUser`.
- Etapa 3A — Commit 30 completado: nueva app `apps.company` y modelo `CompanyProfile`.
- Etapa 3A — Commit 31 completado: decoradores y mixins backoffice multi-tipo (`professional` + `company`).
- Etapa 3A — Commit 32 completado: registro y login de empresa (`/empresa/auth/`) con namespace `accounts_company` para mantener coherencia de URLs.
- Etapa 3A — Commit 33 completado: dashboard refactorizado para backoffice multi-tipo con navbar condicional y context processor de empresa.
- Etapa 3A — Commit 34 completado: perfil de empresa (edición/vista) y despacho por tipo en `dashboard:profile`.
- Etapa 3B — Commit 35 completado: modelo `CompanyWorker` (relación formal empresa↔trabajador).
- Etapa 3B — Commit 36 completado: vista de nómina con búsqueda y filtros (`/dashboard/empresa/nomina/`).
- Etapa 3B — Commit 37 completado: alta manual de trabajadores en nómina (`/dashboard/empresa/nomina/agregar/`).
- Etapa 3B — Commit 38 completado: ficha individual del trabajador (`/dashboard/empresa/nomina/<id>/`).
- Etapa 3B — Commit 39 completado: edición de datos laborales (`/dashboard/empresa/nomina/<id>/editar/`).
- Etapa 3B — Commit 40 completado: exportación de nómina a CSV (`/dashboard/empresa/nomina/exportar/`).
- Etapa 3C — Commit 41 completado: incorporación de `AgendaEvent` para agenda y vencimientos de empresas.
- Etapa 3C — Commit 42 completado: vista de Agenda con filtros y métricas básicas (`/dashboard/empresa/agenda/`).
- Etapa 3C — Commit 43 completado: CRUD básico de eventos de agenda (alta, edición y marcado como completado).
- Etapa 3C — Commit 44 completado: management command `generate_cert_expiry_events` para auto-generar eventos por vencimientos próximos (`--days`, `--dry-run`).
- Etapa 3C — Commit 45 completado: home refactorizada por tipo y panel de vencimientos/agenda para empresa.
- Etapa 3D — Commit 46 completado: directorio básico de profesionales con flag de visibilidad y filtros.
- Etapa 3D — Commit 47 completado: solicitudes de contacto empresa-profesional (envío, listado y respuesta).
- Etapa 3D — Commit 48 completado: testing integral de Etapa 3 y validación de no-regresión de flujos company/professional/trainee.

---

*ErgoSolutions © 2026*
