# 📋 ERGOSOLUTIONS - PLAN MAESTRO DE COMMITS (FASES 3–6)

## Documento de Referencia para Implementación

**Proyecto:** ErgoSolutions  
**Estado actual:** Commit 14 completado (Fases 1 y 2 listas)  
**Commits planificados:** 15 – 28  
**Fecha de creación:** Febrero 2026

---

## 🔑 ÍNDICE DE FASES Y COMMITS

| Fase | Commits | Descripción | Estado |
|------|---------|-------------|--------|
| **FASE 3** | 15-17 | Dashboard y Menú Capacitaciones | ⬜ Pendiente |
| **FASE 4** | 18-21 | Modo Presencial | ⬜ Pendiente |
| **FASE 5** | 22-25 | Modo Online (Sistema de Links) | ⬜ Pendiente |
| **FASE 6** | 26-28 | Mejoras, Testing y Pulido | ⬜ Pendiente |

---

## 📌 ESTADO ACTUAL DEL PROYECTO (Post Commit 14)

### Estructura de URLs activa

| Prefijo | App/Namespace | Descripción |
|---------|---------------|-------------|
| `/` | `landing:home` | Landing institucional pública |
| `/acceso/` | `accounts` (trainees) | Registro/Login de trabajadores |
| `/auth/` | `accounts_professional` | Registro/Login de profesionales |
| `/dashboard/` | `dashboard` | Panel de profesionales (placeholder) |
| `/capacitacion/` | `training` | Página de capacitación (trainees) |
| `/quiz/` | `quiz` | Sistema de evaluaciones |
| `/certificados/` | `certificates` | Descarga de certificados |
| `/ai/` | `ergobot_ai` | Chatbot IA (SSE) |

### Modelo TrainingModule actual

```
slug, title, youtube_id, intro_md, material_md, transcript_md, is_active, created_at, updated_at
```

### Templates base existentes

- `base.html` → Layout trainees (dark theme)
- `base_landing.html` → Layout marketing/público

---

# ═══════════════════════════════════════════════════════════════════════════
# FASE 3: DASHBOARD Y MENÚ CAPACITACIONES
# ═══════════════════════════════════════════════════════════════════════════

## COMMIT 15: Dashboard con selector Evaluaciones/Capacitaciones

### 📋 Descripción
Crear el dashboard principal del profesional con un template base propio (`base_dashboard.html`), navbar profesional, y dos cards de selección: Evaluaciones (desactivado) y Capacitaciones (activo).

### 🎯 Objetivos
- [x] Template base para el área de profesionales (base_dashboard.html)
- [x] Navbar profesional con links a Dashboard, Perfil, Logout
- [x] Dashboard con cards de Evaluaciones (badge "Próximamente") y Capacitaciones (activo)
- [x] Vista completa del dashboard con información del usuario

### 📁 Archivos a crear/modificar

---

#### 1. `templates/base_dashboard.html` (CREAR)

```html
{% load static %}
<!DOCTYPE html>
<html lang="es" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Dashboard - ErgoSolutions{% endblock %}</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{% static 'css/dashboard.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body class="bg-black text-light min-vh-100 d-flex flex-column">

    <!-- ============================== NAVBAR ============================== -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark border-bottom border-secondary">
        <div class="container-fluid">
            <a class="navbar-brand fw-bold" href="{% url 'dashboard:home' %}">
                <i class="bi bi-shield-check text-primary me-2"></i>ErgoSolutions
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#dashboardNav">
                <span class="navbar-toggler-icon"></span>
            </button>

            <div class="collapse navbar-collapse" id="dashboardNav">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li class="nav-item">
                        <a class="nav-link {% if request.resolver_match.url_name == 'home' %}active{% endif %}" 
                           href="{% url 'dashboard:home' %}">
                            <i class="bi bi-grid-1x2 me-1"></i>Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.resolver_match.url_name == 'capacitaciones_menu' %}active{% endif %}" 
                           href="{% url 'dashboard:capacitaciones_menu' %}">
                            <i class="bi bi-mortarboard me-1"></i>Capacitaciones
                        </a>
                    </li>
                </ul>
                
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" role="button" 
                           data-bs-toggle="dropdown" aria-expanded="false">
                            <i class="bi bi-person-circle me-1"></i>
                            {{ request.user.display_name }}
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end dropdown-menu-dark">
                            <li>
                                <a class="dropdown-item" href="{% url 'dashboard:profile' %}">
                                    <i class="bi bi-person me-2"></i>Mi Perfil
                                </a>
                            </li>
                            <li><hr class="dropdown-divider"></li>
                            <li>
                                <form method="post" action="{% url 'professional_logout' %}">
                                    {% csrf_token %}
                                    <button type="submit" class="dropdown-item text-danger">
                                        <i class="bi bi-box-arrow-right me-2"></i>Cerrar sesión
                                    </button>
                                </form>
                            </li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- ========================= CONTENIDO PRINCIPAL ========================= -->
    {% include "includes/messages.html" %}
    
    <main class="flex-grow-1">
        {% block content %}{% endblock %}
    </main>

    <!-- ============================== FOOTER ============================== -->
    <footer class="bg-dark border-top border-secondary py-3 mt-auto">
        <div class="container-fluid">
            <p class="text-secondary text-center mb-0 small">
                ErgoSolutions &copy; 2026 — Desarrollado por 
                <strong class="text-white">Lic. Pablo Aguirre</strong> - MN 10.027
            </p>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

---

#### 2. `static/css/dashboard.css` (CREAR)

```css
/* static/css/dashboard.css */
/* ============================================================================
   COMMIT 15: Estilos para el área de profesionales
   ============================================================================ */

/* Cards del dashboard */
.dashboard-card {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border-radius: 12px;
    overflow: hidden;
}

