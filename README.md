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

---

*ErgoSolutions © 2026*
