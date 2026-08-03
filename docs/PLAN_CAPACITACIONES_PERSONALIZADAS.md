# 📋 ERGOSOLUTIONS — PLAN: CAPACITACIONES PERSONALIZADAS

## Documento de Referencia para Implementación

**Proyecto:** ErgoSolutions  
**Estado actual:** Commit 28 completado (Etapa 2 finalizada)  
**Feature:** Capacitaciones Personalizadas (visibles solo para profesionales asignados)  
**Fecha de creación:** 27 de Febrero 2026  
**Commits planificados:** 29 – 32

---

## 📌 RESUMEN EJECUTIVO

### Objetivo
Incorporar la posibilidad de crear **capacitaciones personalizadas** que solo sean visibles para los profesionales que las solicitaron. Cuando un profesional accede a `/dashboard/capacitaciones/`, debe ver las capacitaciones generales (visibles para todos) **más** sus capacitaciones particulares asignadas. El resto de los usuarios no verá esas capacitaciones personalizadas.

### Alcance
- Modificar el modelo `TrainingModule` para soportar capacitaciones personalizadas
- Crear una relación M2M entre `TrainingModule` y `CustomUser` para la asignación
- Modificar la vista `capacitaciones_menu` para filtrar por tipo
- Modificar el template `capacitaciones_menu.html` para mostrar ambas secciones
- Configurar el Admin de Django para gestionar asignaciones
- Crear un formulario para que los profesionales puedan solicitar capacitaciones personalizadas (opcional/futuro)

---

## 🔑 ÍNDICE DE COMMITS

| Commit | Descripción | Estado |
|--------|-------------|--------|
| **29** | Modelo: campos `is_personalized` + relación M2M `assigned_professionals` | ⬜ Pendiente |
| **30** | Vista + Template: separar capacitaciones generales y personalizadas | ⬜ Pendiente |
| **31** | Admin avanzado: gestión de asignaciones + formulario de solicitud | ⬜ Pendiente |
| **32** | Integración completa: modalidad selector + tests + verificación | ⬜ Pendiente |

---

## 📐 DISEÑO DE LA SOLUCIÓN

### Diagrama Conceptual

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    /dashboard/capacitaciones/                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  📚 CAPACITACIONES GENERALES (visibles para TODOS)               │  │
│  │                                                                   │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │  │
│  │  │Ergonomía │  │ Ruido    │  │ R.Eléct. │  │ T.Altura │         │  │
│  │  │✅ Activo │  │⏳ Próx.  │  │⏳ Próx.  │  │⏳ Próx.  │         │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  🔒 MIS CAPACITACIONES PERSONALIZADAS (solo para este usuario)   │  │
│  │                                                                   │  │
│  │  ┌──────────────────┐  ┌──────────────────┐                      │  │
│  │  │ Ergonomía - Emp.  │  │ Ruido Industrial │                      │  │
│  │  │ Acme S.A.         │  │ - Planta Norte   │                      │  │
│  │  │ ✅ Activo         │  │ ✅ Activo        │                      │  │
│  │  └──────────────────┘  └──────────────────┘                      │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Lógica de Visibilidad

```
REGLA DE VISIBILIDAD:

  Si TrainingModule.is_personalized == False:
      → VISIBLE para TODOS los profesionales (capacitación general)

  Si TrainingModule.is_personalized == True:
      → VISIBLE solo para los profesionales que están en assigned_professionals
      → INVISIBLE para el resto
```

### Modelo de Datos (cambios)

```
┌─────────────────────────────────────────────────────────────────────┐
│                     TrainingModule (ACTUALIZADO)                     │
├─────────────────────────────────────────────────────────────────────┤
│  (campos existentes sin cambios)                                    │
│  slug, title, description, youtube_id, intro_md, material_md,       │
│  transcript_md, is_active, icon, color, order, created_at,          │
│  updated_at                                                         │
│                                                                     │
│  ── NUEVOS CAMPOS ──────────────────────────────────────────────── │
│  is_personalized  : BooleanField (default=False)                    │
│  requested_by     : FK → CustomUser (null, blank) [quien solicitó]  │
│  assigned_professionals : M2M → CustomUser (blank) [quiénes ven]    │
│  company_name     : CharField (blank) [empresa asociada]            │
│  custom_notes     : TextField (blank) [notas internas]              │
└─────────────────────────────────────────────────────────────────────┘

                              │ M2M
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│             TrainingModuleAssignment (tabla intermedia)              │
│             (generada automáticamente por Django M2M)                │
├─────────────────────────────────────────────────────────────────────┤
│  trainingmodule_id  : FK → TrainingModule                           │
│  customuser_id      : FK → CustomUser                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

# ═══════════════════════════════════════════════════════════════════
# COMMIT 29: Modelo — Campos para Capacitaciones Personalizadas
# ═══════════════════════════════════════════════════════════════════

## 📋 Descripción
Agregar los campos necesarios al modelo `TrainingModule` para soportar capacitaciones personalizadas: un flag `is_personalized`, una FK al profesional que la solicitó, una relación M2M para asignar profesionales, y campos auxiliares.

## 🎯 Objetivos
- [ ] Agregar campo `is_personalized` (BooleanField, default=False)
- [ ] Agregar campo `requested_by` (FK a CustomUser, nullable)
- [ ] Agregar campo `assigned_professionals` (M2M a CustomUser)
- [ ] Agregar campo `company_name` (CharField, para identificar empresa)
- [ ] Agregar campo `custom_notes` (TextField, notas internas)
- [ ] Crear migración de base de datos
- [ ] Verificar que los módulos existentes no se vean afectados

## 📁 Archivos a modificar

---

### 1. `apps/training/models.py` (MODIFICAR)

**Agregar los siguientes campos al modelo `TrainingModule`**, justo antes de `created_at`:

```python
# apps/training/models.py
# ============================================================================
# COMMIT 29: Campos para capacitaciones personalizadas
# ============================================================================