.dashboard-card:hover:not(.disabled-card) {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.dashboard-card .card-icon {
    font-size: 3.5rem;
    margin-bottom: 1rem;
}

.dashboard-card.disabled-card {
    opacity: 0.6;
    cursor: not-allowed;
}

.dashboard-card.disabled-card .card-body {
    pointer-events: none;
}

/* Cards de capacitaciones */
.training-card {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border-radius: 12px;
    cursor: pointer;
}

.training-card:hover:not(.disabled-card) {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.training-card .card-icon {
    width: 64px;
    height: 64px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
    margin-bottom: 1rem;
}

/* Selector de modalidad */
.modality-card {
    transition: all 0.3s ease;
    border-radius: 12px;
    cursor: pointer;
    border: 2px solid transparent;
}

.modality-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.modality-card.presencial:hover {
    border-color: #ffc107;
}

.modality-card.online:hover {
    border-color: #0d6efd;
}

/* Stats cards */
.stat-card {
    border-radius: 10px;
    padding: 1.25rem;
}

.stat-card .stat-number {
    font-size: 2rem;
    font-weight: 700;
}

/* Breadcrumb custom */
.breadcrumb-dark {
    background: transparent;
    padding: 0;
}

.breadcrumb-dark .breadcrumb-item a {
    color: #6c757d;
    text-decoration: none;
}

.breadcrumb-dark .breadcrumb-item a:hover {
    color: #adb5bd;
}

.breadcrumb-dark .breadcrumb-item.active {
    color: #f8f9fa;
}

.breadcrumb-dark .breadcrumb-item + .breadcrumb-item::before {
    color: #6c757d;
}
```

---

#### 3. `templates/dashboard/home.html` (REEMPLAZAR COMPLETO)

```html
{% extends "base_dashboard.html" %}

{% block title %}Dashboard - ErgoSolutions{% endblock %}

{% block content %}
<div class="container-fluid py-4 px-4">
    
    <!-- Encabezado -->
    <div class="row mb-4">
        <div class="col">
            <h2 class="fw-bold mb-1">
                <i class="bi bi-grid-1x2 me-2 text-primary"></i>Dashboard
            </h2>
            <p class="text-secondary mb-0">
                Bienvenido, <strong class="text-light">{{ request.user.display_name }}</strong>
                {% if request.user.profession %}
                    — {{ request.user.profession }}
                    {% if request.user.license_number %}
                        ({{ request.user.license_number }})
                    {% endif %}
                {% endif %}
            </p>
        </div>
    </div>

    <!-- Stats rápidas -->
    <div class="row g-3 mb-5">
        <div class="col-md-4">
            <div class="stat-card bg-dark border border-secondary">
                <div class="d-flex align-items-center">
                    <div class="me-3">
                        <i class="bi bi-mortarboard text-success" style="font-size: 2rem;"></i>
                    </div>
                    <div>
                        <div class="stat-number text-success">{{ stats.capacitaciones_total|default:"0" }}</div>
                        <small class="text-secondary">Sesiones realizadas</small>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="stat-card bg-dark border border-secondary">
                <div class="d-flex align-items-center">
                    <div class="me-3">
                        <i class="bi bi-link-45deg text-info" style="font-size: 2rem;"></i>
                    </div>
                    <div>
                        <div class="stat-number text-info">{{ stats.links_generados|default:"0" }}</div>
                        <small class="text-secondary">Links generados</small>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="stat-card bg-dark border border-secondary">
                <div class="d-flex align-items-center">
                    <div class="me-3">
                        <i class="bi bi-people text-warning" style="font-size: 2rem;"></i>
                    </div>
                    <div>
                        <div class="stat-number text-warning">{{ stats.trabajadores_capacitados|default:"0" }}</div>
                        <small class="text-secondary">Trabajadores capacitados</small>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Selector principal -->
    <div class="row mb-4">
        <div class="col">
            <h4 class="text-secondary mb-3">
                <i class="bi bi-collection me-2"></i>Herramientas
            </h4>
        </div>
    </div>

    <div class="row g-4 justify-content-center">
        <!-- Card EVALUACIONES (desactivado) -->
        <div class="col-md-6 col-lg-5">
            <div class="card dashboard-card disabled-card bg-dark border-secondary h-100">
                <div class="card-body text-center py-5 px-4">
                    <div class="card-icon text-secondary">
                        <i class="bi bi-clipboard-check"></i>
                    </div>
                    <h3 class="card-title text-secondary">Evaluaciones</h3>
                    <p class="card-text text-muted mb-4">
                        Evaluaciones de riesgos ergonómicos, iluminación, ruido y más. 
                        Todo según normativa vigente.
                    </p>
                    <span class="badge bg-warning text-dark fs-6 px-3 py-2">
                        <i class="bi bi-clock me-1"></i>Próximamente
                    </span>
                </div>
            </div>
        </div>

        <!-- Card CAPACITACIONES (activo) -->
        <div class="col-md-6 col-lg-5">
            <a href="{% url 'dashboard:capacitaciones_menu' %}" class="text-decoration-none">
                <div class="card dashboard-card bg-dark border-success h-100">
                    <div class="card-body text-center py-5 px-4">
                        <div class="card-icon text-success">
                            <i class="bi bi-mortarboard"></i>
                        </div>
                        <h3 class="card-title text-white">Capacitaciones</h3>
                        <p class="card-text text-secondary mb-4">
                            Capacitaciones online y presenciales con certificación automática. 
                            Gestioná la formación de tus trabajadores.
                        </p>
                        <span class="badge bg-success fs-6 px-3 py-2">
                            <i class="bi bi-check-circle me-1"></i>Disponible
                        </span>
                    </div>
                </div>
            </a>
        </div>
    </div>

</div>
{% endblock %}
```

---

#### 4. `apps/dashboard/views.py` (REEMPLAZAR COMPLETO)

```python
# apps/dashboard/views.py
# ============================================================================
# COMMIT 15: Dashboard principal de profesionales
# ============================================================================

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.accounts.decorators import professional_required


@login_required
@professional_required
def home(request):
    """
    Dashboard principal del profesional.
    Muestra selector de Evaluaciones / Capacitaciones y stats básicas.
    """
    # Stats placeholder — se completan en commits posteriores
    stats = {
        'capacitaciones_total': 0,
        'links_generados': 0,
        'trabajadores_capacitados': 0,
    }
    
    return render(request, 'dashboard/home.html', {
        'stats': stats,
    })


@login_required
@professional_required
def profile(request):
    """Perfil del profesional (placeholder — se completa en Commit 26)."""
    return render(request, 'dashboard/profile.html')
```

---

#### 5. `apps/dashboard/urls.py` (REEMPLAZAR COMPLETO)

```python
# apps/dashboard/urls.py
# ============================================================================
# COMMIT 15: URLs del dashboard de profesionales
# ============================================================================

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('perfil/', views.profile, name='profile'),
]
```

> **NOTA:** La URL `capacitaciones_menu` se agrega en el Commit 16. Mientras tanto, el link en el template del dashboard producirá un error si se accede antes de implementar el Commit 16. Esto se resuelve secuencialmente.

---

### ✅ Verificación del Commit 15
- [ ] `base_dashboard.html` renderiza correctamente con navbar y footer
- [ ] Dashboard muestra cards de Evaluaciones (desactivado) y Capacitaciones (activo)
- [ ] Evaluaciones tiene badge "Próximamente" y cursor not-allowed
- [ ] Capacitaciones es clickeable y lleva a `dashboard:capacitaciones_menu`
- [ ] Navbar muestra nombre del usuario logueado con dropdown
- [ ] Solo profesionales pueden acceder (decorador `@professional_required`)

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 15: Dashboard principal con selector Evaluaciones/Capacitaciones

- Template base para área de profesionales (base_dashboard.html)
- Estilos dashboard.css para cards, stats y breadcrumbs
- Dashboard con cards de Evaluaciones y Capacitaciones
- Evaluaciones desactivado con badge 'Próximamente'
- Capacitaciones activo con link al menú
- Navbar profesional con dropdown (perfil, logout)
- Stats placeholder (sesiones, links, trabajadores)
- Información del usuario logueado (nombre, profesión, matrícula)"
```

---

## COMMIT 16: Menú de capacitaciones con íconos

### 📋 Descripción
Agregar campos `icon`, `color`, `order` al modelo `TrainingModule` y crear el menú visual de capacitaciones disponibles con grid de cards.

### 🎯 Objetivos
- [x] Agregar campos `icon`, `color`, `order` a `TrainingModule`
- [x] Crear migración de base de datos
- [x] Vista de menú de capacitaciones
- [x] Grid responsive con cards e íconos de Bootstrap Icons
- [x] Indicador de activo / próximamente
- [x] Click lleva al selector de modalidad

### 📁 Archivos a crear/modificar

---

#### 1. `apps/training/models.py` (REEMPLAZAR COMPLETO)

```python
# apps/training/models.py
# ============================================================================
# COMMIT 16: Agregados campos icon, color, order para menú visual
# ============================================================================

from django.db import models


class TrainingModule(models.Model):
    slug = models.SlugField(unique=True, help_text="Identificador único para la URL.")
    title = models.CharField(max_length=200, verbose_name="Título del módulo")
    description = models.TextField(
        blank=True, default="",
        verbose_name="Descripción corta",
        help_text="Descripción breve para mostrar en el menú de capacitaciones."
    )
    youtube_id = models.CharField(
        max_length=32,
        help_text="Solo el ID del video (ej: IIgZp_NbsAE), no la URL completa."
    )

    # Contenido en formato Markdown para la IA y el Front
    intro_md = models.TextField(blank=True, default="", verbose_name="Introducción (Markdown)")
    material_md = models.TextField(blank=True, default="", verbose_name="Material de lectura")
    transcript_md = models.TextField(blank=True, default="", verbose_name="Transcripción del video")

    # =========================================================================
    # COMMIT 16: Campos para menú visual
    # =========================================================================
    icon = models.CharField(
        max_length=50,
        default='bi-book',
        help_text='Clase de Bootstrap Icons (ej: bi-body-text, bi-lightning-charge)'
    )
    color = models.CharField(
        max_length=20,
        default='#28a745',
        help_text='Color hex para el card (ej: #28a745)'
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Orden de aparición en el menú (menor = primero)'
    )

    is_active = models.BooleanField(default=False, verbose_name="¿Está activo?")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Módulo de capacitación"
        verbose_name_plural = "Módulos de capacitación"

    def __str__(self) -> str:
        return f"{self.title} ({self.slug})"
```

---

#### 2. `apps/training/admin.py` (REEMPLAZAR COMPLETO)

```python
# apps/training/admin.py
# ============================================================================
# COMMIT 16: Admin actualizado con campos de menú visual
# ============================================================================

from django.contrib import admin
from .models import TrainingModule


@admin.register(TrainingModule)
class TrainingModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "icon", "order", "is_active", "updated_at")
    list_filter = ("is_active",)
    list_editable = ("order", "is_active")
    search_fields = ("title", "slug", "youtube_id")
    prepopulated_fields = {"slug": ("title",)}
    
    fieldsets = (
        ("Información básica", {
            "fields": ("title", "slug", "description", "youtube_id", "is_active")
        }),
        ("Apariencia en menú", {
            "fields": ("icon", "color", "order"),
            "description": "Configuración visual para el menú de capacitaciones"
        }),
        ("Contenido", {
            "fields": ("intro_md", "material_md", "transcript_md"),
            "classes": ("collapse",),
        }),
    )
```

---

#### 3. Crear migración

```bash
python manage.py makemigrations training --name add_icon_color_order_description
python manage.py migrate
```

> **IMPORTANTE:** Después de migrar, actualizar el módulo de Ergonomía existente en la DB:
> ```bash
> python manage.py shell -c "
> from apps.training.models import TrainingModule
> m = TrainingModule.objects.filter(slug='ergonomia').first()
> if m:
>     m.icon = 'bi-body-text'
>     m.color = '#28a745'
>     m.order = 1
>     m.description = 'Capacitación sobre factores de riesgo ergonómicos en puestos de trabajo. Incluye video, asistente IA y evaluación con certificación.'
>     m.save()
>     print('Módulo actualizado')
> else:
>     print('Módulo no encontrado')
> "
> ```

---

#### 4. `apps/dashboard/views.py` (AGREGAR vista de menú)

```python
# apps/dashboard/views.py
# ============================================================================
# COMMIT 15-16: Dashboard y Menú de Capacitaciones
# ============================================================================

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from apps.accounts.decorators import professional_required
from apps.training.models import TrainingModule


@login_required
@professional_required
def home(request):
    """
    Dashboard principal del profesional.
    Muestra selector de Evaluaciones / Capacitaciones y stats básicas.
    """
    stats = {
        'capacitaciones_total': 0,
        'links_generados': 0,
        'trabajadores_capacitados': 0,
    }
    
    return render(request, 'dashboard/home.html', {
        'stats': stats,
    })


@login_required
@professional_required
def capacitaciones_menu(request):
    """
    Menú de capacitaciones disponibles.
    Muestra grid de cards con íconos y estados.
    """
    modules = TrainingModule.objects.all()
    
    return render(request, 'dashboard/capacitaciones_menu.html', {
        'modules': modules,
    })


@login_required
@professional_required
def profile(request):
    """Perfil del profesional (placeholder — se completa en Commit 26)."""
    return render(request, 'dashboard/profile.html')
```

---

#### 5. `apps/dashboard/urls.py` (REEMPLAZAR COMPLETO)

```python
# apps/dashboard/urls.py
# ============================================================================
# COMMIT 15-16: URLs del dashboard de profesionales
# ============================================================================

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('capacitaciones/', views.capacitaciones_menu, name='capacitaciones_menu'),
    path('perfil/', views.profile, name='profile'),
]
```

---

#### 6. `templates/dashboard/capacitaciones_menu.html` (CREAR)

```html
{% extends "base_dashboard.html" %}

{% block title %}Capacitaciones - ErgoSolutions{% endblock %}

{% block content %}
<div class="container-fluid py-4 px-4">
    
    <!-- Breadcrumb -->
    <nav aria-label="breadcrumb" class="mb-3">
        <ol class="breadcrumb breadcrumb-dark">
            <li class="breadcrumb-item"><a href="{% url 'dashboard:home' %}">Dashboard</a></li>
            <li class="breadcrumb-item active" aria-current="page">Capacitaciones</li>
        </ol>
    </nav>

    <!-- Encabezado -->
    <div class="row mb-4">
        <div class="col">
            <h2 class="fw-bold mb-1">
                <i class="bi bi-mortarboard me-2 text-success"></i>Capacitaciones
            </h2>
            <p class="text-secondary">
                Seleccioná una capacitación para iniciar en modo presencial o generar un link para modo online.
            </p>
        </div>
    </div>

    <!-- Grid de capacitaciones -->
    <div class="row g-4">
        {% for module in modules %}
        <div class="col-sm-6 col-lg-4 col-xl-3">
            {% if module.is_active %}
            <a href="{% url 'dashboard:modalidad_selector' module.slug %}" class="text-decoration-none">
            {% endif %}
                <div class="card training-card bg-dark border-secondary h-100 {% if not module.is_active %}disabled-card{% endif %}">
                    <div class="card-body text-center py-4">
                        <div class="card-icon mx-auto" style="background-color: {{ module.color }}20;">
                            <i class="{{ module.icon }}" style="color: {{ module.color }};"></i>
                        </div>
                        <h5 class="card-title text-white mb-2">{{ module.title }}</h5>
                        <p class="card-text text-secondary small mb-3">
                            {{ module.description|default:"Capacitación disponible." }}
                        </p>
                        {% if module.is_active %}
                            <span class="badge bg-success px-3 py-1">
                                <i class="bi bi-check-circle me-1"></i>Disponible
                            </span>
                        {% else %}
                            <span class="badge bg-warning text-dark px-3 py-1">
                                <i class="bi bi-clock me-1"></i>Próximamente
                            </span>
                        {% endif %}
                    </div>
                </div>
            {% if module.is_active %}
            </a>
            {% endif %}
        </div>
        {% empty %}
        <div class="col-12">
            <div class="alert alert-info">
                <i class="bi bi-info-circle me-2"></i>
                No hay capacitaciones cargadas aún. Contactá al administrador.
            </div>
        </div>
        {% endfor %}
    </div>

</div>
{% endblock %}
```

---

### ✅ Verificación del Commit 16
- [ ] Migración creada y aplicada sin errores
- [ ] Módulo de Ergonomía tiene ícono, color y order configurados
- [ ] `/dashboard/capacitaciones/` muestra el menú con grid de cards
- [ ] Cards activos son clickeables; inactivos muestran "Próximamente"
- [ ] Breadcrumb funciona correctamente
- [ ] Admin de TrainingModule muestra los nuevos campos

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 16: Menú de capacitaciones con íconos

- Campos icon, color, order, description agregados a TrainingModule
- Migración de base de datos
- Vista de menú de capacitaciones en dashboard
- Grid responsive con cards e íconos
- Estados activo/próximamente con badges
- Admin actualizado con fieldsets y campos editables
- Link al selector de modalidad"
```

---

## COMMIT 17: Selector de modalidad (Presencial/Online)

### 📋 Descripción
Pantalla para elegir entre capacitación presencial u online al clickear una capacitación del menú.

### 🎯 Objetivos
- [x] Página de selección de modalidad para cada módulo
- [x] Descripción de cada modalidad (presencial / online)
- [x] Botones de navegación a cada modo
- [x] Diseño consistente con el dashboard

### 📁 Archivos a crear/modificar

---

#### 1. `apps/dashboard/views.py` (AGREGAR vista)

Agregar al final del archivo actual:

```python
@login_required
@professional_required
def modalidad_selector(request, module_slug):
    """
    Selector de modalidad: Presencial u Online.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    
    return render(request, 'dashboard/modalidad_selector.html', {
        'module': module,
    })
```

---

#### 2. `apps/dashboard/urls.py` (REEMPLAZAR COMPLETO)

```python
# apps/dashboard/urls.py
# ============================================================================
# COMMIT 15-17: URLs del dashboard de profesionales
# ============================================================================

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('capacitaciones/', views.capacitaciones_menu, name='capacitaciones_menu'),
    path('capacitaciones/<slug:module_slug>/', views.modalidad_selector, name='modalidad_selector'),
    path('perfil/', views.profile, name='profile'),
]
```

---

#### 3. `templates/dashboard/modalidad_selector.html` (CREAR)

```html
{% extends "base_dashboard.html" %}

{% block title %}{{ module.title }} - Modalidad - ErgoSolutions{% endblock %}

{% block content %}
<div class="container-fluid py-4 px-4">
    
    <!-- Breadcrumb -->
    <nav aria-label="breadcrumb" class="mb-3">
        <ol class="breadcrumb breadcrumb-dark">
            <li class="breadcrumb-item"><a href="{% url 'dashboard:home' %}">Dashboard</a></li>
            <li class="breadcrumb-item"><a href="{% url 'dashboard:capacitaciones_menu' %}">Capacitaciones</a></li>
            <li class="breadcrumb-item active" aria-current="page">{{ module.title }}</li>
        </ol>
    </nav>

    <!-- Encabezado -->
    <div class="text-center mb-5">
        <div class="d-inline-flex align-items-center justify-content-center rounded-circle mb-3"
             style="width: 80px; height: 80px; background-color: {{ module.color }}20;">
            <i class="{{ module.icon }}" style="font-size: 2.5rem; color: {{ module.color }};"></i>
        </div>
        <h2 class="fw-bold text-white">{{ module.title }}</h2>
        <p class="text-secondary lead">¿Cómo vas a realizar esta capacitación?</p>
    </div>

    <!-- Cards de modalidad -->
    <div class="row g-4 justify-content-center">
        
        <!-- Presencial -->
        <div class="col-md-6 col-lg-5">
            <a href="{% url 'dashboard:presencial_capacitacion' module.slug %}" class="text-decoration-none">
                <div class="card modality-card presencial bg-dark border-secondary h-100">
                    <div class="card-body text-center py-5 px-4">
                        <i class="bi bi-people-fill display-3 text-warning mb-3"></i>
                        <h3 class="text-white mb-3">Modo Presencial</h3>
                        <p class="text-secondary mb-4">
                            Para capacitaciones en el lugar de trabajo. 
                            Proyectá el video, usá el chat con Ergobot y 
                            generá la planilla de asistencia al finalizar.
                        </p>
                        <ul class="list-unstyled text-start text-secondary small">
                            <li class="mb-2"><i class="bi bi-check2 text-warning me-2"></i>Video de capacitación + Chat IA</li>
                            <li class="mb-2"><i class="bi bi-check2 text-warning me-2"></i>Quiz grupal (solo resultado)</li>
                            <li class="mb-2"><i class="bi bi-check2 text-warning me-2"></i>Planilla PDF de asistencia</li>
                            <li><i class="bi bi-check2 text-warning me-2"></i>Sin registro individual de trabajadores</li>
                        </ul>
                        <div class="mt-4">
                            <span class="btn btn-warning btn-lg px-4">
                                <i class="bi bi-easel me-2"></i>Iniciar Presencial
                            </span>
                        </div>
                    </div>
                </div>
            </a>
        </div>

        <!-- Online -->
        <div class="col-md-6 col-lg-5">
            <a href="{% url 'dashboard:online_links' module.slug %}" class="text-decoration-none">
                <div class="card modality-card online bg-dark border-secondary h-100">
                    <div class="card-body text-center py-5 px-4">
                        <i class="bi bi-globe display-3 text-primary mb-3"></i>
                        <h3 class="text-white mb-3">Modo Online</h3>
                        <p class="text-secondary mb-4">
                            Generá un link único para compartir con los trabajadores. 
                            Cada uno accede de forma individual, completa el quiz 
                            y recibe su certificado automáticamente.
                        </p>
                        <ul class="list-unstyled text-start text-secondary small">
                            <li class="mb-2"><i class="bi bi-check2 text-primary me-2"></i>Link compartible por email/WhatsApp</li>
                            <li class="mb-2"><i class="bi bi-check2 text-primary me-2"></i>Registro individual de trabajadores</li>
                            <li class="mb-2"><i class="bi bi-check2 text-primary me-2"></i>Quiz con reglas completas (3 intentos)</li>
                            <li><i class="bi bi-check2 text-primary me-2"></i>Certificado PDF individual automático</li>
                        </ul>
                        <div class="mt-4">
                            <span class="btn btn-primary btn-lg px-4">
                                <i class="bi bi-link-45deg me-2"></i>Gestionar Links
                            </span>
                        </div>
                    </div>
                </div>
            </a>
        </div>

    </div>

    <!-- Volver -->
    <div class="text-center mt-5">
        <a href="{% url 'dashboard:capacitaciones_menu' %}" class="btn btn-outline-secondary">
            <i class="bi bi-arrow-left me-2"></i>Volver al menú de capacitaciones
        </a>
    </div>

</div>
{% endblock %}
```

---

### ✅ Verificación del Commit 17
- [ ] Click en una capacitación activa lleva al selector de modalidad
- [ ] Se muestra el ícono y título del módulo seleccionado
- [ ] Card Presencial lleva a la ruta de capacitación presencial
- [ ] Card Online lleva a la gestión de links
- [ ] Breadcrumb muestra la navegación completa
- [ ] Botón "Volver" regresa al menú

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 17: Selector de modalidad Presencial/Online

- Página de selección al clickear una capacitación
- Descripción de modalidad presencial con features
- Descripción de modalidad online con features
- Botones de navegación a cada modalidad
- Breadcrumb completo
- Diseño consistente con el resto del dashboard"
```

---

# ═══════════════════════════════════════════════════════════════════════════
# FASE 4: MODO PRESENCIAL
# ═══════════════════════════════════════════════════════════════════════════

## COMMIT 18: Página de capacitación presencial

### 📋 Descripción
Crear la página de capacitación para uso presencial por el profesional, con video embebido, chat con Ergobot, y diseño optimizado para proyección (sin registro de trabajadores).

### 🎯 Objetivos
- [x] Crear app `presencial` dentro de `apps/`
- [x] Video de capacitación embebido (YouTube)
- [x] Chat con Ergobot integrado
- [x] Diseño limpio optimizado para proyección
- [x] Sin formularios de registro de trabajadores

### 📁 Archivos a crear/modificar

---

#### 1. Crear app `presencial`

```bash
cd apps
python ../manage.py startapp presencial
```

#### 2. `apps/presencial/__init__.py`
```python
# (vacío)
```

#### 3. `apps/presencial/apps.py`

```python
from django.apps import AppConfig


class PresencialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.presencial'
    verbose_name = 'Capacitación Presencial'
```

---

#### 4. `apps/presencial/views.py` (CREAR)

```python
# apps/presencial/views.py
# ============================================================================
# COMMIT 18: Vistas de capacitación presencial
# ============================================================================

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie

from apps.accounts.decorators import professional_required
from apps.training.models import TrainingModule


@login_required
@professional_required
@ensure_csrf_cookie
def capacitacion_presencial(request, module_slug):
    """
    Página de capacitación para uso presencial.
    Incluye video + chat Ergobot, sin registro de trabajadores.
    Diseñada para proyección en sala.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    
    return render(request, 'presencial/capacitacion.html', {
        'module': module,
    })
```

---

#### 5. `apps/presencial/urls.py` (CREAR)

```python
# apps/presencial/urls.py
# ============================================================================
# COMMIT 18: URLs de capacitación presencial
# ============================================================================

from django.urls import path
from . import views

app_name = 'presencial'

urlpatterns = [
    path('<slug:module_slug>/', views.capacitacion_presencial, name='capacitacion'),
]
```

---

#### 6. `templates/presencial/capacitacion.html` (CREAR)

```html
{% extends "base_dashboard.html" %}
{% load static %}

{% block title %}{{ module.title }} (Presencial) - ErgoSolutions{% endblock %}

{% block extra_css %}
<style>
    /* Estilos optimizados para proyección */
    .video-container {
        position: relative;
        padding-bottom: 56.25%; /* 16:9 */
        height: 0;
        overflow: hidden;
        border-radius: 8px;
        background: #000;
    }
    .video-container iframe {
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        border: 0;
    }
    
    /* Chat container */
    #chat-container {
        height: 450px;
        display: flex;
        flex-direction: column;
    }
    #chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 1rem;
        background: #1a1a2e;
        border-radius: 8px 8px 0 0;
    }
    #chat-input-area {
        padding: 0.75rem;
        background: #16213e;
        border-radius: 0 0 8px 8px;
    }
    .message {
        margin-bottom: 0.75rem;
        max-width: 85%;
    }
    .message.user { margin-left: auto; }
    .message.assistant { margin-right: auto; }
    .message .bubble {
        padding: 0.6rem 1rem;
        border-radius: 12px;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .message.user .bubble {
        background: #0d6efd;
        color: white;
    }
    .message.assistant .bubble {
        background: #2d2d44;
        color: #e0e0e0;
    }
</style>
{% endblock %}

{% block content %}
<div class="container-fluid py-3 px-4">
    
    <!-- Breadcrumb -->
    <nav aria-label="breadcrumb" class="mb-3">
        <ol class="breadcrumb breadcrumb-dark">
            <li class="breadcrumb-item"><a href="{% url 'dashboard:home' %}">Dashboard</a></li>
            <li class="breadcrumb-item"><a href="{% url 'dashboard:capacitaciones_menu' %}">Capacitaciones</a></li>
            <li class="breadcrumb-item">
                <a href="{% url 'dashboard:modalidad_selector' module.slug %}">{{ module.title }}</a>
            </li>
            <li class="breadcrumb-item active">Presencial</li>
        </ol>
    </nav>

    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h3 class="fw-bold mb-0">
            <i class="{{ module.icon }} me-2" style="color: {{ module.color }};"></i>
            {{ module.title }}
            <span class="badge bg-warning text-dark ms-2 fs-6">Presencial</span>
        </h3>
    </div>

    <div class="row g-4">
        <!-- Video -->
        <div class="col-lg-7">
            <div class="card bg-dark border-secondary">
                <div class="card-header border-secondary py-2">
                    <h5 class="mb-0 text-white">
                        <i class="bi bi-play-circle me-2"></i>Video de Capacitación
                    </h5>
                </div>
                <div class="card-body p-0">
                    <div class="video-container">
                        <iframe 
                            src="https://www.youtube.com/embed/{{ module.youtube_id }}?rel=0&modestbranding=1"
                            title="{{ module.title }}"
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                            allowfullscreen>
                        </iframe>
                    </div>
                </div>
                <div class="card-footer border-secondary text-center py-2">
                    <a href="https://www.youtube.com/watch?v={{ module.youtube_id }}" 
                       target="_blank" class="text-secondary small">
                        <i class="bi bi-youtube me-1"></i>Abrir en YouTube
                    </a>
                </div>
            </div>

            <!-- Botón Quiz (debajo del video) -->
            <div class="d-grid mt-3">
                <a href="{% url 'presencial:quiz' module.slug %}" class="btn btn-outline-warning btn-lg">
                    <i class="bi bi-pencil-square me-2"></i>Iniciar Quiz de Evaluación
                </a>
            </div>
        </div>

        <!-- Chat Ergobot -->
        <div class="col-lg-5">
            <div class="card bg-dark border-secondary">
                <div class="card-header border-secondary py-2">
                    <h5 class="mb-0 text-white">
                        <i class="bi bi-robot me-2 text-info"></i>Chat con Ergobot
                    </h5>
                </div>
                <div class="card-body p-0">
                    <div id="chat-container">
                        <div id="chat-messages">
                            <div class="message assistant">
                                <div class="bubble">
                                    ¡Hola! Soy <strong>Ergobot</strong>, tu asistente de ergonomía. 
                                    Podés hacerme preguntas sobre el contenido de la capacitación. 🤖
                                </div>
                            </div>
                        </div>
                        <div id="chat-input-area">
                            <form id="chat-form" class="d-flex gap-2">
                                <input type="text" id="chat-input" class="form-control bg-dark text-light border-secondary" 
                                       placeholder="Escribí tu consulta..." autocomplete="off">
                                <button type="submit" class="btn btn-info px-3" id="send-btn">
                                    <i class="bi bi-send"></i>
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
// ============================================================================
// Chat Ergobot - Reutiliza endpoint SSE existente (/ai/)
// ============================================================================
(function() {
    const form = document.getElementById('chat-form');
    const input = document.getElementById('chat-input');
    const messagesDiv = document.getElementById('chat-messages');
    const sendBtn = document.getElementById('send-btn');
    const moduleSlug = '{{ module.slug }}';
    
    let threadId = null;
    
    function scrollToBottom() {
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    function addMessage(role, html) {
        const div = document.createElement('div');
        div.className = `message ${role}`;
        div.innerHTML = `<div class="bubble">${html}</div>`;
        messagesDiv.appendChild(div);
        scrollToBottom();
        return div;
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        const text = input.value.trim();
        if (!text) return;
        
        addMessage('user', text);
        input.value = '';
        sendBtn.disabled = true;
        
        // Crear bubble del asistente (streaming)
        const assistantMsg = addMessage('assistant', '<em class="text-muted">Pensando...</em>');
        const bubble = assistantMsg.querySelector('.bubble');
        
        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value 
                              || document.cookie.split('csrftoken=')[1]?.split(';')[0];
            
            const response = await fetch('/ai/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({
                    message: text,
                    module_slug: moduleSlug,
                    thread_id: threadId,
                }),
            });
            
            if (!response.ok) throw new Error('Error en la respuesta');
            
            bubble.innerHTML = '';
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop();
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') continue;
                        try {
                            const parsed = JSON.parse(data);
                            if (parsed.delta) {
                                bubble.innerHTML += parsed.delta;
                            }
                            if (parsed.thread_id) {
                                threadId = parsed.thread_id;
                            }
                        } catch(e) {
                            // SSE data no es JSON, agregar como texto
                            bubble.innerHTML += data;
                        }
                    }
                }
                scrollToBottom();
            }
        } catch (err) {
            bubble.innerHTML = '<span class="text-danger">Error al conectar con Ergobot. Intentá de nuevo.</span>';
        }
        
        sendBtn.disabled = false;
        input.focus();
    });
})();
</script>
{% endblock %}
```

---

#### 7. `apps/dashboard/urls.py` (REEMPLAZAR COMPLETO — agrega ruta presencial)

```python
# apps/dashboard/urls.py
# ============================================================================
# COMMIT 15-18: URLs del dashboard de profesionales
# ============================================================================

