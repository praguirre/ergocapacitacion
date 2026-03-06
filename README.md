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

---

*ErgoSolutions © 2026*