from django.db import models
from django.conf import settings


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
        blank=True,
        default="",
        help_text="Solo el ID del video (ej: IIgZp_NbsAE), no la URL completa."
    )

    # Contenido en formato Markdown para la IA y el Front
    intro_md = models.TextField(blank=True, default="", verbose_name="Introducción (Markdown)")
    material_md = models.TextField(blank=True, default="", verbose_name="Material de lectura")
    transcript_md = models.TextField(blank=True, default="", verbose_name="Transcripción del video")

    is_active = models.BooleanField(default=False, verbose_name="¿Está activo?")

    # Campos de menú visual (Commit 16)
    icon = models.CharField(
        max_length=50,
        default='bi-book',
        help_text='Clase de Bootstrap Icons (ej: bi-body-text)'
    )
    color = models.CharField(
        max_length=20,
        default='#28a745',
        help_text='Color hex para el card'
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Orden en el menú'
    )

    # =========================================================================
    # ✅ COMMIT 29: Campos para capacitaciones personalizadas
    # =========================================================================
    is_personalized = models.BooleanField(
        default=False,
        verbose_name="¿Es personalizada?",
        help_text="Si es True, solo los profesionales asignados pueden ver esta capacitación."
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requested_trainings',
        verbose_name="Solicitada por",
        help_text="Profesional que solicitó esta capacitación personalizada."
    )
    assigned_professionals = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='personalized_trainings',
        verbose_name="Profesionales asignados",
        help_text="Profesionales que pueden ver y acceder a esta capacitación."
    )
    company_name_custom = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Empresa/Cliente",
        help_text="Nombre de la empresa o cliente para esta capacitación personalizada."
    )
    custom_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notas internas",
        help_text="Notas internas sobre esta capacitación (no visibles para los usuarios)."
    )
    # =========================================================================

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Módulo de capacitación"
        verbose_name_plural = "Módulos de capacitación"

    def __str__(self) -> str:
        prefix = "[PERSONALIZADA] " if self.is_personalized else ""
        return f"{prefix}{self.title} ({self.slug})"

    # =========================================================================
    # Managers personalizados para facilitar queries
    # =========================================================================
    @classmethod
    def get_general_modules(cls):
        """Retorna solo las capacitaciones generales (no personalizadas)."""
        return cls.objects.filter(is_personalized=False)

    @classmethod
    def get_personalized_for_user(cls, user):
        """Retorna las capacitaciones personalizadas asignadas a un usuario."""
        return cls.objects.filter(
            is_personalized=True,
            assigned_professionals=user,
        )

    @classmethod
    def get_all_for_user(cls, user):
        """
        Retorna TODAS las capacitaciones visibles para un usuario:
        - Generales (is_personalized=False)
        - Personalizadas asignadas a este usuario
        """
        from django.db.models import Q
        return cls.objects.filter(
            Q(is_personalized=False) |
            Q(is_personalized=True, assigned_professionals=user)
        ).distinct()
```

> **NOTA IMPORTANTE:** El campo `company_name_custom` usa un nombre diferente a `company_name` para evitar conflictos con otros campos que puedan existir en el futuro. Si prefiere usar `company_name`, verificar que no haya conflictos.

---

### 2. Crear migración

```bash
python manage.py makemigrations training --name add_personalized_training_fields
python manage.py migrate
```

**Migración esperada** (Django la generará automáticamente):

```python
# apps/training/migrations/0005_add_personalized_training_fields.py
# (Auto-generada por makemigrations)

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('training', '0004_add_link_share_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainingmodule',
            name='is_personalized',
            field=models.BooleanField(
                default=False,
                help_text='Si es True, solo los profesionales asignados pueden ver esta capacitación.',
                verbose_name='¿Es personalizada?'
            ),
        ),
        migrations.AddField(
            model_name='trainingmodule',
            name='requested_by',
            field=models.ForeignKey(
                blank=True,
                help_text='Profesional que solicitó esta capacitación personalizada.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='requested_trainings',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Solicitada por'
            ),
        ),
        migrations.AddField(
            model_name='trainingmodule',
            name='assigned_professionals',
            field=models.ManyToManyField(
                blank=True,
                help_text='Profesionales que pueden ver y acceder a esta capacitación.',
                related_name='personalized_trainings',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Profesionales asignados'
            ),
        ),
        migrations.AddField(
            model_name='trainingmodule',
            name='company_name_custom',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Nombre de la empresa o cliente para esta capacitación personalizada.',
                max_length=200,
                verbose_name='Empresa/Cliente'
            ),
        ),
        migrations.AddField(
            model_name='trainingmodule',
            name='custom_notes',
            field=models.TextField(
                blank=True,
                default='',
                help_text='Notas internas sobre esta capacitación (no visibles para los usuarios).',
                verbose_name='Notas internas'
            ),
        ),
    ]
```

---

### ✅ Verificación del Commit 29
- [ ] Migración creada y aplicada sin errores
- [ ] Los módulos existentes tienen `is_personalized=False` por defecto
- [ ] Se puede crear un TrainingModule con `is_personalized=True` desde el shell
- [ ] Los métodos `get_general_modules()`, `get_personalized_for_user()` y `get_all_for_user()` funcionan correctamente
- [ ] La relación M2M funciona (se puede asignar un profesional)
- [ ] Los módulos existentes siguen apareciendo normalmente

### 🧪 Test desde el shell

```bash
python manage.py shell -c "
from apps.training.models import TrainingModule
from django.contrib.auth import get_user_model

User = get_user_model()

# Verificar que los módulos existentes NO son personalizados
general = TrainingModule.get_general_modules()
print(f'Módulos generales: {general.count()}')
for m in general:
    print(f'  - {m.title} (is_personalized={m.is_personalized})')

# Crear un módulo personalizado de prueba
prof = User.objects.filter(user_type='professional').first()
if prof:
    test_mod, created = TrainingModule.objects.get_or_create(
        slug='test-personalizado',
        defaults={
            'title': 'Ergonomía - Empresa Test',
            'description': 'Capacitación personalizada de prueba',
            'is_personalized': True,
            'requested_by': prof,
            'is_active': True,
            'icon': 'bi-star',
            'color': '#e83e8c',
        }
    )
    if created:
        test_mod.assigned_professionals.add(prof)
        print(f'Módulo personalizado creado: {test_mod.title}')
    
    # Verificar visibilidad
    personalized = TrainingModule.get_personalized_for_user(prof)
    print(f'Módulos personalizados para {prof}: {personalized.count()}')
    
    all_modules = TrainingModule.get_all_for_user(prof)
    print(f'Total módulos visibles para {prof}: {all_modules.count()}')
    
    # Limpiar test
    TrainingModule.objects.filter(slug='test-personalizado').delete()
    print('Test limpiado.')
else:
    print('No hay profesionales en la DB. Creá uno primero.')
"
```

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 29: Modelo — Campos para capacitaciones personalizadas

- Campo is_personalized (BooleanField) para distinguir generales de personalizadas
- FK requested_by al profesional que solicitó la capacitación
- M2M assigned_professionals para controlar visibilidad
- Campo company_name_custom para identificar empresa/cliente
- Campo custom_notes para notas internas
- Métodos de clase: get_general_modules(), get_personalized_for_user(), get_all_for_user()
- Migración de base de datos
- Módulos existentes no afectados (is_personalized=False por defecto)"
```

---

# ═══════════════════════════════════════════════════════════════════
# COMMIT 30: Vista + Template — Separar Generales y Personalizadas
# ═══════════════════════════════════════════════════════════════════