from django.urls import path, include
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('capacitaciones/', views.capacitaciones_menu, name='capacitaciones_menu'),
    path('capacitaciones/<slug:module_slug>/', views.modalidad_selector, name='modalidad_selector'),
    path('presencial/', include('apps.presencial.urls')),
    path('perfil/', views.profile, name='profile'),
]
```

> **NOTA:** Así las URLs presenciales quedan como `/dashboard/presencial/<slug>/`

---

#### 8. `config/settings.py` (AGREGAR app)

Agregar `'apps.presencial',` en `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... existentes ...
    'apps.presencial',      # NUEVO - Commit 18
    # ... resto ...
]
```

---

### ✅ Verificación del Commit 18
- [ ] `/dashboard/presencial/ergonomia/` muestra la página de capacitación
- [ ] Video de YouTube se muestra correctamente embebido
- [ ] Chat con Ergobot funciona (usa el endpoint `/ai/chat/` existente)
- [ ] Breadcrumb navegable completo
- [ ] Botón "Iniciar Quiz" está visible debajo del video
- [ ] Solo profesionales pueden acceder

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 18: Página de capacitación presencial

- Nueva app 'presencial' para modo presencial
- Video embebido de YouTube
- Chat con Ergobot integrado (reutiliza endpoint SSE)
- Diseño optimizado para proyección
- Sin formularios de registro (uso presencial)
- Breadcrumb completo
- Botón para iniciar quiz"
```

---

## COMMIT 19: Quiz simplificado para modo presencial

### 📋 Descripción
Quiz presencial: mismas preguntas pero sin reglas de intentos/bloqueo. Solo muestra el resultado (score) y botones para generar planilla o volver.

### 🎯 Objetivos
- [x] Quiz con las mismas preguntas que el modo online
- [x] Sin reglas de intentos, bloqueo ni certificado individual
- [x] Resultado muestra solo el score
- [x] Botones "Generar Planilla" y "Volver a la Capacitación"

### 📁 Archivos a crear/modificar

---

#### 1. `apps/presencial/views.py` (REEMPLAZAR COMPLETO)

```python
# apps/presencial/views.py
# ============================================================================
# COMMIT 18-19: Vistas de capacitación y quiz presencial
# ============================================================================

import json

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from apps.accounts.decorators import professional_required
from apps.training.models import TrainingModule
from apps.quiz.models import Question


@login_required
@professional_required
@ensure_csrf_cookie
def capacitacion_presencial(request, module_slug):
    """
    Página de capacitación para uso presencial.
    Incluye video + chat Ergobot, sin registro de trabajadores.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    
    return render(request, 'presencial/capacitacion.html', {
        'module': module,
    })


@login_required
@professional_required
@ensure_csrf_cookie
def quiz_presencial(request, module_slug):
    """
    Quiz para modo presencial.
    Muestra las mismas preguntas pero sin reglas de intentos/bloqueo.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    questions = Question.objects.filter(module=module).prefetch_related('choices')
    
    questions_data = []
    for q in questions:
        choices = [{'id': c.id, 'text': c.text} for c in q.choices.all()]
        questions_data.append({
            'id': q.id,
            'text': q.text,
            'choices': choices,
        })
    
    return render(request, 'presencial/quiz.html', {
        'module': module,
        'questions_json': json.dumps(questions_data),
        'total_questions': len(questions_data),
    })


@login_required
@professional_required
@require_POST
def quiz_presencial_submit(request, module_slug):
    """
    Corrige el quiz presencial. Retorna JSON con score.
    Sin guardar intentos ni generar certificados.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    
    try:
        body = json.loads(request.body)
        answers = body.get('answers', {})
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    
    questions = Question.objects.filter(module=module).prefetch_related('choices')
    
    correct = 0
    total = questions.count()
    details = []
    
    for q in questions:
        selected_id = answers.get(str(q.id))
        correct_choice = q.choices.filter(is_correct=True).first()
        is_correct = (str(selected_id) == str(correct_choice.id)) if correct_choice and selected_id else False
        
        if is_correct:
            correct += 1
        
        details.append({
            'question_id': q.id,
            'question_text': q.text,
            'selected_id': selected_id,
            'correct_id': correct_choice.id if correct_choice else None,
            'correct_text': correct_choice.text if correct_choice else '',
            'is_correct': is_correct,
            'explanation': q.explanation if hasattr(q, 'explanation') else '',
        })
    
    passed = correct >= 8
    
    return JsonResponse({
        'score': correct,
        'total': total,
        'passed': passed,
        'details': details,
        'module_slug': module_slug,
        'module_title': module.title,
    })
```

---

#### 2. `apps/presencial/urls.py` (REEMPLAZAR COMPLETO)

```python
# apps/presencial/urls.py
# ============================================================================
# COMMIT 18-19: URLs de capacitación presencial
# ============================================================================

from django.urls import path
from . import views

app_name = 'presencial'

urlpatterns = [
    path('<slug:module_slug>/', views.capacitacion_presencial, name='capacitacion'),
    path('<slug:module_slug>/quiz/', views.quiz_presencial, name='quiz'),
    path('<slug:module_slug>/quiz/submit/', views.quiz_presencial_submit, name='quiz_submit'),
]
```