## 📋 Descripción
Modificar la vista `capacitaciones_menu` y su template para mostrar dos secciones: capacitaciones generales y capacitaciones personalizadas del usuario logueado.

## 🎯 Objetivos
- [ ] Modificar la vista `capacitaciones_menu` para enviar dos querysets al template
- [ ] Modificar el template para mostrar dos secciones diferenciadas
- [ ] Agregar badge visual "Personalizada" en las cards
- [ ] Mantener la funcionalidad existente sin cambios
- [ ] Asegurar que las personalizadas solo son visibles para los asignados

## 📁 Archivos a modificar

---

### 1. `apps/dashboard/views.py` (MODIFICAR vista `capacitaciones_menu`)

**Reemplazar la vista `capacitaciones_menu` existente:**

```python
# ============================================================================
# ANTES (Commit 16):
# ============================================================================
# @login_required
# @professional_required
# def capacitaciones_menu(request):
#     modules = TrainingModule.objects.all()
#     return render(request, 'dashboard/capacitaciones_menu.html', {
#         'modules': modules,
#     })

# ============================================================================
# DESPUÉS (Commit 30):
# ============================================================================
@login_required
@professional_required
def capacitaciones_menu(request):
    """
    Menú de capacitaciones disponibles.
    Muestra dos secciones:
    1. Capacitaciones generales (visibles para todos)
    2. Capacitaciones personalizadas (solo las asignadas a este usuario)
    """
    # Capacitaciones generales (no personalizadas)
    general_modules = TrainingModule.get_general_modules()

    # Capacitaciones personalizadas asignadas a este profesional
    personalized_modules = TrainingModule.get_personalized_for_user(request.user)

    return render(request, 'dashboard/capacitaciones_menu.html', {
        'general_modules': general_modules,
        'personalized_modules': personalized_modules,
        'has_personalized': personalized_modules.exists(),
    })
```

> **NOTA:** Se eliminó la variable `modules` y se reemplazó por `general_modules` y `personalized_modules`. Esto requiere actualizar el template.

---

### 2. `templates/dashboard/capacitaciones_menu.html` (REEMPLAZAR COMPLETO)

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

    <!-- ================================================================== -->
    <!-- SECCIÓN 1: CAPACITACIONES GENERALES                                -->
    <!-- ================================================================== -->
    <div class="row mb-3">
        <div class="col">
            <h4 class="text-secondary mb-0">
                <i class="bi bi-collection me-2"></i>Capacitaciones Generales
            </h4>
            <small class="text-muted">Disponibles para todos los profesionales</small>
        </div>
    </div>

    <div class="row g-4 mb-5">
        {% for module in general_modules %}
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
                No hay capacitaciones generales cargadas aún. Contactá al administrador.
            </div>
        </div>
        {% endfor %}
    </div>

    <!-- ================================================================== -->
    <!-- SECCIÓN 2: CAPACITACIONES PERSONALIZADAS                           -->
    <!-- Solo se muestra si el usuario tiene capacitaciones asignadas        -->
    <!-- ================================================================== -->
    {% if has_personalized %}
    <hr class="border-secondary my-4">

    <div class="row mb-3">
        <div class="col">
            <h4 class="text-secondary mb-0">
                <i class="bi bi-person-lock me-2 text-info"></i>Mis Capacitaciones Personalizadas
            </h4>
            <small class="text-muted">Capacitaciones exclusivas asignadas a tu cuenta</small>
        </div>
    </div>

    <div class="row g-4 mb-4">
        {% for module in personalized_modules %}
        <div class="col-sm-6 col-lg-4 col-xl-3">
            {% if module.is_active %}
            <a href="{% url 'dashboard:modalidad_selector' module.slug %}" class="text-decoration-none">
            {% endif %}
                <div class="card training-card bg-dark h-100 {% if not module.is_active %}disabled-card{% endif %}"
                     style="border: 1px solid {{ module.color }}40;">
                    <div class="card-body text-center py-4">
                        <!-- Badge de personalizada -->
                        <div class="mb-2">
                            <span class="badge bg-info bg-opacity-25 text-info px-2 py-1 small">
                                <i class="bi bi-person-lock me-1"></i>Personalizada
                            </span>
                        </div>
                        <div class="card-icon mx-auto" style="background-color: {{ module.color }}20;">
                            <i class="{{ module.icon }}" style="color: {{ module.color }};"></i>
                        </div>
                        <h5 class="card-title text-white mb-1">{{ module.title }}</h5>
                        {% if module.company_name_custom %}
                        <p class="text-info small mb-2">
                            <i class="bi bi-building me-1"></i>{{ module.company_name_custom }}
                        </p>
                        {% endif %}
                        <p class="card-text text-secondary small mb-3">
                            {{ module.description|default:"Capacitación personalizada." }}
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
        {% endfor %}
    </div>
    {% endif %}

</div>
{% endblock %}
```

---

### 3. Verificar que `modalidad_selector` funciona con módulos personalizados

La vista `modalidad_selector` existente usa:
```python
module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
```

Esto ya funciona correctamente porque busca por `slug` y `is_active`, sin filtrar por `is_personalized`. **Sin embargo**, debemos agregar una verificación de seguridad para asegurar que un profesional solo pueda acceder a módulos que tiene permitido ver.

**Modificar `apps/dashboard/views.py` — vista `modalidad_selector`:**

```python
# ============================================================================
# ANTES:
# ============================================================================
# @login_required
# @professional_required
# def modalidad_selector(request, module_slug):
#     module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
#     return render(request, 'dashboard/modalidad_selector.html', {
#         'module': module,
#     })

# ============================================================================
# DESPUÉS (Commit 30):
# ============================================================================
from django.http import HttpResponseForbidden