---

#### 3. `templates/presencial/quiz.html` (CREAR)

```html
{% extends "base_dashboard.html" %}
{% load static %}

{% block title %}Quiz - {{ module.title }} (Presencial) - ErgoSolutions{% endblock %}

{% block extra_css %}
<style>
    .question-card { border-radius: 12px; }
    .choice-btn {
        transition: all 0.2s ease;
        border: 2px solid #495057;
        border-radius: 8px;
        cursor: pointer;
        text-align: left;
    }
    .choice-btn:hover { border-color: #6c757d; background: #1a1a2e; }
    .choice-btn.selected { border-color: #0d6efd; background: #0d6efd20; }
    .choice-btn.correct { border-color: #198754; background: #19875420; }
    .choice-btn.incorrect { border-color: #dc3545; background: #dc354520; }
    
    /* Resultado */
    .result-score { font-size: 5rem; font-weight: 800; }
    .result-passed { color: #198754; }
    .result-failed { color: #dc3545; }
</style>
{% endblock %}

{% block content %}
<div class="container-fluid py-4 px-4">
    
    <!-- Breadcrumb -->
    <nav aria-label="breadcrumb" class="mb-3">
        <ol class="breadcrumb breadcrumb-dark">
            <li class="breadcrumb-item"><a href="{% url 'dashboard:home' %}">Dashboard</a></li>
            <li class="breadcrumb-item"><a href="{% url 'dashboard:capacitaciones_menu' %}">Capacitaciones</a></li>
            <li class="breadcrumb-item">
                <a href="{% url 'presencial:capacitacion' module.slug %}">{{ module.title }}</a>
            </li>
            <li class="breadcrumb-item active">Quiz Presencial</li>
        </ol>
    </nav>

    <!-- Quiz Container -->
    <div id="quiz-section">
        <div class="text-center mb-4">
            <h3 class="fw-bold">
                <i class="bi bi-pencil-square me-2 text-warning"></i>
                Quiz de Evaluación
                <span class="badge bg-warning text-dark ms-2">Presencial</span>
            </h3>
            <p class="text-secondary">
                Pregunta <span id="current-q">1</span> de {{ total_questions }}
            </p>
            <div class="progress mx-auto" style="max-width: 500px; height: 6px;">
                <div class="progress-bar bg-warning" id="progress-bar" style="width: 0%"></div>
            </div>
        </div>

        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div id="question-area">
                    <!-- Se llena con JS -->
                </div>
                
                <div class="d-flex justify-content-between mt-4">
                    <button class="btn btn-outline-secondary" id="prev-btn" disabled>
                        <i class="bi bi-arrow-left me-2"></i>Anterior
                    </button>
                    <button class="btn btn-warning" id="next-btn" disabled>
                        Siguiente<i class="bi bi-arrow-right ms-2"></i>
                    </button>
                    <button class="btn btn-success d-none" id="submit-btn">
                        <i class="bi bi-check-lg me-2"></i>Finalizar Quiz
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Resultado (oculto hasta submit) -->
    <div id="result-section" class="d-none">
        <div class="row justify-content-center">
            <div class="col-lg-6 text-center">
                <div class="card bg-dark border-secondary shadow-lg">
                    <div class="card-body py-5">
                        <div id="result-icon" class="mb-3"></div>
                        <div id="result-score" class="result-score mb-2"></div>
                        <p id="result-text" class="lead mb-4"></p>
                        
                        <div class="d-grid gap-3">
                            <a href="{% url 'presencial:planilla_pdf' module.slug %}" 
                               class="btn btn-warning btn-lg" id="btn-planilla" target="_blank">
                                <i class="bi bi-file-earmark-pdf me-2"></i>Generar Planilla de Asistencia
                            </a>
                            <a href="{% url 'presencial:capacitacion' module.slug %}" 
                               class="btn btn-outline-light">
                                <i class="bi bi-arrow-left me-2"></i>Volver a la Capacitación
                            </a>
                            <button class="btn btn-outline-secondary" onclick="location.reload()">
                                <i class="bi bi-arrow-repeat me-2"></i>Repetir Quiz
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

</div>
{% endblock %}

{% block extra_js %}
<script>
(function() {
    const questions = {{ questions_json|safe }};
    const answers = {};
    let currentIndex = 0;
    
    const questionArea = document.getElementById('question-area');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const submitBtn = document.getElementById('submit-btn');
    const progressBar = document.getElementById('progress-bar');
    const currentQSpan = document.getElementById('current-q');
    
    function renderQuestion(index) {
        const q = questions[index];
        currentQSpan.textContent = index + 1;
        progressBar.style.width = ((index + 1) / questions.length * 100) + '%';
        
        let html = `
            <div class="card question-card bg-dark border-secondary">
                <div class="card-body p-4">
                    <h5 class="text-white mb-4">${index + 1}. ${q.text}</h5>
                    <div class="d-grid gap-2">
        `;
        
        q.choices.forEach(c => {
            const selected = answers[q.id] === c.id ? 'selected' : '';
            html += `
                <button class="btn choice-btn p-3 text-light ${selected}" 
                        onclick="selectChoice(${q.id}, ${c.id}, this)">
                    ${c.text}
                </button>
            `;
        });
        
        html += '</div></div></div>';
        questionArea.innerHTML = html;
        
        prevBtn.disabled = index === 0;
        
        if (index === questions.length - 1) {
            nextBtn.classList.add('d-none');
            submitBtn.classList.remove('d-none');
        } else {
            nextBtn.classList.remove('d-none');
            submitBtn.classList.add('d-none');
        }
        
        nextBtn.disabled = !answers[q.id];
        submitBtn.disabled = Object.keys(answers).length < questions.length;
    }
    
    window.selectChoice = function(qId, cId, btn) {
        answers[qId] = cId;
        document.querySelectorAll('.choice-btn').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        nextBtn.disabled = false;
        submitBtn.disabled = Object.keys(answers).length < questions.length;
    };
    
    prevBtn.addEventListener('click', () => {
        if (currentIndex > 0) { currentIndex--; renderQuestion(currentIndex); }
    });
    
    nextBtn.addEventListener('click', () => {
        if (currentIndex < questions.length - 1) { currentIndex++; renderQuestion(currentIndex); }
    });
    
    submitBtn.addEventListener('click', async () => {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Enviando...';
        
        const csrfToken = document.cookie.split('csrftoken=')[1]?.split(';')[0];
        
        try {
            const resp = await fetch('{% url "presencial:quiz_submit" module.slug %}', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({ answers }),
            });
            
            const data = await resp.json();
            showResult(data);
        } catch(err) {
            alert('Error al enviar el quiz. Intentá de nuevo.');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-check-lg me-2"></i>Finalizar Quiz';
        }
    });
    
    function showResult(data) {
        document.getElementById('quiz-section').classList.add('d-none');
        const resultSection = document.getElementById('result-section');
        resultSection.classList.remove('d-none');
        
        const iconEl = document.getElementById('result-icon');
        const scoreEl = document.getElementById('result-score');
        const textEl = document.getElementById('result-text');
        
        if (data.passed) {
            iconEl.innerHTML = '<i class="bi bi-check-circle-fill text-success" style="font-size: 4rem;"></i>';
            scoreEl.innerHTML = `<span class="result-passed">${data.score}/${data.total}</span>`;
            textEl.textContent = '¡Aprobado! Podés generar la planilla de asistencia.';
        } else {
            iconEl.innerHTML = '<i class="bi bi-x-circle-fill text-danger" style="font-size: 4rem;"></i>';
            scoreEl.innerHTML = `<span class="result-failed">${data.score}/${data.total}</span>`;
            textEl.textContent = 'No aprobado. Mínimo requerido: 8/10.';
        }
    }
    
    // Iniciar
    renderQuestion(0);
})();
</script>
{% endblock %}
```

---

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 19: Quiz simplificado para modo presencial

- Mismo quiz pero sin reglas de intentos/bloqueo
- Navegación pregunta por pregunta con barra de progreso
- Resultado muestra solo el score (aprobado/no aprobado)
- Sin generación de certificado individual
- Botón 'Generar Planilla de Asistencia'
- Botón 'Volver a la Capacitación'
- Botón 'Repetir Quiz'"
```

---

## COMMIT 20: Generador de planilla PDF grupal

### 📋 Descripción
Crear PDF de planilla para capacitaciones presenciales con datos del módulo, profesional, fecha, y listado de participantes con líneas para firma.

### 📁 Archivos a crear/modificar

---

#### 1. `apps/presencial/pdf.py` (CREAR)

```python
# apps/presencial/pdf.py
# ============================================================================
# COMMIT 20: Generador de planilla PDF para capacitaciones presenciales
# ============================================================================

import io
from datetime import date, datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)


def build_planilla_presencial_pdf(module, professional, session_date=None, num_rows=25):
    """
    Genera una planilla PDF para capacitación presencial.
    
    Args:
        module: TrainingModule instance
        professional: CustomUser instance (profesional)
        session_date: fecha de la sesión (date o None para hoy)
        num_rows: cantidad de filas para participantes
    
    Returns:
        bytes del PDF generado
    """
    buffer = io.BytesIO()
    
    if session_date is None:
        session_date = date.today()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )
    
    # Estilos
    styles = {
        'title': ParagraphStyle(
            'title',
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=colors.HexColor('#1a1a2e'),
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        'subtitle': ParagraphStyle(
            'subtitle',
            fontName='Helvetica',
            fontSize=11,
            textColor=colors.HexColor('#2d3748'),
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        'header_info': ParagraphStyle(
            'header_info',
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor('#2d3748'),
            alignment=TA_LEFT,
            spaceAfter=2,
        ),
        'footer': ParagraphStyle(
            'footer',
            fontName='Helvetica-Oblique',
            fontSize=8,
            textColor=colors.HexColor('#718096'),
            alignment=TA_CENTER,
        ),
    }
    
    story = []
    
    # === ENCABEZADO ===
    story.append(Paragraph("PLANILLA DE CAPACITACIÓN PRESENCIAL", styles['title']))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("REGISTRO DE ASISTENCIA", styles['subtitle']))
    story.append(Spacer(1, 8 * mm))
    
    # === DATOS DE LA CAPACITACIÓN ===
    page_width = A4[0] - 3 * cm  # ancho disponible
    
    info_data = [
        ["Capacitación:", module.title],
        ["Responsable:", f"{professional.display_name}"],
        ["Profesión:", f"{professional.profession or 'No especificada'}"],
        ["Matrícula:", f"{professional.license_number or 'No especificada'}"],
        ["Fecha:", session_date.strftime("%d/%m/%Y")],
        ["Lugar:", "________________________________________"],
    ]
    
    info_table = Table(info_data, colWidths=[3.5 * cm, page_width - 3.5 * cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2d3748')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 10 * mm))
    
    # === TABLA DE PARTICIPANTES ===
    col_widths = [1 * cm, 6.5 * cm, 3 * cm, page_width - 10.5 * cm]
    
    # Header
    table_data = [["N°", "Nombre y Apellido", "DNI", "Firma"]]
    
    # Filas vacías para completar
    for i in range(1, num_rows + 1):
        table_data.append([str(i), "", "", ""])
    
    participants_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    participants_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        # Cuerpo
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        
        # Bordes
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#a0aec0')),
        
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        
        # Altura de filas
        ('ROWHEIGHT', (0, 1), (-1, -1), 22),
        
        # Alternar color de fondo
        *[
            ('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f7fafc'))
            for i in range(2, num_rows + 1, 2)
        ],
    ]))
    story.append(participants_table)
    
    story.append(Spacer(1, 10 * mm))
    
    # === FOOTER ===
    story.append(Paragraph(
        "Documento generado por ErgoSolutions — www.ergosolutions.com.ar",
        styles['footer']
    ))
    story.append(Paragraph(
        f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        styles['footer']
    ))
    
    doc.build(story)
    return buffer.getvalue()
```

---

#### 2. `apps/presencial/views.py` (AGREGAR al final)

```python
from django.http import HttpResponse
from .pdf import build_planilla_presencial_pdf