@login_required
@professional_required
def modalidad_selector(request, module_slug):
    """
    Selector de modalidad: Presencial u Online.
    Verifica que el profesional tenga acceso al módulo.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)

    # ✅ Verificación de acceso para módulos personalizados
    if module.is_personalized:
        if not module.assigned_professionals.filter(pk=request.user.pk).exists():
            return HttpResponseForbidden(
                "No tenés acceso a esta capacitación personalizada."
            )

    return render(request, 'dashboard/modalidad_selector.html', {
        'module': module,
    })
```

---

### 4. Aplicar misma verificación en vistas de links online

**En `apps/dashboard/views.py` — vista `online_links`:**

Agregar al inicio de la vista, justo después de obtener el módulo:

```python
@login_required
@professional_required
def online_links(request, module_slug):
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)

    # ✅ Verificación de acceso para módulos personalizados
    if module.is_personalized:
        if not module.assigned_professionals.filter(pk=request.user.pk).exists():
            return HttpResponseForbidden(
                "No tenés acceso a esta capacitación personalizada."
            )

    links = CapacitacionLink.objects.filter(
        module=module,
        created_by=request.user,
    )
    return render(request, 'dashboard/online_links.html', {
        'module': module,
        'links': links,
    })
```

---

### 5. (OPCIONAL) Helper para verificación de acceso reutilizable

Para no repetir el código de verificación en cada vista, se puede crear un helper:

**Agregar en `apps/dashboard/views.py` o en un archivo `apps/dashboard/utils.py`:**

```python
# apps/dashboard/utils.py (CREAR)

from django.http import HttpResponseForbidden
from apps.training.models import TrainingModule


def check_module_access(module, user):
    """
    Verifica si un usuario tiene acceso a un módulo.
    Retorna None si tiene acceso, o HttpResponseForbidden si no.
    """
    if module.is_personalized:
        if not module.assigned_professionals.filter(pk=user.pk).exists():
            return HttpResponseForbidden(
                "No tenés acceso a esta capacitación personalizada."
            )
    return None
```

**Uso en las vistas:**

```python
from .utils import check_module_access

@login_required
@professional_required
def modalidad_selector(request, module_slug):
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)

    denied = check_module_access(module, request.user)
    if denied:
        return denied

    return render(request, 'dashboard/modalidad_selector.html', {
        'module': module,
    })
```

---

### ✅ Verificación del Commit 30
- [ ] `/dashboard/capacitaciones/` muestra sección "Capacitaciones Generales"
- [ ] Si el usuario tiene personalizadas asignadas, aparece la sección "Mis Capacitaciones Personalizadas"
- [ ] Si NO tiene personalizadas, la sección no aparece (no hay sección vacía)
- [ ] Las cards personalizadas muestran el badge "Personalizada"
- [ ] Las cards personalizadas muestran la empresa si está configurada
- [ ] Un profesional NO asignado NO ve las capacitaciones personalizadas de otro
- [ ] Intentar acceder a un módulo personalizado sin asignación retorna 403
- [ ] Los módulos generales siguen funcionando exactamente igual
- [ ] El breadcrumb y la navegación funcionan correctamente

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 30: Vista + Template — Separar generales y personalizadas

- Vista capacitaciones_menu envía dos querysets: general_modules y personalized_modules
- Template muestra sección 'Capacitaciones Generales' siempre
- Sección 'Mis Capacitaciones Personalizadas' solo si el usuario tiene asignadas
- Badge 'Personalizada' en cards de capacitaciones personalizadas
- Empresa/cliente visible en cards personalizadas
- Verificación de acceso en modalidad_selector y online_links
- Helper check_module_access() para reutilización
- Módulos generales no afectados"
```

---

# ═══════════════════════════════════════════════════════════════════
# COMMIT 31: Admin Avanzado — Gestión de Capacitaciones Personalizadas
# ═══════════════════════════════════════════════════════════════════

## 📋 Descripción
Configurar el Admin de Django para facilitar la creación y gestión de capacitaciones personalizadas, incluyendo la asignación de profesionales y filtros especializados.

## 🎯 Objetivos
- [ ] Actualizar `TrainingModuleAdmin` con nuevos fieldsets
- [ ] Agregar filtros por `is_personalized`
- [ ] Widget autocomplete para selección de profesionales
- [ ] Acciones batch para asignar/desasignar profesionales
- [ ] Vista de resumen de asignaciones
- [ ] (Opcional) Formulario de solicitud para profesionales

## 📁 Archivos a modificar

---

### 1. `apps/training/admin.py` (REEMPLAZAR COMPLETO)

```python
# apps/training/admin.py
# ============================================================================
# COMMIT 31: Admin actualizado con gestión de capacitaciones personalizadas
# ============================================================================

from django.contrib import admin
from django.utils.html import format_html

from .models import TrainingModule, CapacitacionLink, LinkShareLog


@admin.register(TrainingModule)
class TrainingModuleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "is_personalized_display",
        "company_name_custom",
        "assigned_count",
        "icon",
        "order",
        "is_active",
        "updated_at",
    )
    list_filter = (
        "is_personalized",
        "is_active",
    )
    list_editable = ("order", "is_active")
    search_fields = ("title", "slug", "youtube_id", "company_name_custom")
    prepopulated_fields = {"slug": ("title",)}

    # Autocomplete para relaciones con usuarios
    filter_horizontal = ('assigned_professionals',)

    fieldsets = (
        ("Información básica", {
            "fields": ("title", "slug", "description", "youtube_id", "is_active")
        }),
        ("Apariencia en menú", {
            "fields": ("icon", "color", "order"),
            "description": "Configuración visual para el menú de capacitaciones"
        }),
        ("📌 Personalización", {
            "fields": (
                "is_personalized",
                "requested_by",
                "assigned_professionals",
                "company_name_custom",
                "custom_notes",
            ),
            "description": (
                "Si 'Es personalizada' está activado, esta capacitación SOLO será "
                "visible para los profesionales seleccionados en 'Profesionales asignados'. "
                "El resto de los usuarios no la verá en su menú."
            ),
            "classes": ("wide",),
        }),
        ("Contenido", {
            "fields": ("intro_md", "material_md", "transcript_md"),
            "classes": ("collapse",),
        }),
    )

    def is_personalized_display(self, obj):
        """Muestra un ícono visual para personalizada/general."""
        if obj.is_personalized:
            return format_html(
                '<span style="color: #17a2b8;">🔒 Personalizada</span>'
            )
        return format_html(
            '<span style="color: #28a745;">🌐 General</span>'
        )
    is_personalized_display.short_description = "Tipo"
    is_personalized_display.admin_order_field = "is_personalized"

    def assigned_count(self, obj):
        """Muestra la cantidad de profesionales asignados."""
        if not obj.is_personalized:
            return "-"
        count = obj.assigned_professionals.count()
        return format_html(
            '<span class="badge" style="background-color:#17a2b8;color:white;padding:3px 8px;border-radius:4px;">'
            '{} prof.</span>',
            count
        )
    assigned_count.short_description = "Asignados"

    def get_queryset(self, request):
        """Optimizar queries con prefetch."""
        qs = super().get_queryset(request)
        return qs.prefetch_related('assigned_professionals')

    # =========================================================================
    # Acciones batch
    # =========================================================================
    actions = ['mark_as_personalized', 'mark_as_general']

    @admin.action(description="Marcar como capacitación personalizada")
    def mark_as_personalized(self, request, queryset):
        updated = queryset.update(is_personalized=True)
        self.message_user(
            request,
            f"{updated} capacitación(es) marcada(s) como personalizada(s)."
        )

    @admin.action(description="Marcar como capacitación general")
    def mark_as_general(self, request, queryset):
        updated = queryset.update(is_personalized=False)
        self.message_user(
            request,
            f"{updated} capacitación(es) marcada(s) como general(es)."
        )


@admin.register(CapacitacionLink)
class CapacitacionLinkAdmin(admin.ModelAdmin):
    list_display = ('module', 'label', 'created_by', 'created_at', 'is_active', 'access_count')
    list_filter = ('module', 'is_active', 'created_at')
    search_fields = ('label', 'created_by__email')
    readonly_fields = ('id', 'created_at', 'access_count')


@admin.register(LinkShareLog)
class LinkShareLogAdmin(admin.ModelAdmin):
    list_display = ('link', 'shared_to_email', 'shared_at')
    list_filter = ('shared_at',)
    search_fields = ('shared_to_email',)
    readonly_fields = ('shared_at',)
```

---

### 2. (OPCIONAL) Management Command para crear capacitación personalizada

Para facilitar la creación de capacitaciones personalizadas desde la línea de comandos:

**Crear `apps/training/management/commands/create_custom_training.py`:**

```python
# apps/training/management/commands/create_custom_training.py
# ============================================================================
# COMMIT 31: Comando para crear capacitaciones personalizadas
# ============================================================================

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from apps.training.models import TrainingModule

User = get_user_model()


class Command(BaseCommand):
    help = 'Crear una capacitación personalizada y asignarla a un profesional'

    def add_arguments(self, parser):
        parser.add_argument('--title', type=str, required=True, help='Título de la capacitación')
        parser.add_argument('--email', type=str, required=True, help='Email del profesional a asignar')
        parser.add_argument('--company', type=str, default='', help='Nombre de la empresa')
        parser.add_argument('--base-module', type=str, default='', help='Slug del módulo base para copiar contenido')
        parser.add_argument('--icon', type=str, default='bi-person-gear', help='Clase de Bootstrap Icons')
        parser.add_argument('--color', type=str, default='#17a2b8', help='Color hex')

    def handle(self, *args, **options):
        title = options['title']
        email = options['email']
        company = options['company']
        base_slug = options['base_module']
        icon = options['icon']
        color = options['color']

        # Buscar el profesional
        try:
            professional = User.objects.get(email=email, user_type='professional')
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Profesional con email {email} no encontrado.'))
            return

        # Generar slug único
        base_slug_text = slugify(title)
        slug = base_slug_text
        counter = 1
        while TrainingModule.objects.filter(slug=slug).exists():
            slug = f"{base_slug_text}-{counter}"
            counter += 1

        # Copiar contenido del módulo base si se especificó
        intro_md = ''
        material_md = ''
        transcript_md = ''
        youtube_id = ''

        if base_slug:
            try:
                base_module = TrainingModule.objects.get(slug=base_slug)
                intro_md = base_module.intro_md
                material_md = base_module.material_md
                transcript_md = base_module.transcript_md
                youtube_id = base_module.youtube_id
                self.stdout.write(
                    self.style.SUCCESS(f'  Contenido copiado del módulo: {base_module.title}')
                )
            except TrainingModule.DoesNotExist:
                self.stderr.write(
                    self.style.WARNING(f'  Módulo base "{base_slug}" no encontrado. Creando sin contenido.')
                )

        # Crear el módulo
        module = TrainingModule.objects.create(
            slug=slug,
            title=title,
            description=f'Capacitación personalizada para {company}' if company else f'Capacitación personalizada',
            youtube_id=youtube_id,
            intro_md=intro_md,
            material_md=material_md,
            transcript_md=transcript_md,
            is_active=True,
            icon=icon,
            color=color,
            order=100,  # Al final del listado
            is_personalized=True,
            requested_by=professional,
            company_name_custom=company,
        )

        # Asignar al profesional
        module.assigned_professionals.add(professional)

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Capacitación personalizada creada:'
            f'\n   Título: {module.title}'
            f'\n   Slug: {module.slug}'
            f'\n   Empresa: {module.company_name_custom or "N/A"}'
            f'\n   Asignada a: {professional.display_name} ({professional.email})'
            f'\n   Estado: Activa'
        ))
```

**Uso:**

```bash
# Crear capacitación personalizada básica
python manage.py create_custom_training \
    --title "Ergonomía - Acme S.A." \
    --email "profesional@example.com" \
    --company "Acme S.A."

# Crear copiando contenido de un módulo existente
python manage.py create_custom_training \
    --title "Ergonomía - Planta Norte" \
    --email "profesional@example.com" \
    --company "Fábrica Norte SRL" \
    --base-module "ergonomia" \
    --icon "bi-body-text" \
    --color "#e83e8c"
```

---

### 3. (OPCIONAL) Formulario de Solicitud para Profesionales

Si se desea que los profesionales puedan solicitar capacitaciones personalizadas desde el dashboard (en lugar de solo por admin), se puede agregar un formulario simple:

**Crear `apps/dashboard/forms.py` (AGREGAR al archivo existente):**

```python
# apps/dashboard/forms.py
# ============================================================================
# COMMIT 31: Formulario de solicitud de capacitación personalizada
# ============================================================================

from django import forms


class SolicitudCapacitacionForm(forms.Form):
    """Formulario para que un profesional solicite una capacitación personalizada."""

    titulo = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary',
            'placeholder': 'Ej: Ergonomía en Oficinas - Empresa XYZ',
        }),
        label="Título de la capacitación",
    )
    empresa = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-white border-secondary',
            'placeholder': 'Ej: Acme S.A.',
        }),
        label="Empresa / Cliente",
    )
    tema_base = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select bg-dark text-white border-secondary',
        }),
        label="Basada en (temática)",
        help_text="Seleccioná un tema base si querés que la capacitación tenga contenido similar.",
    )
    descripcion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control bg-dark text-white border-secondary',
            'rows': 4,
            'placeholder': 'Describí las particularidades de esta capacitación...',
        }),
        label="Descripción / Notas",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.training.models import TrainingModule
        # Opciones de tema base: módulos generales activos
        choices = [('', '-- Ninguno --')]
        for m in TrainingModule.get_general_modules().filter(is_active=True):
            choices.append((m.slug, m.title))
        self.fields['tema_base'].choices = choices
```

**Vista en `apps/dashboard/views.py`:**

```python
from .forms import SolicitudCapacitacionForm


@login_required
@professional_required
def solicitar_capacitacion(request):
    """
    Formulario para solicitar una capacitación personalizada.
    Genera una solicitud que el admin puede aprobar.
    """
    if request.method == 'POST':
        form = SolicitudCapacitacionForm(request.POST)
        if form.is_valid():
            # Por ahora, crear el módulo directamente como inactivo (pendiente de aprobación)
            from django.utils.text import slugify
            titulo = form.cleaned_data['titulo']
            empresa = form.cleaned_data['empresa']
            descripcion = form.cleaned_data['descripcion']
            tema_base_slug = form.cleaned_data['tema_base']

            # Generar slug único
            base_slug = slugify(titulo)
            slug = base_slug
            counter = 1
            while TrainingModule.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            # Copiar contenido del módulo base si se seleccionó
            intro_md = ''
            material_md = ''
            transcript_md = ''
            youtube_id = ''

            if tema_base_slug:
                try:
                    base_module = TrainingModule.objects.get(slug=tema_base_slug)
                    intro_md = base_module.intro_md
                    material_md = base_module.material_md
                    transcript_md = base_module.transcript_md
                    youtube_id = base_module.youtube_id
                except TrainingModule.DoesNotExist:
                    pass

            module = TrainingModule.objects.create(
                slug=slug,
                title=titulo,
                description=descripcion or f'Capacitación personalizada para {empresa}',
                youtube_id=youtube_id,
                intro_md=intro_md,
                material_md=material_md,
                transcript_md=transcript_md,
                is_active=False,  # ❗ Inactivo hasta que el admin la apruebe
                icon='bi-person-gear',
                color='#17a2b8',
                order=100,
                is_personalized=True,
                requested_by=request.user,
                company_name_custom=empresa,
                custom_notes=f'Solicitada por {request.user.display_name}. {descripcion}',
            )
            module.assigned_professionals.add(request.user)

            messages.success(
                request,
                f'Solicitud de capacitación "{titulo}" enviada correctamente. '
                f'Será activada por el administrador.'
            )
            return redirect('dashboard:capacitaciones_menu')
    else:
        form = SolicitudCapacitacionForm()

    return render(request, 'dashboard/solicitar_capacitacion.html', {
        'form': form,
    })
```

**Agregar URL en `apps/dashboard/urls.py`:**

```python
path('capacitaciones/solicitar/', views.solicitar_capacitacion, name='solicitar_capacitacion'),
```

> ⚠️ **IMPORTANTE:** Esta URL debe estar **ANTES** de `capacitaciones/<slug:module_slug>/` para que Django no confunda "solicitar" con un slug de módulo.

**Template `templates/dashboard/solicitar_capacitacion.html`:**

```html
{% extends "base_dashboard.html" %}

{% block title %}Solicitar Capacitación - ErgoSolutions{% endblock %}

{% block content %}
<div class="container-fluid py-4 px-4">

    <nav aria-label="breadcrumb" class="mb-3">
        <ol class="breadcrumb breadcrumb-dark">
            <li class="breadcrumb-item"><a href="{% url 'dashboard:home' %}">Dashboard</a></li>
            <li class="breadcrumb-item"><a href="{% url 'dashboard:capacitaciones_menu' %}">Capacitaciones</a></li>
            <li class="breadcrumb-item active">Solicitar Capacitación</li>
        </ol>
    </nav>

    <div class="row justify-content-center">
        <div class="col-lg-8">
            <div class="card bg-dark border-info">
                <div class="card-header bg-info bg-opacity-10 border-info">
                    <h4 class="mb-0">
                        <i class="bi bi-plus-circle me-2 text-info"></i>
                        Solicitar Capacitación Personalizada
                    </h4>
                </div>
                <div class="card-body">
                    <p class="text-secondary mb-4">
                        Completá los datos para solicitar una capacitación personalizada.
                        Una vez enviada, el administrador la revisará y activará.
                    </p>

                    <form method="post">
                        {% csrf_token %}

                        {% for field in form %}
                        <div class="mb-3">
                            <label for="{{ field.id_for_label }}" class="form-label text-white">
                                {{ field.label }}
                                {% if field.field.required %}<span class="text-danger">*</span>{% endif %}
                            </label>
                            {{ field }}
                            {% if field.help_text %}
                                <small class="text-muted">{{ field.help_text }}</small>
                            {% endif %}
                            {% for error in field.errors %}
                                <div class="invalid-feedback d-block">{{ error }}</div>
                            {% endfor %}
                        </div>
                        {% endfor %}

                        <div class="d-flex gap-2 mt-4">
                            <button type="submit" class="btn btn-info">
                                <i class="bi bi-send me-1"></i>Enviar Solicitud
                            </button>
                            <a href="{% url 'dashboard:capacitaciones_menu' %}" class="btn btn-outline-secondary">
                                Cancelar
                            </a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

</div>
{% endblock %}
```

---

### 4. Agregar botón de solicitud en el menú de capacitaciones

**En `templates/dashboard/capacitaciones_menu.html`, agregar después del encabezado:**

```html
<!-- Botón para solicitar capacitación personalizada -->
<div class="row mb-4">
    <div class="col text-end">
        <a href="{% url 'dashboard:solicitar_capacitacion' %}" class="btn btn-outline-info btn-sm">
            <i class="bi bi-plus-circle me-1"></i>Solicitar Capacitación Personalizada
        </a>
    </div>
</div>
```

---

### ✅ Verificación del Commit 31
- [ ] Admin muestra columna "Tipo" con ícono visual (General/Personalizada)
- [ ] Admin muestra columna "Asignados" con cantidad de profesionales
- [ ] Fieldset "Personalización" permite configurar todos los campos
- [ ] `filter_horizontal` permite seleccionar profesionales fácilmente
- [ ] Acciones batch "Marcar como personalizada" y "Marcar como general" funcionan
- [ ] Management command `create_custom_training` funciona correctamente
- [ ] (Si implementado) Formulario de solicitud crea módulo inactivo
- [ ] (Si implementado) Botón "Solicitar" aparece en el menú de capacitaciones

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 31: Admin avanzado — Gestión de capacitaciones personalizadas

- Admin TrainingModule actualizado con fieldset 'Personalización'
- Columnas visuales: tipo (General/Personalizada) y asignados
- filter_horizontal para selección de profesionales
- Acciones batch: marcar como personalizada/general
- Management command create_custom_training
- (Opcional) Formulario de solicitud para profesionales
- (Opcional) Template solicitar_capacitacion.html
- (Opcional) Botón 'Solicitar' en menú de capacitaciones"
```

---

# ═══════════════════════════════════════════════════════════════════
# COMMIT 32: Integración Completa + Tests + Verificación Final
# ═══════════════════════════════════════════════════════════════════

## 📋 Descripción
Verificar la integración completa de las capacitaciones personalizadas con todos los flujos existentes (presencial, online, ergobot), agregar tests y realizar correcciones finales.

## 🎯 Objetivos
- [ ] Verificar flujo presencial con módulos personalizados
- [ ] Verificar flujo online (links) con módulos personalizados
- [ ] Verificar Ergobot IA con módulos personalizados
- [ ] Agregar tests automatizados
- [ ] Verificar seguridad (acceso no autorizado)
- [ ] Actualizar stats del dashboard

## 📁 Archivos a modificar

---

### 1. Verificar acceso en `apps/presencial/views.py`

Agregar verificación de acceso en la vista `capacitacion_presencial`:

```python
# apps/presencial/views.py
# ============================================================================
# COMMIT 32: Agregar verificación de acceso para módulos personalizados
# ============================================================================

from django.http import HttpResponseForbidden


@login_required
@professional_required
@ensure_csrf_cookie
def capacitacion_presencial(request, module_slug):
    """
    Página de capacitación para uso presencial.
    Incluye video + chat Ergobot, sin registro de trabajadores.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)

    # ✅ Verificación de acceso para módulos personalizados
    if module.is_personalized:
        if not module.assigned_professionals.filter(pk=request.user.pk).exists():
            return HttpResponseForbidden(
                "No tenés acceso a esta capacitación personalizada."
            )

    return render(request, 'presencial/capacitacion.html', {
        'module': module,
    })