@login_required
@professional_required
def planilla_pdf(request, module_slug):
    """
    Genera y descarga la planilla PDF de asistencia.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    
    pdf_bytes = build_planilla_presencial_pdf(
        module=module,
        professional=request.user,
    )
    
    filename = f"planilla_{module.slug}_{date.today().strftime('%Y%m%d')}.pdf"
    
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
```

> **NOTA:** Agregar `from datetime import date` al inicio del archivo si no está.

---

#### 3. `apps/presencial/urls.py` (REEMPLAZAR COMPLETO)

```python
# apps/presencial/urls.py
# ============================================================================
# COMMIT 18-20: URLs de capacitación presencial
# ============================================================================

from django.urls import path
from . import views

app_name = 'presencial'

urlpatterns = [
    path('<slug:module_slug>/', views.capacitacion_presencial, name='capacitacion'),
    path('<slug:module_slug>/quiz/', views.quiz_presencial, name='quiz'),
    path('<slug:module_slug>/quiz/submit/', views.quiz_presencial_submit, name='quiz_submit'),
    path('<slug:module_slug>/planilla/', views.planilla_pdf, name='planilla_pdf'),
]
```

---

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 20: Generador de planilla PDF para capacitaciones presenciales

- Template PDF profesional con ReportLab
- Encabezado con nombre de capacitación
- Datos del responsable (profesional, profesión, matrícula)
- Campo de fecha y lugar
- Tabla de 25 filas para participantes (N°, Nombre, DNI, Firma)
- Descarga inmediata al presionar botón
- Diseño limpio y profesional"
```

---

## COMMIT 21: Modelo PresencialSession e historial

### 📋 Descripción
Crear modelo para registrar sesiones presenciales y vista de historial.

### 📁 Archivos a crear/modificar

---

#### 1. `apps/presencial/models.py` (CREAR)

```python
# apps/presencial/models.py
# ============================================================================
# COMMIT 21: Modelo PresencialSession para registro de sesiones
# ============================================================================

from django.db import models
from django.conf import settings

from apps.training.models import TrainingModule


class PresencialSession(models.Model):
    """Registro de sesiones de capacitación presencial."""
    
    module = models.ForeignKey(
        TrainingModule,
        on_delete=models.CASCADE,
        related_name='presencial_sessions',
        verbose_name='Módulo'
    )
    professional = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='presencial_sessions',
        verbose_name='Profesional'
    )
    session_date = models.DateField(verbose_name='Fecha de la sesión')
    location = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name='Ubicación'
    )
    participants_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Cantidad de participantes'
    )
    quiz_score = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name='Score del quiz'
    )
    quiz_passed = models.BooleanField(
        default=False,
        verbose_name='Quiz aprobado'
    )
    notes = models.TextField(
        blank=True, default='',
        verbose_name='Notas / Observaciones'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-session_date', '-created_at']
        verbose_name = 'Sesión presencial'
        verbose_name_plural = 'Sesiones presenciales'
    
    def __str__(self):
        return f"{self.module.title} - {self.session_date} ({self.professional.display_name})"
```

---

#### 2. `apps/presencial/admin.py` (CREAR)

```python
# apps/presencial/admin.py
# ============================================================================
# COMMIT 21: Admin de sesiones presenciales
# ============================================================================

from django.contrib import admin
from .models import PresencialSession


@admin.register(PresencialSession)
class PresencialSessionAdmin(admin.ModelAdmin):
    list_display = (
        'module', 'professional', 'session_date', 'location',
        'participants_count', 'quiz_score', 'quiz_passed', 'created_at'
    )
    list_filter = ('module', 'quiz_passed', 'session_date')
    search_fields = ('professional__email', 'professional__first_name', 'location')
    date_hierarchy = 'session_date'
    
    readonly_fields = ('created_at',)
```

---

#### 3. Migración

```bash
python manage.py makemigrations presencial --name create_presencial_session
python manage.py migrate
```

---

#### 4. Agregar registro automático en la vista de planilla

En `apps/presencial/views.py`, actualizar la vista `planilla_pdf`:

```python
from .models import PresencialSession


@login_required
@professional_required
def planilla_pdf(request, module_slug):
    """
    Genera la planilla PDF y registra la sesión presencial.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    
    # Registrar la sesión
    session = PresencialSession.objects.create(
        module=module,
        professional=request.user,
        session_date=date.today(),
        location=request.GET.get('location', ''),
        participants_count=int(request.GET.get('participants', 0) or 0),
    )
    
    pdf_bytes = build_planilla_presencial_pdf(
        module=module,
        professional=request.user,
    )
    
    filename = f"planilla_{module.slug}_{date.today().strftime('%Y%m%d')}.pdf"
    
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
```

---

#### 5. `apps/presencial/views.py` — AGREGAR vista de historial

```python
@login_required
@professional_required
def historial_presencial(request):
    """
    Historial de sesiones presenciales del profesional.
    """
    sessions = PresencialSession.objects.filter(
        professional=request.user
    ).select_related('module')
    
    return render(request, 'presencial/historial.html', {
        'sessions': sessions,
    })
```

---

#### 6. `apps/presencial/urls.py` (REEMPLAZAR COMPLETO)

```python
# apps/presencial/urls.py
# ============================================================================
# COMMIT 18-21: URLs de capacitación presencial completas
# ============================================================================

from django.urls import path
from . import views

app_name = 'presencial'

urlpatterns = [
    path('historial/', views.historial_presencial, name='historial'),
    path('<slug:module_slug>/', views.capacitacion_presencial, name='capacitacion'),
    path('<slug:module_slug>/quiz/', views.quiz_presencial, name='quiz'),
    path('<slug:module_slug>/quiz/submit/', views.quiz_presencial_submit, name='quiz_submit'),
    path('<slug:module_slug>/planilla/', views.planilla_pdf, name='planilla_pdf'),
]
```

---

#### 7. `templates/presencial/historial.html` (CREAR)

```html
{% extends "base_dashboard.html" %}

{% block title %}Historial Presencial - ErgoSolutions{% endblock %}

{% block content %}
<div class="container-fluid py-4 px-4">
    
    <nav aria-label="breadcrumb" class="mb-3">
        <ol class="breadcrumb breadcrumb-dark">
            <li class="breadcrumb-item"><a href="{% url 'dashboard:home' %}">Dashboard</a></li>
            <li class="breadcrumb-item active">Historial Presencial</li>
        </ol>
    </nav>

    <h2 class="fw-bold mb-4">
        <i class="bi bi-clock-history me-2 text-warning"></i>Historial de Capacitaciones Presenciales
    </h2>

    {% if sessions %}
    <div class="table-responsive">
        <table class="table table-dark table-hover align-middle">
            <thead class="table-secondary">
                <tr>
                    <th>Fecha</th>
                    <th>Capacitación</th>
                    <th>Ubicación</th>
                    <th>Participantes</th>
                    <th>Quiz</th>
                </tr>
            </thead>
            <tbody>
                {% for s in sessions %}
                <tr>
                    <td>{{ s.session_date|date:"d/m/Y" }}</td>
                    <td>{{ s.module.title }}</td>
                    <td>{{ s.location|default:"-" }}</td>
                    <td>{{ s.participants_count|default:"-" }}</td>
                    <td>
                        {% if s.quiz_score is not None %}
                            <span class="badge {% if s.quiz_passed %}bg-success{% else %}bg-danger{% endif %}">
                                {{ s.quiz_score }}/10
                            </span>
                        {% else %}
                            <span class="text-muted">-</span>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% else %}
    <div class="alert alert-info">
        <i class="bi bi-info-circle me-2"></i>
        Todavía no realizaste capacitaciones presenciales.
    </div>
    {% endif %}

</div>
{% endblock %}
```

---

#### 8. Actualizar stats en dashboard (`apps/dashboard/views.py`)

Actualizar la vista `home` para incluir stats reales:

```python
from apps.presencial.models import PresencialSession


@login_required
@professional_required
def home(request):
    """Dashboard principal del profesional con stats."""
    
    presencial_count = PresencialSession.objects.filter(
        professional=request.user
    ).count()
    
    stats = {
        'capacitaciones_total': presencial_count,
        'links_generados': 0,       # Se actualiza en Commit 22
        'trabajadores_capacitados': 0,  # Se actualiza en Commit 25
    }
    
    return render(request, 'dashboard/home.html', {
        'stats': stats,
    })
```

---

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 21: Modelo PresencialSession e historial

- Modelo PresencialSession para registro de sesiones
- Campos: module, professional, fecha, ubicación, participantes, score
- Registro automático al generar planilla PDF
- Vista de historial de sesiones presenciales
- Admin configurado con filtros y búsqueda
- Stats del dashboard actualizadas con sesiones reales
- Integración con dashboard del profesional"
```

---

# ═══════════════════════════════════════════════════════════════════════════
# FASE 5: MODO ONLINE (SISTEMA DE LINKS)
# ═══════════════════════════════════════════════════════════════════════════

## COMMIT 22: Modelo CapacitacionLink

### 📋 Descripción
Crear el modelo para gestionar links únicos de capacitaciones online.

### 📁 Archivos a crear/modificar

---

#### 1. `apps/presencial/models.py` → Mover a `apps/capacitaciones/` no es necesario.

Creamos los modelos de links en la app `training` ya que es el lugar natural.

#### 1. `apps/training/models.py` (AGREGAR al final)

```python
# ============================================================================
# COMMIT 22: Modelo CapacitacionLink
# ============================================================================

import uuid
from django.conf import settings


class CapacitacionLink(models.Model):
    """Link único para compartir una capacitación en modo online."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(
        TrainingModule,
        on_delete=models.CASCADE,
        related_name='capacitacion_links',
        verbose_name='Módulo'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='capacitacion_links',
        verbose_name='Creado por'
    )
    label = models.CharField(
        max_length=100, blank=True, default='',
        verbose_name='Etiqueta',
        help_text='Nombre descriptivo (ej: "Empresa XYZ - Marzo 2026")'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Fecha de expiración',
        help_text='Dejar vacío para que no expire'
    )
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    access_count = models.PositiveIntegerField(
        default=0, verbose_name='Accesos'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Link de capacitación'
        verbose_name_plural = 'Links de capacitación'
    
    def __str__(self):
        return f"{self.module.title} - {self.label or str(self.id)[:8]}"
    
    @property
    def is_expired(self):
        from django.utils import timezone
        if self.expires_at and self.expires_at < timezone.now():
            return True
        return False
    
    @property
    def is_usable(self):
        return self.is_active and not self.is_expired
    
    def get_absolute_url(self):
        return f"/c/{self.module.slug}/?ref={self.id}"
```

---

#### 2. `apps/training/admin.py` (AGREGAR al final)

```python
from .models import CapacitacionLink


@admin.register(CapacitacionLink)
class CapacitacionLinkAdmin(admin.ModelAdmin):
    list_display = ('module', 'label', 'created_by', 'created_at', 'is_active', 'access_count')
    list_filter = ('module', 'is_active', 'created_at')
    search_fields = ('label', 'created_by__email')
    readonly_fields = ('id', 'created_at', 'access_count')
```

---

#### 3. Migración

```bash
python manage.py makemigrations training --name add_capacitacion_link
python manage.py migrate
```

---

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 22: Modelo CapacitacionLink para links compartibles

- Modelo CapacitacionLink con UUID único como PK
- Asociación con módulo y profesional creador
- Campo label para descripción del link
- Campo de expiración opcional
- Contador de accesos para estadísticas
- Properties is_expired, is_usable
- Método get_absolute_url() para generar URL
- Admin configurado"
```

---

## COMMIT 23: Generación y copia de links

### 📋 Descripción
Interfaz para generar links, copiarlos, y ver historial de links generados.

### 📁 Archivos a crear/modificar

---

#### 1. `apps/dashboard/views.py` (AGREGAR vistas de links)

Agregar las siguientes vistas:

```python
from apps.training.models import CapacitacionLink


@login_required
@professional_required
def online_links(request, module_slug):
    """
    Gestión de links para una capacitación online.
    Lista links existentes y permite crear nuevos.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    
    links = CapacitacionLink.objects.filter(
        module=module,
        created_by=request.user,
    )
    
    return render(request, 'dashboard/online_links.html', {
        'module': module,
        'links': links,
    })


@login_required
@professional_required
@require_POST
def generate_link(request, module_slug):
    """Genera un nuevo link de capacitación."""
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    
    label = request.POST.get('label', '').strip()
    
    link = CapacitacionLink.objects.create(
        module=module,
        created_by=request.user,
        label=label,
    )
    
    messages.success(request, 'Link generado exitosamente.')
    return redirect('dashboard:online_links', module_slug=module_slug)
```

> **NOTA:** Agregar `from django.views.decorators.http import require_POST` y `from django.shortcuts import redirect` y `from django.contrib import messages` si no están importados.

---

#### 2. `apps/dashboard/urls.py` (REEMPLAZAR COMPLETO)

```python
# apps/dashboard/urls.py
# ============================================================================
# COMMIT 15-23: URLs del dashboard de profesionales
# ============================================================================

from django.urls import path, include
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('capacitaciones/', views.capacitaciones_menu, name='capacitaciones_menu'),
    path('capacitaciones/<slug:module_slug>/', views.modalidad_selector, name='modalidad_selector'),
    path('capacitaciones/<slug:module_slug>/links/', views.online_links, name='online_links'),
    path('capacitaciones/<slug:module_slug>/links/generar/', views.generate_link, name='generate_link'),
    path('presencial/', include('apps.presencial.urls')),
    path('perfil/', views.profile, name='profile'),
]
```

---

#### 3. `templates/dashboard/online_links.html` (CREAR)

```html
{% extends "base_dashboard.html" %}

{% block title %}Links Online - {{ module.title }} - ErgoSolutions{% endblock %}

{% block content %}
<div class="container-fluid py-4 px-4">
    
    <!-- Breadcrumb -->
    <nav aria-label="breadcrumb" class="mb-3">
        <ol class="breadcrumb breadcrumb-dark">
            <li class="breadcrumb-item"><a href="{% url 'dashboard:home' %}">Dashboard</a></li>
            <li class="breadcrumb-item"><a href="{% url 'dashboard:capacitaciones_menu' %}">Capacitaciones</a></li>
            <li class="breadcrumb-item">
                <a href="{% url 'dashboard:modalidad_selector' module.slug %}">{{ module.title }}</a>
            </li>
            <li class="breadcrumb-item active">Links Online</li>
        </ol>
    </nav>

    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h3 class="fw-bold mb-1">
                <i class="bi bi-globe me-2 text-primary"></i>
                Modo Online — {{ module.title }}
            </h3>
            <p class="text-secondary mb-0">
                Generá links para compartir la capacitación con los trabajadores.
            </p>
        </div>
    </div>

    <!-- Formulario para crear link -->
    <div class="card bg-dark border-primary mb-4">
        <div class="card-body">
            <h5 class="card-title text-white mb-3">
                <i class="bi bi-plus-circle me-2"></i>Generar nuevo link
            </h5>
            <form method="post" action="{% url 'dashboard:generate_link' module.slug %}" class="row g-3 align-items-end">
                {% csrf_token %}
                <div class="col-md-8">
                    <label class="form-label text-secondary">Etiqueta (opcional)</label>
                    <input type="text" name="label" class="form-control bg-black text-light border-secondary" 
                           placeholder="Ej: Empresa XYZ - Marzo 2026">
                </div>
                <div class="col-md-4">
                    <button type="submit" class="btn btn-primary w-100">
                        <i class="bi bi-link-45deg me-2"></i>Generar Link
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- Lista de links existentes -->
    <h5 class="text-secondary mb-3">
        <i class="bi bi-list-ul me-2"></i>Links generados ({{ links.count }})
    </h5>

    {% for link in links %}
    <div class="card bg-dark border-secondary mb-3">
        <div class="card-body">
            <div class="row align-items-center">
                <div class="col-md-5">
                    <h6 class="text-white mb-1">
                        {% if link.label %}{{ link.label }}{% else %}Link {{ link.id|truncatechars:12 }}{% endif %}
                    </h6>
                    <small class="text-secondary">
                        Creado: {{ link.created_at|date:"d/m/Y H:i" }}
                        {% if link.is_expired %}
                            <span class="badge bg-danger ms-2">Expirado</span>
                        {% elif not link.is_active %}
                            <span class="badge bg-secondary ms-2">Inactivo</span>
                        {% else %}
                            <span class="badge bg-success ms-2">Activo</span>
                        {% endif %}
                    </small>
                </div>
                <div class="col-md-4">
                    <div class="input-group input-group-sm">
                        <input type="text" class="form-control bg-black text-light border-secondary" 
                               value="{{ request.scheme }}://{{ request.get_host }}{{ link.get_absolute_url }}" 
                               readonly id="link-{{ link.id }}">
                        <button class="btn btn-outline-info" onclick="copyLink('{{ link.id }}')" title="Copiar">
                            <i class="bi bi-clipboard" id="icon-{{ link.id }}"></i>
                        </button>
                    </div>
                </div>
                <div class="col-md-3 text-end">
                    <span class="badge bg-info me-2">
                        <i class="bi bi-eye me-1"></i>{{ link.access_count }} accesos
                    </span>
                    <a href="{% url 'dashboard:share_link' module.slug link.id %}" 
                       class="btn btn-sm btn-outline-warning" title="Enviar por email">
                        <i class="bi bi-envelope"></i>
                    </a>
                </div>
            </div>
        </div>
    </div>
    {% empty %}
    <div class="alert alert-info">
        <i class="bi bi-info-circle me-2"></i>
        No hay links generados para esta capacitación. Creá uno arriba.
    </div>
    {% endfor %}

    <!-- Volver -->
    <div class="mt-4">
        <a href="{% url 'dashboard:modalidad_selector' module.slug %}" class="btn btn-outline-secondary">
            <i class="bi bi-arrow-left me-2"></i>Volver
        </a>
    </div>

</div>
{% endblock %}

{% block extra_js %}
<script>
function copyLink(linkId) {
    const input = document.getElementById('link-' + linkId);
    const icon = document.getElementById('icon-' + linkId);
    
    navigator.clipboard.writeText(input.value).then(() => {
        icon.className = 'bi bi-clipboard-check text-success';
        setTimeout(() => { icon.className = 'bi bi-clipboard'; }, 2000);
    }).catch(() => {
        input.select();
        document.execCommand('copy');
        icon.className = 'bi bi-clipboard-check text-success';
        setTimeout(() => { icon.className = 'bi bi-clipboard'; }, 2000);
    });
}
</script>
{% endblock %}
```

---

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 23: Generación y copia de links de capacitaciones

- Vista para generar nuevo CapacitacionLink con etiqueta
- UI mostrando el link generado con URL completa
- Botón 'Copiar' con JavaScript Clipboard API
- Feedback visual al copiar (ícono check)
- Historial de links generados con stats de accesos
- Botón para compartir por email (preparado para Commit 24)"
```

---

## COMMIT 24: Compartir links por email

### 📋 Descripción
Funcionalidad para enviar links de capacitación por email a múltiples destinatarios.

### 📁 Archivos a crear/modificar

---

#### 1. `apps/training/models.py` (AGREGAR al final)

```python
# ============================================================================
# COMMIT 24: Modelo LinkShareLog
# ============================================================================

class LinkShareLog(models.Model):
    """Registro de envíos de links por email."""
    
    link = models.ForeignKey(
        CapacitacionLink,
        on_delete=models.CASCADE,
        related_name='share_logs',
        verbose_name='Link'
    )
    shared_to_email = models.EmailField(verbose_name='Email destinatario')
    shared_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-shared_at']
        verbose_name = 'Envío de link'
        verbose_name_plural = 'Envíos de links'
    
    def __str__(self):
        return f"{self.link} → {self.shared_to_email}"
```

---

#### 2. Migración

```bash
python manage.py makemigrations training --name add_link_share_log
python manage.py migrate
```

---

#### 3. `apps/dashboard/forms.py` (CREAR)

```python
# apps/dashboard/forms.py
# ============================================================================
# COMMIT 24: Formularios del dashboard
# ============================================================================

from django import forms


class ShareLinkForm(forms.Form):
    """Formulario para compartir link por email."""
    
    emails = forms.CharField(
        label='Emails destinatarios',
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'email1@ejemplo.com, email2@ejemplo.com',
            'class': 'form-control bg-black text-light border-secondary',
        }),
        help_text='Separar múltiples emails con coma.'
    )
    message = forms.CharField(
        label='Mensaje personalizado (opcional)',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Hola, te comparto la capacitación que debés completar...',
            'class': 'form-control bg-black text-light border-secondary',
        }),
    )
    
    def clean_emails(self):
        raw = self.cleaned_data.get('emails', '')
        emails = [e.strip().lower() for e in raw.replace(';', ',').split(',') if e.strip()]
        
        if not emails:
            raise forms.ValidationError('Ingresá al menos un email.')
        
        # Validación básica
        from django.core.validators import validate_email
        for email in emails:
            try:
                validate_email(email)
            except forms.ValidationError:
                raise forms.ValidationError(f'Email inválido: {email}')
        
        return emails
```

---

#### 4. `apps/dashboard/views.py` (AGREGAR vistas de compartir)

```python
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings as django_settings

from apps.training.models import CapacitacionLink, LinkShareLog
from .forms import ShareLinkForm


@login_required
@professional_required
def share_link(request, module_slug, link_id):
    """
    Formulario para compartir link por email.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    link = get_object_or_404(
        CapacitacionLink, id=link_id, module=module, created_by=request.user
    )
    
    if request.method == 'POST':
        form = ShareLinkForm(request.POST)
        if form.is_valid():
            emails = form.cleaned_data['emails']
            custom_message = form.cleaned_data.get('message', '')
            
            link_url = f"{request.scheme}://{request.get_host()}{link.get_absolute_url()}"
            
            sent_count = 0
            for email in emails:
                try:
                    subject = f"Capacitación: {module.title} - ErgoSolutions"
                    body = (
                        f"Hola,\n\n"
                        f"{request.user.display_name} te envía la siguiente capacitación:\n\n"
                        f"📚 {module.title}\n\n"
                    )
                    if custom_message:
                        body += f"Mensaje: {custom_message}\n\n"
                    body += (
                        f"Accedé al siguiente link para realizar la capacitación:\n"
                        f"{link_url}\n\n"
                        f"---\n"
                        f"ErgoSolutions - Plataforma de Capacitación\n"
                    )
                    
                    send_mail(
                        subject=subject,
                        message=body,
                        from_email=django_settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        fail_silently=True,
                    )
                    
                    LinkShareLog.objects.create(
                        link=link,
                        shared_to_email=email,
                    )
                    sent_count += 1
                    
                except Exception:
                    pass  # No bloquear por fallos individuales
            
            messages.success(request, f'Link enviado a {sent_count} email(s).')
            return redirect('dashboard:online_links', module_slug=module_slug)
    else:
        form = ShareLinkForm()
    
    return render(request, 'dashboard/share_link.html', {
        'module': module,
        'link': link,
        'form': form,
    })
```

---

#### 5. `apps/dashboard/urls.py` (REEMPLAZAR COMPLETO)

```python
# apps/dashboard/urls.py
# ============================================================================
# COMMIT 15-24: URLs del dashboard de profesionales
# ============================================================================

from django.urls import path, include
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('capacitaciones/', views.capacitaciones_menu, name='capacitaciones_menu'),
    path('capacitaciones/<slug:module_slug>/', views.modalidad_selector, name='modalidad_selector'),
    path('capacitaciones/<slug:module_slug>/links/', views.online_links, name='online_links'),
    path('capacitaciones/<slug:module_slug>/links/generar/', views.generate_link, name='generate_link'),
    path('capacitaciones/<slug:module_slug>/links/<uuid:link_id>/compartir/', views.share_link, name='share_link'),
    path('presencial/', include('apps.presencial.urls')),
    path('perfil/', views.profile, name='profile'),
]
```

---

#### 6. `templates/dashboard/share_link.html` (CREAR)

```html
{% extends "base_dashboard.html" %}
{% load django_bootstrap5 %}

{% block title %}Compartir Link - ErgoSolutions{% endblock %}

{% block content %}
<div class="container-fluid py-4 px-4">
    
    <nav aria-label="breadcrumb" class="mb-3">
        <ol class="breadcrumb breadcrumb-dark">
            <li class="breadcrumb-item"><a href="{% url 'dashboard:home' %}">Dashboard</a></li>
            <li class="breadcrumb-item"><a href="{% url 'dashboard:capacitaciones_menu' %}">Capacitaciones</a></li>
            <li class="breadcrumb-item">
                <a href="{% url 'dashboard:online_links' module.slug %}">{{ module.title }}</a>
            </li>
            <li class="breadcrumb-item active">Compartir</li>
        </ol>
    </nav>

    <div class="row justify-content-center">
        <div class="col-lg-8">
            <div class="card bg-dark border-secondary">
                <div class="card-header border-secondary">
                    <h4 class="mb-0 text-white">
                        <i class="bi bi-envelope me-2 text-warning"></i>Compartir por Email
                    </h4>
                </div>
                <div class="card-body p-4">
                    <div class="alert alert-info border-info small mb-4">
                        <i class="bi bi-link-45deg me-2"></i>
                        <strong>Link:</strong> 
                        <code>{{ request.scheme }}://{{ request.get_host }}{{ link.get_absolute_url }}</code>
                        {% if link.label %}<br><strong>Etiqueta:</strong> {{ link.label }}{% endif %}
                    </div>

                    <form method="post" novalidate>
                        {% csrf_token %}
                        
                        <div class="mb-3">
                            <label class="form-label text-light">{{ form.emails.label }}</label>
                            {{ form.emails }}
                            {% if form.emails.errors %}
                                <div class="text-danger small mt-1">{{ form.emails.errors.0 }}</div>
                            {% endif %}
                            <small class="form-text text-muted">{{ form.emails.help_text }}</small>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label text-light">{{ form.message.label }}</label>
                            {{ form.message }}
                        </div>
                        
                        <div class="d-flex gap-3">
                            <button type="submit" class="btn btn-warning">
                                <i class="bi bi-send me-2"></i>Enviar
                            </button>
                            <a href="{% url 'dashboard:online_links' module.slug %}" class="btn btn-outline-secondary">
                                Cancelar
                            </a>
                        </div>
                    </form>
                </div>
            </div>

            <!-- Historial de envíos de este link -->
            {% if link.share_logs.count > 0 %}
            <div class="card bg-dark border-secondary mt-4">
                <div class="card-header border-secondary">
                    <h5 class="mb-0 text-secondary">
                        <i class="bi bi-clock-history me-2"></i>Envíos anteriores
                    </h5>
                </div>
                <div class="card-body p-0">
                    <ul class="list-group list-group-flush">
                        {% for log in link.share_logs.all %}
                        <li class="list-group-item bg-dark text-light border-secondary">
                            <i class="bi bi-envelope-check text-success me-2"></i>
                            {{ log.shared_to_email }}
                            <small class="text-muted ms-2">{{ log.shared_at|date:"d/m/Y H:i" }}</small>
                        </li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
            {% endif %}

        </div>
    </div>

</div>
{% endblock %}
```

---

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 24: Compartir links de capacitación por email

- Formulario ShareLinkForm con soporte múltiples emails
- Envío de email con link y mensaje personalizado
- Modelo LinkShareLog para registro de envíos
- Vista de historial de envíos por link
- Validación de emails
- Migración de base de datos"
```

---

## COMMIT 25: Rutas públicas /c/<slug>/ para trabajadores

### 📋 Descripción
Crear rutas de acceso público para trabajadores vía links compartidos. Mantiene la lógica actual de registro/login de trainees, pero accesible desde `/c/<slug>/`.

### 📁 Archivos a crear/modificar

---

#### 1. `apps/training/views_public.py` (CREAR)

```python
# apps/training/views_public.py
# ============================================================================
# COMMIT 25: Vistas públicas para acceso vía link compartido
# ============================================================================

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required

from .models import TrainingModule, CapacitacionLink


def public_landing(request, module_slug):
    """
    Landing de capacitación accedida vía link compartido.
    - Si tiene parámetro ref, trackea el acceso
    - Si el usuario no está logueado, redirige al registro/login de trainees
    - Si está logueado, redirige a la página de capacitación
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    
    # Tracking del parámetro ref
    ref_id = request.GET.get('ref')
    if ref_id:
        try:
            link = CapacitacionLink.objects.get(id=ref_id, module=module)
            if link.is_usable:
                # Incrementar contador de accesos
                CapacitacionLink.objects.filter(id=ref_id).update(
                    access_count=models.F('access_count') + 1
                )
                # Guardar ref en sesión para seguimiento posterior
                request.session['capacitacion_ref'] = str(ref_id)
        except (CapacitacionLink.DoesNotExist, ValueError):
            pass  # ref inválido, continuar sin tracking
    
    # Si el usuario ya está logueado como trainee, ir directo a capacitación
    if request.user.is_authenticated and hasattr(request.user, 'is_trainee') and request.user.is_trainee:
        return redirect('training_home')
    
    # Redirigir al flujo de registro/login de trainees
    # Guardamos el módulo en sesión para después del login
    request.session['target_module_slug'] = module_slug
    return redirect('trainee_landing')
```

> **NOTA:** Agregar `from django.db import models` al inicio si no está importado.

---

#### 2. `apps/training/urls_public.py` (CREAR)

```python
# apps/training/urls_public.py
# ============================================================================
# COMMIT 25: URLs públicas para acceso vía link compartido
# ============================================================================

from django.urls import path
from . import views_public

urlpatterns = [
    path('<slug:module_slug>/', views_public.public_landing, name='training_public'),
]
```

---

#### 3. `config/urls.py` (REEMPLAZAR COMPLETO)