```

**Aplicar lo mismo en:**
- `quiz_presencial` (si existe)
- `planilla_pdf` (si existe)

---

### 2. Actualizar stats del Dashboard

Modificar `apps/dashboard/views.py` — vista `home` para incluir stats de personalizadas:

```python
@login_required
@professional_required
def home(request):
    """Dashboard principal con stats actualizadas."""
    from apps.presencial.models import PresencialSession
    from apps.training.models import CapacitacionLink, TrainingModule

    stats = {
        'capacitaciones_total': TrainingModule.get_all_for_user(request.user).filter(is_active=True).count(),
        'capacitaciones_personalizadas': TrainingModule.get_personalized_for_user(request.user).filter(is_active=True).count(),
        'links_generados': CapacitacionLink.objects.filter(created_by=request.user).count(),
        'trabajadores_capacitados': 0,  # Se completará con datos reales
    }

    # Stats de presencial
    try:
        sessions = PresencialSession.objects.filter(professional=request.user)
        stats['sesiones_presenciales'] = sessions.count()
    except Exception:
        stats['sesiones_presenciales'] = 0

    return render(request, 'dashboard/home.html', {
        'stats': stats,
    })
```

---

### 3. Tests automatizados

**Crear/Agregar en `apps/training/tests.py`:**

```python
# apps/training/tests.py
# ============================================================================
# COMMIT 32: Tests para capacitaciones personalizadas
# ============================================================================

from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from apps.training.models import TrainingModule

User = get_user_model()


class PersonalizedTrainingModelTests(TestCase):
    """Tests para el modelo TrainingModule con campos personalizados."""

    def setUp(self):
        """Crear datos de prueba."""
        # Profesional 1
        self.prof1 = User.objects.create_user(
            email='prof1@test.com',
            user_type='professional',
            password='testpass123',
            username='prof1',
            first_name='Profesional',
            last_name='Uno',
        )
        # Profesional 2
        self.prof2 = User.objects.create_user(
            email='prof2@test.com',
            user_type='professional',
            password='testpass123',
            username='prof2',
            first_name='Profesional',
            last_name='Dos',
        )

        # Módulo general
        self.general_module = TrainingModule.objects.create(
            slug='ergonomia-general',
            title='Ergonomía General',
            is_active=True,
            is_personalized=False,
        )

        # Módulo personalizado asignado a prof1
        self.custom_module = TrainingModule.objects.create(
            slug='ergonomia-acme',
            title='Ergonomía - Acme S.A.',
            is_active=True,
            is_personalized=True,
            requested_by=self.prof1,
            company_name_custom='Acme S.A.',
        )
        self.custom_module.assigned_professionals.add(self.prof1)

    def test_general_module_not_personalized(self):
        """Un módulo general tiene is_personalized=False."""
        self.assertFalse(self.general_module.is_personalized)

    def test_custom_module_is_personalized(self):
        """Un módulo personalizado tiene is_personalized=True."""
        self.assertTrue(self.custom_module.is_personalized)

    def test_get_general_modules(self):
        """get_general_modules() retorna solo los generales."""
        general = TrainingModule.get_general_modules()
        self.assertIn(self.general_module, general)
        self.assertNotIn(self.custom_module, general)

    def test_get_personalized_for_assigned_user(self):
        """get_personalized_for_user() retorna personalizadas del usuario asignado."""
        personalized = TrainingModule.get_personalized_for_user(self.prof1)
        self.assertIn(self.custom_module, personalized)

    def test_get_personalized_for_unassigned_user(self):
        """get_personalized_for_user() NO retorna personalizadas de otro usuario."""
        personalized = TrainingModule.get_personalized_for_user(self.prof2)
        self.assertNotIn(self.custom_module, personalized)

    def test_get_all_for_assigned_user(self):
        """get_all_for_user() retorna generales + personalizadas del usuario."""
        all_modules = TrainingModule.get_all_for_user(self.prof1)
        self.assertIn(self.general_module, all_modules)
        self.assertIn(self.custom_module, all_modules)

    def test_get_all_for_unassigned_user(self):
        """get_all_for_user() retorna generales pero NO personalizadas de otro."""
        all_modules = TrainingModule.get_all_for_user(self.prof2)
        self.assertIn(self.general_module, all_modules)
        self.assertNotIn(self.custom_module, all_modules)

    def test_str_general_module(self):
        """__str__ de módulo general no tiene prefijo."""
        self.assertNotIn("[PERSONALIZADA]", str(self.general_module))

    def test_str_custom_module(self):
        """__str__ de módulo personalizado tiene prefijo."""
        self.assertIn("[PERSONALIZADA]", str(self.custom_module))