```python
# config/urls.py
# ============================================================================
# COMMIT 25: URLs completas de ErgoSolutions
# ============================================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # =========================================================================
    # Admin
    # =========================================================================
    path("admin/", admin.site.urls),
    
    # =========================================================================
    # Landing Principal (ErgoSolutions) — Commit 12
    # =========================================================================
    path('', include('apps.landing.urls', namespace='landing')),
    
    # =========================================================================
    # Autenticación de Profesionales — Commit 13-14
    # =========================================================================
    path('auth/', include('apps.accounts.urls_professional')),
    
    # =========================================================================
    # Dashboard de Profesionales — Commit 15+
    # Incluye presencial y gestión de links
    # =========================================================================
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    
    # =========================================================================
    # Área de Capacitaciones - ACCESO VÍA LINK — Commit 25
    # URL corta para links compartibles: /c/<slug>/
    # =========================================================================
    path('c/', include('apps.training.urls_public')),
    
    # =========================================================================
    # Autenticación de Trainees (registro/login) — /acceso/
    # =========================================================================
    path('acceso/', include('apps.accounts.urls')),
    
    # =========================================================================
    # Área de Capacitaciones - TRABAJADORES (sistema existente)
    # =========================================================================
    path("capacitacion/", include("apps.training.urls")),
    
    # =========================================================================
    # Quiz
    # =========================================================================
    path("quiz/", include("apps.quiz.urls")),
    
    # =========================================================================
    # Certificados
    # =========================================================================
    path("certificados/", include("apps.certificates.urls")),
    
    # =========================================================================
    # Chatbot IA (Ergobot)
    # =========================================================================
    path("ai/", include("apps.ergobot_ai.urls")),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

#### 4. Actualizar stats del dashboard

En `apps/dashboard/views.py`, actualizar la vista `home`:

```python
@login_required
@professional_required
def home(request):
    """Dashboard principal del profesional con stats actualizadas."""
    
    presencial_count = PresencialSession.objects.filter(
        professional=request.user
    ).count()
    
    links_count = CapacitacionLink.objects.filter(
        created_by=request.user
    ).count()
    
    total_accesses = CapacitacionLink.objects.filter(
        created_by=request.user
    ).aggregate(total=models.Sum('access_count'))['total'] or 0
    
    stats = {
        'capacitaciones_total': presencial_count,
        'links_generados': links_count,
        'trabajadores_capacitados': total_accesses,
    }
    
    return render(request, 'dashboard/home.html', {
        'stats': stats,
    })
```

> **NOTA:** Agregar `from django.db import models` al inicio de `dashboard/views.py` si no está.

---

### ✅ Verificación del Commit 25
- [ ] `/c/ergonomia/?ref=<uuid>` redirige al registro/login de trainees
- [ ] El contador de accesos se incrementa correctamente
- [ ] Si el trainee ya está logueado, va directo a la capacitación
- [ ] Las URLs cortas funcionan con y sin parámetro ref
- [ ] Stats del dashboard actualizadas

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 25: Rutas públicas /c/<slug>/ para trabajadores

- URL corta /c/<slug>/ para acceso vía link
- Tracking de parámetro ref (CapacitacionLink)
- Incremento de contador de accesos (F expression)
- Redirección al flujo de registro/login de trainees
- config/urls.py actualizado con ruta /c/
- Stats del dashboard actualizadas (links + accesos)"
```

---

# ═══════════════════════════════════════════════════════════════════════════
# FASE 6: MEJORAS, TESTING Y PULIDO
# ═══════════════════════════════════════════════════════════════════════════

## COMMIT 26: Panel de perfil del profesional

### 📋 Descripción
Completar el panel de perfil del profesional con edición de datos, cambio de contraseña, y estadísticas.

### 📁 Archivos a crear/modificar

---

#### 1. `apps/dashboard/forms.py` (AGREGAR al final)

```python
# ============================================================================
# COMMIT 26: Formularios de perfil profesional
# ============================================================================

from django.contrib.auth import get_user_model

User = get_user_model()


class ProfessionalProfileForm(forms.Form):
    """Formulario de edición de perfil del profesional."""
    
    first_name = forms.CharField(
        label='Nombre', max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control bg-black text-light border-secondary'})
    )
    last_name = forms.CharField(
        label='Apellido', max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control bg-black text-light border-secondary'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control bg-black text-light border-secondary'})
    )
    profession = forms.CharField(
        label='Profesión', max_length=100, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control bg-black text-light border-secondary'})
    )
    license_number = forms.CharField(
        label='Matrícula', max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control bg-black text-light border-secondary'})
    )
    dni = forms.CharField(
        label='DNI', max_length=15, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control bg-black text-light border-secondary'})
    )
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['profession'].initial = user.profession
            self.fields['license_number'].initial = user.license_number
            self.fields['dni'].initial = user.dni
    
    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if self.user and User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError('Este email ya está en uso por otro usuario.')
        return email


class ChangePasswordForm(forms.Form):
    """Formulario de cambio de contraseña."""
    
    current_password = forms.CharField(
        label='Contraseña actual',
        widget=forms.PasswordInput(attrs={'class': 'form-control bg-black text-light border-secondary'})
    )
    new_password1 = forms.CharField(
        label='Nueva contraseña', min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-control bg-black text-light border-secondary'})
    )
    new_password2 = forms.CharField(
        label='Confirmar nueva contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control bg-black text-light border-secondary'})
    )
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
    
    def clean_current_password(self):
        password = self.cleaned_data.get('current_password')
        if self.user and not self.user.check_password(password):
            raise forms.ValidationError('La contraseña actual es incorrecta.')
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password1')
        p2 = cleaned_data.get('new_password2')
        if p1 and p2 and p1 != p2:
            self.add_error('new_password2', 'Las contraseñas no coinciden.')
        return cleaned_data
```

---

#### 2. `apps/dashboard/views.py` — REEMPLAZAR vista `profile`

```python
from .forms import ShareLinkForm, ProfessionalProfileForm, ChangePasswordForm


@login_required
@professional_required
def profile(request):
    """Perfil del profesional con edición y stats."""
    user = request.user
    
    profile_form = ProfessionalProfileForm(user=user)
    password_form = ChangePasswordForm(user=user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            profile_form = ProfessionalProfileForm(request.POST, user=user)
            if profile_form.is_valid():
                user.first_name = profile_form.cleaned_data['first_name']
                user.last_name = profile_form.cleaned_data['last_name']
                user.email = profile_form.cleaned_data['email']
                user.profession = profile_form.cleaned_data.get('profession', '')
                user.license_number = profile_form.cleaned_data.get('license_number', '')
                user.dni = profile_form.cleaned_data.get('dni', '')
                user.save()
                messages.success(request, 'Perfil actualizado correctamente.')
                return redirect('dashboard:profile')
        
        elif action == 'change_password':
            password_form = ChangePasswordForm(request.POST, user=user)
            if password_form.is_valid():
                user.set_password(password_form.cleaned_data['new_password1'])
                user.save()
                # Re-autenticar para no cerrar sesión
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)
                messages.success(request, 'Contraseña actualizada correctamente.')
                return redirect('dashboard:profile')
    
    # Stats
    presencial_count = PresencialSession.objects.filter(professional=user).count()
    links_count = CapacitacionLink.objects.filter(created_by=user).count()
    shares_count = LinkShareLog.objects.filter(link__created_by=user).count()
    
    return render(request, 'dashboard/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'stats': {
            'presencial': presencial_count,
            'links': links_count,
            'shares': shares_count,
        },
    })
```

> **NOTA:** Importar `LinkShareLog`: `from apps.training.models import CapacitacionLink, LinkShareLog`

---

#### 3. `templates/dashboard/profile.html` (REEMPLAZAR COMPLETO)

```html
{% extends "base_dashboard.html" %}

{% block title %}Mi Perfil - ErgoSolutions{% endblock %}

{% block content %}
<div class="container-fluid py-4 px-4">
    
    <nav aria-label="breadcrumb" class="mb-3">
        <ol class="breadcrumb breadcrumb-dark">
            <li class="breadcrumb-item"><a href="{% url 'dashboard:home' %}">Dashboard</a></li>
            <li class="breadcrumb-item active">Mi Perfil</li>
        </ol>
    </nav>

    <h2 class="fw-bold mb-4">
        <i class="bi bi-person-circle me-2 text-primary"></i>Mi Perfil
    </h2>

    <div class="row g-4">
        <!-- Datos personales -->
        <div class="col-lg-8">
            <div class="card bg-dark border-secondary mb-4">
                <div class="card-header border-secondary">
                    <h5 class="mb-0 text-white">
                        <i class="bi bi-pencil me-2"></i>Datos Personales
                    </h5>
                </div>
                <div class="card-body p-4">
                    <form method="post">
                        {% csrf_token %}
                        <input type="hidden" name="action" value="update_profile">
                        
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label text-secondary">{{ profile_form.first_name.label }}</label>
                                {{ profile_form.first_name }}
                                {% if profile_form.first_name.errors %}
                                    <div class="text-danger small">{{ profile_form.first_name.errors.0 }}</div>
                                {% endif %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-secondary">{{ profile_form.last_name.label }}</label>
                                {{ profile_form.last_name }}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-secondary">{{ profile_form.email.label }}</label>
                                {{ profile_form.email }}
                                {% if profile_form.email.errors %}
                                    <div class="text-danger small">{{ profile_form.email.errors.0 }}</div>
                                {% endif %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-secondary">{{ profile_form.dni.label }}</label>
                                {{ profile_form.dni }}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-secondary">{{ profile_form.profession.label }}</label>
                                {{ profile_form.profession }}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-secondary">{{ profile_form.license_number.label }}</label>
                                {{ profile_form.license_number }}
                            </div>
                        </div>
                        
                        <div class="mt-4">
                            <button type="submit" class="btn btn-primary">
                                <i class="bi bi-check-lg me-2"></i>Guardar cambios
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <!-- Cambio de contraseña -->
            <div class="card bg-dark border-secondary">
                <div class="card-header border-secondary">
                    <h5 class="mb-0 text-white">
                        <i class="bi bi-lock me-2"></i>Cambiar Contraseña
                    </h5>
                </div>
                <div class="card-body p-4">
                    <form method="post">
                        {% csrf_token %}
                        <input type="hidden" name="action" value="change_password">
                        
                        <div class="row g-3">
                            <div class="col-12">
                                <label class="form-label text-secondary">{{ password_form.current_password.label }}</label>
                                {{ password_form.current_password }}
                                {% if password_form.current_password.errors %}
                                    <div class="text-danger small">{{ password_form.current_password.errors.0 }}</div>
                                {% endif %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-secondary">{{ password_form.new_password1.label }}</label>
                                {{ password_form.new_password1 }}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label text-secondary">{{ password_form.new_password2.label }}</label>
                                {{ password_form.new_password2 }}
                                {% if password_form.new_password2.errors %}
                                    <div class="text-danger small">{{ password_form.new_password2.errors.0 }}</div>
                                {% endif %}
                            </div>
                        </div>
                        
                        <div class="mt-4">
                            <button type="submit" class="btn btn-warning">
                                <i class="bi bi-lock me-2"></i>Cambiar contraseña
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <!-- Sidebar: Stats -->
        <div class="col-lg-4">
            <div class="card bg-dark border-secondary mb-4">
                <div class="card-header border-secondary">
                    <h5 class="mb-0 text-white">
                        <i class="bi bi-bar-chart me-2"></i>Estadísticas
                    </h5>
                </div>
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-3 pb-3 border-bottom border-secondary">
                        <span class="text-secondary">Sesiones presenciales</span>
                        <span class="badge bg-warning fs-6">{{ stats.presencial }}</span>
                    </div>
                    <div class="d-flex justify-content-between align-items-center mb-3 pb-3 border-bottom border-secondary">
                        <span class="text-secondary">Links generados</span>
                        <span class="badge bg-info fs-6">{{ stats.links }}</span>
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="text-secondary">Emails enviados</span>
                        <span class="badge bg-success fs-6">{{ stats.shares }}</span>
                    </div>
                </div>
            </div>

            <div class="card bg-dark border-secondary">
                <div class="card-header border-secondary">
                    <h5 class="mb-0 text-white">
                        <i class="bi bi-credit-card me-2"></i>Suscripción
                    </h5>
                </div>
                <div class="card-body">
                    <p class="text-secondary mb-2">Plan actual:</p>
                    <span class="badge bg-success fs-6 mb-3">
                        {{ request.user.get_subscription_tier_display|default:"Gratuito" }}
                    </span>
                    <p class="text-muted small mb-0">
                        Los planes de suscripción estarán disponibles próximamente.
                    </p>
                </div>
            </div>
        </div>
    </div>

</div>
{% endblock %}
```

---

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 26: Panel de perfil del profesional

- Vista de perfil completa con datos personales
- Formulario de edición (nombre, email, profesión, matrícula, DNI)
- Cambio de contraseña con validación
- Estadísticas: sesiones presenciales, links, emails enviados
- Información de suscripción (preparado para futuro)
- Mantiene sesión activa después de cambio de contraseña"
```

---

## COMMIT 27: Agregar capacitaciones adicionales (datos)

### 📋 Descripción
Crear fixture con datos de capacitaciones adicionales como placeholders.

### 📁 Archivos a crear

---

#### 1. `apps/training/fixtures/training_modules.json` (CREAR)

```json
[
    {
        "model": "training.trainingmodule",
        "fields": {
            "slug": "ergonomia",
            "title": "Ergonomía y Prevención de Riesgos",
            "description": "Capacitación sobre factores de riesgo ergonómicos en puestos de trabajo. Incluye video, asistente IA y evaluación con certificación.",
            "youtube_id": "IIgZp_NbsAE",
            "icon": "bi-body-text",
            "color": "#28a745",
            "order": 1,
            "is_active": true,
            "intro_md": "",
            "material_md": "",
            "transcript_md": ""
        }
    },
    {
        "model": "training.trainingmodule",
        "fields": {
            "slug": "riesgo-electrico",
            "title": "Riesgo Eléctrico",
            "description": "Prevención de accidentes por contacto eléctrico directo e indirecto. Normas de seguridad y procedimientos de bloqueo/etiquetado.",
            "youtube_id": "",
            "icon": "bi-lightning-charge",
            "color": "#ffc107",
            "order": 2,
            "is_active": false,
            "intro_md": "",
            "material_md": "",
            "transcript_md": ""
        }
    },
    {
        "model": "training.trainingmodule",
        "fields": {
            "slug": "trabajo-en-altura",
            "title": "Trabajo en Altura",
            "description": "Medidas de prevención para tareas en altura. Uso de arnés, líneas de vida y sistemas de protección contra caídas.",
            "youtube_id": "",
            "icon": "bi-building-up",
            "color": "#17a2b8",
            "order": 3,
            "is_active": false,
            "intro_md": "",
            "material_md": "",
            "transcript_md": ""
        }
    },
    {
        "model": "training.trainingmodule",
        "fields": {
            "slug": "prevencion-incendios",
            "title": "Prevención de Incendios",
            "description": "Prevención, detección y combate de incendios. Uso de extintores, evacuación y plan de emergencia.",
            "youtube_id": "",
            "icon": "bi-fire",
            "color": "#dc3545",
            "order": 4,
            "is_active": false,
            "intro_md": "",
            "material_md": "",
            "transcript_md": ""
        }
    },
    {
        "model": "training.trainingmodule",
        "fields": {
            "slug": "elementos-proteccion-personal",
            "title": "Elementos de Protección Personal",
            "description": "Selección, uso correcto y mantenimiento de EPP según el tipo de riesgo laboral.",
            "youtube_id": "",
            "icon": "bi-shield-check",
            "color": "#6f42c1",
            "order": 5,
            "is_active": false,
            "intro_md": "",
            "material_md": "",
            "transcript_md": ""
        }
    }
]
```

---

#### 2. Cargar fixture

```bash
python manage.py loaddata apps/training/fixtures/training_modules.json
```

> **NOTA:** Si el módulo de ergonomía ya existe, la fixture puede dar error por duplicado de slug. En ese caso, quitar el primer objeto del JSON y cargarlo sin el de ergonomía. Alternativamente usar un management command:

#### 3. `apps/training/management/commands/seed_modules.py` (CREAR — alternativa)

```python
# apps/training/management/commands/seed_modules.py
# ============================================================================
# COMMIT 27: Seed de módulos de capacitación adicionales
# ============================================================================

from django.core.management.base import BaseCommand
from apps.training.models import TrainingModule


MODULES = [
    {
        'slug': 'riesgo-electrico',
        'title': 'Riesgo Eléctrico',
        'description': 'Prevención de accidentes por contacto eléctrico directo e indirecto. Normas de seguridad y procedimientos de bloqueo/etiquetado.',
        'youtube_id': '',
        'icon': 'bi-lightning-charge',
        'color': '#ffc107',
        'order': 2,
        'is_active': False,
    },
    {
        'slug': 'trabajo-en-altura',
        'title': 'Trabajo en Altura',
        'description': 'Medidas de prevención para tareas en altura. Uso de arnés, líneas de vida y sistemas de protección contra caídas.',
        'youtube_id': '',
        'icon': 'bi-building-up',
        'color': '#17a2b8',
        'order': 3,
        'is_active': False,
    },
    {
        'slug': 'prevencion-incendios',
        'title': 'Prevención de Incendios',
        'description': 'Prevención, detección y combate de incendios. Uso de extintores, evacuación y plan de emergencia.',
        'youtube_id': '',
        'icon': 'bi-fire',
        'color': '#dc3545',
        'order': 4,
        'is_active': False,
    },
    {
        'slug': 'elementos-proteccion-personal',
        'title': 'Elementos de Protección Personal',
        'description': 'Selección, uso correcto y mantenimiento de EPP según el tipo de riesgo laboral.',
        'youtube_id': '',
        'icon': 'bi-shield-check',
        'color': '#6f42c1',
        'order': 5,
        'is_active': False,
    },
]


class Command(BaseCommand):
    help = 'Crea módulos de capacitación adicionales (placeholders)'
    
    def handle(self, *args, **options):
        created = 0
        for data in MODULES:
            obj, was_created = TrainingModule.objects.get_or_create(
                slug=data['slug'],
                defaults=data,
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'  ✅ Creado: {obj.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠️ Ya existe: {obj.title}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nTotal creados: {created}'))
```

```bash
# Crear directorio si no existe
mkdir -p apps/training/management/commands

# Crear __init__.py en management y commands
touch apps/training/management/__init__.py
touch apps/training/management/commands/__init__.py

# Ejecutar
python manage.py seed_modules
```

---

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 27: Datos de capacitaciones adicionales (placeholders)

- Módulo Riesgo Eléctrico (is_active=False)
- Módulo Trabajo en Altura (is_active=False)
- Módulo Prevención de Incendios (is_active=False)
- Módulo Elementos de Protección Personal (is_active=False)
- Íconos y colores configurados para cada módulo
- Fixture JSON para carga de datos
- Management command seed_modules como alternativa"
```

---

## COMMIT 28: Testing, documentación y correcciones finales

### 📋 Descripción
Tests de flujos principales, README actualizado, y correcciones finales.

### 📁 Archivos a crear/modificar

---

#### 1. `apps/accounts/tests.py` (REEMPLAZAR COMPLETO)

```python
# apps/accounts/tests.py
# ============================================================================
# COMMIT 28: Tests de autenticación dual
# ============================================================================

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class TraineeAuthTests(TestCase):
    """Tests de autenticación de trabajadores (trainees)."""
    
    def setUp(self):
        self.client = Client()
        self.trainee = User.objects.create_trainee(
            cuil='20123456789',
            email='trainee@test.com',
            full_name='Test Trainee',
        )
    
    def test_trainee_login_with_cuil_email(self):
        """Login de trainee con CUIL y email."""
        response = self.client.post(reverse('login_post'), {
            'cuil': '20123456789',
            'email': 'trainee@test.com',
        })
        self.assertEqual(response.status_code, 302)
    
    def test_trainee_cannot_access_dashboard(self):
        """Trainee no puede acceder al dashboard de profesionales."""
        self.client.force_login(self.trainee)
        response = self.client.get(reverse('dashboard:home'))
        # Debería redirigir o devolver 403
        self.assertIn(response.status_code, [302, 403])


class ProfessionalAuthTests(TestCase):
    """Tests de autenticación de profesionales."""
    
    def setUp(self):
        self.client = Client()
        self.professional = User.objects.create_professional(
            email='pro@test.com',
            password='testpass123',
            username='prouser',
            first_name='Test',
            last_name='Professional',
        )
    
    def test_professional_login(self):
        """Login de profesional con username y password."""
        response = self.client.post(reverse('professional_login'), {
            'username': 'prouser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)
    
    def test_professional_login_with_email(self):
        """Login de profesional con email y password."""
        response = self.client.post(reverse('professional_login'), {
            'username': 'pro@test.com',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)
    
    def test_professional_can_access_dashboard(self):
        """Profesional puede acceder al dashboard."""
        self.client.force_login(self.professional)
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
    
    def test_professional_register(self):
        """Registro de nuevo profesional."""
        response = self.client.post(reverse('professional_register'), {
            'first_name': 'Nuevo',
            'last_name': 'Pro',
            'dni': '30123456',
            'email': 'nuevo@test.com',
            'profession': 'Lic. en Higiene y Seguridad',
            'license_number': 'MN 99999',
            'username': 'nuevopro',
            'password1': 'securepass123',
            'password2': 'securepass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='nuevopro').exists())
```

---

#### 2. `apps/dashboard/tests.py` (CREAR)

```python
# apps/dashboard/tests.py
# ============================================================================
# COMMIT 28: Tests del dashboard y flujos de capacitaciones
# ============================================================================

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.training.models import TrainingModule, CapacitacionLink

User = get_user_model()


class DashboardTests(TestCase):
    """Tests del dashboard de profesionales."""
    
    def setUp(self):
        self.client = Client()
        self.professional = User.objects.create_professional(
            email='pro@test.com',
            password='testpass123',
            username='prouser',
            first_name='Test',
            last_name='Pro',
        )
        self.module = TrainingModule.objects.create(
            slug='test-module',
            title='Módulo de Test',
            youtube_id='test123',
            is_active=True,
            icon='bi-book',
            color='#28a745',
            order=1,
        )
    
    def test_dashboard_home(self):
        """Dashboard muestra correctamente."""
        self.client.force_login(self.professional)
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Capacitaciones')
    
    def test_capacitaciones_menu(self):
        """Menú de capacitaciones lista los módulos."""
        self.client.force_login(self.professional)
        response = self.client.get(reverse('dashboard:capacitaciones_menu'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Módulo de Test')
    
    def test_modalidad_selector(self):
        """Selector de modalidad muestra presencial y online."""
        self.client.force_login(self.professional)
        response = self.client.get(
            reverse('dashboard:modalidad_selector', args=['test-module'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Presencial')
        self.assertContains(response, 'Online')
    
    def test_generate_link(self):
        """Generación de link de capacitación."""
        self.client.force_login(self.professional)
        response = self.client.post(
            reverse('dashboard:generate_link', args=['test-module']),
            {'label': 'Test Link'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CapacitacionLink.objects.filter(label='Test Link').exists())
    
    def test_online_links_list(self):
        """Lista de links muestra links creados."""
        self.client.force_login(self.professional)
        CapacitacionLink.objects.create(
            module=self.module,
            created_by=self.professional,
            label='Mi Link',
        )
        response = self.client.get(
            reverse('dashboard:online_links', args=['test-module'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mi Link')


class PublicLinkTests(TestCase):
    """Tests de acceso público vía links."""
    
    def setUp(self):
        self.client = Client()
        self.professional = User.objects.create_professional(
            email='pro@test.com',
            password='testpass123',
            username='prouser',
        )
        self.module = TrainingModule.objects.create(
            slug='test-module',
            title='Módulo de Test',
            youtube_id='test123',
            is_active=True,
        )
        self.link = CapacitacionLink.objects.create(
            module=self.module,
            created_by=self.professional,
        )
    
    def test_public_link_redirects(self):
        """Link público redirige al login de trainees."""
        url = f"/c/test-module/?ref={self.link.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
    
    def test_public_link_increments_counter(self):
        """Link público incrementa el contador de accesos."""
        url = f"/c/test-module/?ref={self.link.id}"
        self.client.get(url)
        self.link.refresh_from_db()
        self.assertEqual(self.link.access_count, 1)
```

---

#### 3. `apps/presencial/tests.py` (CREAR)

```python
# apps/presencial/tests.py
# ============================================================================
# COMMIT 28: Tests de modo presencial
# ============================================================================

import json

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.training.models import TrainingModule
from apps.quiz.models import Question, Choice

User = get_user_model()


class PresencialTests(TestCase):
    """Tests de capacitación presencial."""
    
    def setUp(self):
        self.client = Client()
        self.professional = User.objects.create_professional(
            email='pro@test.com',
            password='testpass123',
            username='prouser',
        )
        self.module = TrainingModule.objects.create(
            slug='test-module',
            title='Módulo de Test',
            youtube_id='test123',
            is_active=True,
        )
    
    def test_capacitacion_page(self):
        """Página de capacitación presencial carga correctamente."""
        self.client.force_login(self.professional)
        response = self.client.get(
            reverse('presencial:capacitacion', args=['test-module'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Presencial')
    
    def test_quiz_presencial_page(self):
        """Página del quiz presencial carga correctamente."""
        self.client.force_login(self.professional)
        response = self.client.get(
            reverse('presencial:quiz', args=['test-module'])
        )
        self.assertEqual(response.status_code, 200)
    
    def test_planilla_pdf_download(self):
        """Descarga de planilla PDF."""
        self.client.force_login(self.professional)
        response = self.client.get(
            reverse('presencial:planilla_pdf', args=['test-module'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
```

---

#### 4. `README.md` (CREAR/REEMPLAZAR en la raíz del proyecto)

```markdown
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
```

---

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 28: Testing, documentación y correcciones - MVP completo

- Tests de autenticación dual (trainee + profesional)
- Tests de flujo de capacitaciones (dashboard, menú, modalidad)
- Tests de generación de links y acceso público
- Tests de modo presencial (capacitación, quiz, planilla)
- README actualizado con instrucciones completas
- Estructura de URLs documentada
- MVP de ErgoSolutions completo"
```

---

# ═══════════════════════════════════════════════════════════════════════════
# RESUMEN FINAL — FASES 3 A 6
# ═══════════════════════════════════════════════════════════════════════════

## Progreso Total

| Fase | Commits | Descripción | Archivos nuevos clave |
|------|---------|-------------|-----------------------|
| **3. Dashboard + Menú** | 15-17 | Dashboard, menú capacitaciones, selector modalidad | `base_dashboard.html`, `dashboard.css`, `capacitaciones_menu.html`, `modalidad_selector.html` |
| **4. Modo Presencial** | 18-21 | Capacitación presencial, quiz simplificado, PDF planilla, historial | App `presencial/`, `pdf.py`, `PresencialSession` |
| **5. Modo Online** | 22-25 | Links compartibles, copia, email, rutas públicas | `CapacitacionLink`, `LinkShareLog`, `urls_public.py` |
| **6. Mejoras + Testing** | 26-28 | Perfil, datos adicionales, tests, README | `profile.html`, `tests.py`, `README.md` |

## Apps creadas

| App | Commit | Propósito |
|-----|--------|-----------|
| `apps.presencial` | 18 | Capacitación presencial (video, quiz, planilla, historial) |

## Modelos nuevos

| Modelo | App | Commit |
|--------|-----|--------|
| `PresencialSession` | `presencial` | 21 |
| `CapacitacionLink` | `training` | 22 |
| `LinkShareLog` | `training` | 24 |

## Campos nuevos en modelos existentes

| Modelo | Campo | Commit |
|--------|-------|--------|
| `TrainingModule` | `description` | 16 |
| `TrainingModule` | `icon` | 16 |
| `TrainingModule` | `color` | 16 |
| `TrainingModule` | `order` | 16 |

## Migraciones necesarias

```bash
# Commit 16
python manage.py makemigrations training --name add_icon_color_order_description
python manage.py migrate

# Commit 21
python manage.py makemigrations presencial --name create_presencial_session
python manage.py migrate

# Commit 22
python manage.py makemigrations training --name add_capacitacion_link
python manage.py migrate

# Commit 24
python manage.py makemigrations training --name add_link_share_log
python manage.py migrate
```

## Árbol final de URLs (Post Commit 28)

```
/                                    → Landing institucional
/auth/registro/                      → Registro profesional
/auth/login/                         → Login profesional
/auth/logout/                        → Logout profesional
/dashboard/                          → Dashboard principal
/dashboard/capacitaciones/           → Menú de capacitaciones
/dashboard/capacitaciones/<slug>/    → Selector de modalidad
/dashboard/capacitaciones/<slug>/links/           → Gestión de links online
/dashboard/capacitaciones/<slug>/links/generar/   → Generar nuevo link
/dashboard/capacitaciones/<slug>/links/<uuid>/compartir/ → Compartir por email
/dashboard/presencial/<slug>/        → Capacitación presencial
/dashboard/presencial/<slug>/quiz/   → Quiz presencial
/dashboard/presencial/<slug>/quiz/submit/ → Submit quiz presencial
/dashboard/presencial/<slug>/planilla/    → Planilla PDF
/dashboard/presencial/historial/     → Historial presencial
/dashboard/perfil/                   → Perfil profesional
/c/<slug>/                           → Acceso público vía link
/acceso/                             → Landing trainees
/capacitacion/                       → Página de capacitación (trainees)
/quiz/                               → Quiz (trainees)
/certificados/                       → Certificados
/ai/                                 → Chat Ergobot (SSE)
/admin/                              → Admin
```

---

*Documento generado para ErgoSolutions*  
*Fases 3–6 | Commits 15–28*  
*Fecha: Febrero 2026*