class PersonalizedTrainingViewTests(TestCase):
    """Tests para las vistas del menú de capacitaciones."""

    def setUp(self):
        self.client = Client()

        self.prof1 = User.objects.create_user(
            email='prof1@test.com',
            user_type='professional',
            password='testpass123',
            username='prof1',
        )
        self.prof2 = User.objects.create_user(
            email='prof2@test.com',
            user_type='professional',
            password='testpass123',
            username='prof2',
        )

        self.general_module = TrainingModule.objects.create(
            slug='ergo-general',
            title='Ergonomía General',
            is_active=True,
            is_personalized=False,
        )
        self.custom_module = TrainingModule.objects.create(
            slug='ergo-custom',
            title='Ergonomía Custom',
            is_active=True,
            is_personalized=True,
        )
        self.custom_module.assigned_professionals.add(self.prof1)

    def test_capacitaciones_menu_shows_general_for_all(self):
        """El menú muestra módulos generales para cualquier profesional."""
        self.client.login(email='prof1@test.com', password='testpass123')
        response = self.client.get('/dashboard/capacitaciones/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.general_module, response.context['general_modules'])

    def test_capacitaciones_menu_shows_personalized_for_assigned(self):
        """El menú muestra personalizadas solo para el profesional asignado."""
        self.client.login(email='prof1@test.com', password='testpass123')
        response = self.client.get('/dashboard/capacitaciones/')
        self.assertIn(self.custom_module, response.context['personalized_modules'])

    def test_capacitaciones_menu_hides_personalized_for_others(self):
        """El menú NO muestra personalizadas para profesionales no asignados."""
        self.client.login(email='prof2@test.com', password='testpass123')
        response = self.client.get('/dashboard/capacitaciones/')
        self.assertNotIn(self.custom_module, response.context['personalized_modules'])

    def test_modalidad_selector_allows_assigned_user(self):
        """Un profesional asignado puede acceder al selector de modalidad."""
        self.client.login(email='prof1@test.com', password='testpass123')
        response = self.client.get(f'/dashboard/capacitaciones/{self.custom_module.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_modalidad_selector_blocks_unassigned_user(self):
        """Un profesional NO asignado recibe 403 al acceder."""
        self.client.login(email='prof2@test.com', password='testpass123')
        response = self.client.get(f'/dashboard/capacitaciones/{self.custom_module.slug}/')
        self.assertEqual(response.status_code, 403)
```

**Ejecutar tests:**

```bash
python manage.py test apps.training.tests.PersonalizedTrainingModelTests -v 2
python manage.py test apps.training.tests.PersonalizedTrainingViewTests -v 2

# O todos juntos:
python manage.py test apps.training -v 2
```

---

### 4. URLs finales actualizadas

```python
# apps/dashboard/urls.py
# ============================================================================
# COMMIT 15-32: URLs del dashboard de profesionales (FINAL)
# ============================================================================

from django.urls import path, include
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('capacitaciones/', views.capacitaciones_menu, name='capacitaciones_menu'),
    path('capacitaciones/solicitar/', views.solicitar_capacitacion, name='solicitar_capacitacion'),
    path('capacitaciones/<slug:module_slug>/', views.modalidad_selector, name='modalidad_selector'),
    path('capacitaciones/<slug:module_slug>/links/', views.online_links, name='online_links'),
    path('capacitaciones/<slug:module_slug>/links/generar/', views.generate_link, name='generate_link'),
    path('capacitaciones/<slug:module_slug>/links/<uuid:link_id>/compartir/', views.share_link, name='share_link'),
    path('presencial/', include('apps.presencial.urls')),
    path('perfil/', views.profile, name='profile'),
]
```

> ⚠️ **NOTAR** que `capacitaciones/solicitar/` está ANTES de `capacitaciones/<slug:module_slug>/` para que Django no confunda "solicitar" con un slug.

---

### ✅ Verificación del Commit 32
- [ ] Todos los tests pasan: `python manage.py test apps.training -v 2`
- [ ] Flujo presencial funciona con módulos personalizados
- [ ] Flujo online (links) funciona con módulos personalizados
- [ ] Ergobot IA funciona con módulos personalizados (usa el contenido del módulo)
- [ ] Stats del dashboard muestran capacitaciones personalizadas
- [ ] Acceso no autorizado a módulos personalizados retorna 403
- [ ] Navegación completa funciona sin errores

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 32: Integración completa + Tests + Verificación final

- Verificación de acceso en vistas presencial y online
- Stats actualizadas con datos de capacitaciones personalizadas
- Tests automatizados para modelos (8 tests)
- Tests automatizados para vistas (5 tests)
- URLs finales actualizadas
- Seguridad: profesionales no asignados reciben 403
- Integración verificada con Ergobot IA"
```

---

# ═══════════════════════════════════════════════════════════════════
# RESUMEN DE ARCHIVOS AFECTADOS
# ═══════════════════════════════════════════════════════════════════

| Archivo | Acción | Commit |
|---------|--------|--------|
| `apps/training/models.py` | MODIFICAR (agregar 5 campos + 3 métodos) | 29 |
| `apps/training/migrations/0005_*.py` | CREAR (auto-generada) | 29 |
| `apps/dashboard/views.py` | MODIFICAR (capacitaciones_menu, modalidad_selector, online_links + nueva vista solicitar) | 30, 31 |
| `apps/dashboard/utils.py` | CREAR (helper check_module_access) | 30 |
| `templates/dashboard/capacitaciones_menu.html` | REEMPLAZAR (dos secciones + botón solicitar) | 30, 31 |
| `apps/training/admin.py` | REEMPLAZAR (fieldsets + acciones + columnas) | 31 |
| `apps/training/management/commands/create_custom_training.py` | CREAR | 31 |
| `apps/dashboard/forms.py` | MODIFICAR (agregar SolicitudCapacitacionForm) | 31 |
| `templates/dashboard/solicitar_capacitacion.html` | CREAR | 31 |
| `apps/dashboard/urls.py` | MODIFICAR (agregar ruta solicitar) | 31 |
| `apps/presencial/views.py` | MODIFICAR (agregar verificación acceso) | 32 |
| `apps/training/tests.py` | CREAR/AGREGAR (13 tests) | 32 |

---

# ═══════════════════════════════════════════════════════════════════
# CHECKLIST FINAL DE IMPLEMENTACIÓN
# ═══════════════════════════════════════════════════════════════════

## Pre-implementación
- [ ] Hacer backup de la base de datos
- [ ] Verificar que el proyecto está en el último commit (28)
- [ ] Branch: `git checkout -b feature/capacitaciones-personalizadas`

## Commit 29
- [ ] Agregar campos al modelo TrainingModule
- [ ] Ejecutar `makemigrations` y `migrate`
- [ ] Verificar con shell que los métodos funcionan
- [ ] `git add . && git commit`

## Commit 30
- [ ] Modificar vista `capacitaciones_menu`
- [ ] Reemplazar template `capacitaciones_menu.html`
- [ ] Agregar verificación en `modalidad_selector`
- [ ] Crear helper `check_module_access`
- [ ] Crear un módulo personalizado de prueba desde admin
- [ ] Verificar visibilidad correcta
- [ ] `git add . && git commit`

## Commit 31
- [ ] Actualizar admin con fieldsets y acciones
- [ ] Crear management command
- [ ] (Opcional) Crear formulario de solicitud
- [ ] (Opcional) Crear template de solicitud
- [ ] (Opcional) Agregar botón en menú
- [ ] `git add . && git commit`

## Commit 32
- [ ] Agregar verificación de acceso en vistas presencial
- [ ] Actualizar stats del dashboard
- [ ] Escribir y ejecutar tests
- [ ] Verificación completa de todos los flujos
- [ ] `git add . && git commit`

## Post-implementación
- [ ] Merge a main: `git checkout main && git merge feature/capacitaciones-personalizadas`
- [ ] Deploy a producción
- [ ] Crear datos de prueba en producción
- [ ] Verificar en producción

---

*Documento generado para ErgoSolutions*
*Capacitaciones Personalizadas | Commits 29–32*
*Fecha: 27 de Febrero 2026*
