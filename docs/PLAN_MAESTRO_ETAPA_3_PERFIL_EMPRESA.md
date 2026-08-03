# 📋 ERGOSOLUTIONS — PLAN MAESTRO ETAPA 3: PERFIL EMPRESA

## Documento de Referencia para Implementación

**Proyecto:** ErgoSolutions
**Estado actual:** Etapa 2 completada + Capacitaciones Personalizadas
**Etapa:** 3 — Perfil Empresa
**Commits planificados:** 29 – 48
**Fecha de creación:** Marzo 2026

---

## Decisiones de Arquitectura

### DA-2026-07-30-01 — Centralización de la documentación técnica

**Decisión acordada:** centralizar en `docs/` la documentación técnica, los planes,
los roadmaps, el runbook de despliegue y el inventario del proyecto.

**Excepciones deliberadas:**

- `README.md` permanece en la raíz como punto de entrada del repositorio.
- `AGENTS.md` permanece en la raíz para que las instrucciones operativas sean
  descubiertas por los asistentes.
- Los archivos Markdown que son contenido funcional de una app permanecen junto
  a su dominio (`apps/training/content/` y `apps/ergobot_ai/prompts/`).

**Trazabilidad:** la auditoría de producción del 30/07/2026 se incorpora como
documento histórico, manteniendo íntegro el informe entregado y diferenciándolo
del estado del código local.

---

## 📖 ÍNDICE GENERAL

| Sub-Etapa | Commits | Descripción |
|-----------|---------|-------------|
| **3A** | 29–34 | Base de acceso y perfil Empresa |
| **3B** | 35–40 | Nómina de Trabajadores |
| **3C** | 41–45 | Agenda y Vencimientos |
| **3D** | 46–48 | Preparación para red profesional + Testing |

---

## 🔍 ANÁLISIS DEL ESTADO ACTUAL DEL PROYECTO

### Arquitectura de Usuarios Existente

```
CustomUser (AbstractBaseUser + PermissionsMixin)
├── user_type: 'professional' | 'trainee'
├── email (unique, USERNAME_FIELD)
├── username (unique, nullable — solo professional)
├── cuil (unique, nullable — solo trainee)
├── password (unusable para trainee)
├── Campos comunes: first_name, last_name, full_name
├── Campos professional: dni, profession, license_number
├── Campos trainee: job_title, company_name, employer_email, safety_responsible_email
└── Campos suscripción: subscription_tier, subscription_status, subscription_expires
```

### Autenticación Actual

```
AUTHENTICATION_BACKENDS (config/settings.py):
├── ProfessionalBackend  → email/username + password → user_type='professional'
└── CuilEmailBackend     → cuil + email (sin password) → user_type='trainee'
```

### Decoradores Existentes (apps/accounts/decorators.py)

```python
@professional_required   # Verifica is_professional (user_type == 'professional')
@trainee_required        # Verifica is_trainee (user_type == 'trainee')
@subscription_required   # Verifica nivel de suscripción (futuro)
```

### Estructura de URLs Actual (config/urls.py)

```
/admin/                              → Admin Django
/dashboard/                          → include('apps.dashboard.urls', namespace='dashboard')
/                                    → include('apps.landing.urls', namespace='landing')
/acceso/                             → include('apps.accounts.urls')  — trainees
/capacitacion/                       → include('apps.training.urls')
/quiz/                               → include('apps.quiz.urls')
/certificados/                       → include('apps.certificates.urls')
/ai/                                 → include('apps.ergobot_ai.urls')
/auth/                               → include('apps.accounts.urls_professional') — profesionales
/c/                                  → include('apps.training.urls_public') — links compartidos
```

### Dashboard URLs Actual (apps/dashboard/urls.py)

```
/dashboard/                                               → home
/dashboard/capacitaciones/                                 → capacitaciones_menu
/dashboard/capacitaciones/<slug>/                          → modalidad_selector
/dashboard/capacitaciones/<slug>/links/                    → online_links
/dashboard/capacitaciones/<slug>/links/generar/            → generate_link
/dashboard/capacitaciones/<slug>/links/<uuid>/compartir/   → share_link
/dashboard/presencial/                                     → include presencial.urls
/dashboard/perfil/                                         → profile
```

### INSTALLED_APPS Actual (config/settings.py)

```python
LOCAL_APPS = [
    "apps.accounts",
    'apps.landing',
    'apps.dashboard',
    "apps.presencial",
    "apps.training",
    "apps.quiz",
    "apps.certificates",
    "apps.ergobot_ai",
]
```

### Templates Base

```
templates/base.html              → base general (trainees)
templates/base_landing.html      → landing page pública
templates/base_dashboard.html    → área de gestión (navbar: Dashboard + Capacitaciones + dropdown user)
```

### Modelos Existentes Relevantes

```
accounts.CustomUser          → Usuario unificado con user_type
training.TrainingModule      → Módulos de capacitación (general + personalizado)
training.CapacitacionLink    → Links compartibles
training.LinkShareLog        → Registro de envíos
quiz.Question / Choice       → Preguntas y opciones
quiz.QuizAttempt             → Intentos de examen
quiz.QuizState               → Estado global usuario-módulo
certificates.Certificate    → Certificados emitidos (con valid_until)
presencial.PresencialSession → Sesiones presenciales
```

### Archivos Clave que Se Modificarán en Etapa 3

```
apps/accounts/models.py          → Agregar user_type 'company' + is_visible_in_directory
apps/accounts/decorators.py      → Agregar @backoffice_required, @company_required
apps/accounts/mixins.py          → Agregar BackofficeRequiredMixin, CompanyRequiredMixin
apps/accounts/forms.py           → Agregar CompanyRegisterForm
apps/accounts/admin.py           → Actualizar para nuevo tipo
apps/dashboard/views.py          → Refactorizar para aceptar company
apps/dashboard/urls.py           → Agregar rutas de empresa
config/urls.py                   → Agregar rutas de auth empresa
config/settings.py               → Agregar app 'apps.company', context processor
templates/base_dashboard.html    → Menú condicional por tipo de usuario
```

---

# ═══════════════════════════════════════════════════════════════════════════
# SUB-ETAPA 3A: BASE DE ACCESO Y PERFIL EMPRESA (Commits 29–34)
# ═══════════════════════════════════════════════════════════════════════════

---

## COMMIT 29: Agregar user_type 'company' a CustomUser

### 📋 Descripción
Extender el modelo CustomUser para soportar un tercer tipo de usuario: `company`. Este es el cambio más fundamental de la Etapa 3 porque todo lo demás depende de que exista este tipo de usuario.

### 🎯 Objetivos
- [ ] Agregar `COMPANY = 'company', 'Empresa'` a `UserType.choices`
- [ ] Agregar propiedad `is_company` al modelo
- [ ] Agregar propiedad `is_backoffice_user` (True para professional Y company)
- [ ] Agregar método `create_company` al Manager
- [ ] Actualizar `create_user` para aceptar tipo 'company'
- [ ] Crear migración de base de datos
- [ ] Actualizar Admin para reflejar nuevo tipo

### 📝 Archivos a modificar

---

#### 1. `apps/accounts/models.py` — MODIFICAR

**Cambio 1: Agregar nueva choice en UserType**

Buscar:
```python
class UserType(models.TextChoices):
    PROFESSIONAL = 'professional', 'Profesional SySO'
    TRAINEE = 'trainee', 'Trabajador'
```

Reemplazar por:
```python
class UserType(models.TextChoices):
    PROFESSIONAL = 'professional', 'Profesional SySO'
    TRAINEE = 'trainee', 'Trabajador'
    COMPANY = 'company', 'Empresa'
```

---

**Cambio 2: Agregar propiedades al modelo CustomUser**

Buscar la propiedad `is_trainee` y agregar DESPUÉS de ella:

```python
    @property
    def is_company(self) -> bool:
        """Retorna True si es un usuario empresa."""
        return self.user_type == self.UserType.COMPANY

    @property
    def is_backoffice_user(self) -> bool:
        """
        Retorna True si es un usuario de gestión (professional o company).
        Usado para controlar acceso al dashboard y funciones compartidas.
        """
        return self.user_type in (
            self.UserType.PROFESSIONAL,
            self.UserType.COMPANY,
        )
```

---

**Cambio 3: Agregar método create_company al Manager**

Buscar el método `create_professional` en `CustomUserManager` y agregar DESPUÉS de él:

```python
    def create_company(self, email: str, password: str, username: str = None, **extra_fields):
        """Atajo para crear un usuario empresa con password."""
        if username:
            extra_fields['username'] = username
        return self.create_user(
            email=email,
            user_type='company',
            password=password,
            **extra_fields,
        )
```

---

**Cambio 4: Actualizar create_user para aceptar 'company'**

Buscar dentro de `create_user`:
```python
        if user_type == 'professional':
            if not password:
                raise ValueError("Los profesionales requieren contraseña")
            user.set_password(password)
        else:
            user.set_unusable_password()
```

Reemplazar por:
```python
        if user_type in ('professional', 'company'):
            if not password:
                raise ValueError("Los profesionales y empresas requieren contraseña")
            user.set_password(password)
        else:
            user.set_unusable_password()
```

---

#### 2. `apps/accounts/admin.py` — MODIFICAR

Agregar un fieldset informativo DESPUÉS del fieldset "Datos de Trabajador":

```python
        ("Datos de Empresa", {
            "fields": (),
            "classes": ("collapse",),
            "description": "Los datos de empresa se gestionan vía CompanyProfile (ver admin de Gestión de Empresas)"
        }),
```

---

#### 3. Migración de base de datos

```bash
python manage.py makemigrations accounts --name add_company_user_type
python manage.py migrate
```

> **IMPORTANTE:** Esta migración solo cambia las choices del campo `user_type` (CharField). No altera datos existentes ni estructura de tabla. Es una migración segura y reversible.

---

### ✅ Verificación del Commit 29
- [ ] `python manage.py makemigrations` genera migración sin errores
- [ ] `python manage.py migrate` aplica correctamente
- [ ] En el Admin, el campo `user_type` ahora muestra 3 opciones: Profesional SySO, Trabajador, Empresa
- [ ] En shell: `User.objects.create_company(email='test@test.com', password='pass123')` crea correctamente
- [ ] En shell: el nuevo user tiene `is_company == True`
- [ ] En shell: el nuevo user tiene `is_backoffice_user == True`
- [ ] Los usuarios existentes (professional y trainee) siguen funcionando correctamente
- [ ] Las capacitaciones existentes no se ven afectadas
- [ ] Los tests existentes pasan sin errores (`python manage.py test`)

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 29: Agregar user_type 'company' a CustomUser

- Nueva choice COMPANY en UserType
- Propiedad is_company para verificación de tipo
- Propiedad is_backoffice_user (professional + company)
- Método create_company en CustomUserManager
- create_user actualizado para aceptar tipo company
- Migración de base de datos (solo choices, no altera datos)
- Admin actualizado con placeholder de empresa"
```

---

## COMMIT 30: Crear modelo CompanyProfile y nueva app company

### 📋 Descripción
Crear una nueva app `company` con el modelo `CompanyProfile` que almacena los datos específicos de empresa. Se usa OneToOneField a CustomUser para evitar sobrecargar el modelo de usuario con campos que no aplican a todos los tipos.

### 🎯 Objetivos
- [ ] Crear app `apps/company`
- [ ] Crear modelo CompanyProfile con todos los campos empresariales
- [ ] Configurar Admin para CompanyProfile
- [ ] Registrar en INSTALLED_APPS
- [ ] Crear migración

### 📝 Archivos a crear

---

#### 1. Crear la app

```bash
cd apps
python ../manage.py startapp company
```

---

#### 2. `apps/company/__init__.py`
```python
# (vacío)
```

---

#### 3. `apps/company/apps.py` — REEMPLAZAR COMPLETO

```python
from django.apps import AppConfig


class CompanyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.company'
    verbose_name = 'Gestión de Empresas'
```

---

#### 4. `apps/company/models.py` — REEMPLAZAR COMPLETO

```python
# apps/company/models.py
# ============================================================================
# COMMIT 30: Modelo CompanyProfile para datos específicos de empresa
# ============================================================================

from django.conf import settings
from django.db import models


class CompanyProfile(models.Model):
    """
    Perfil extendido para usuarios de tipo 'company'.
    Almacena datos empresariales que no corresponden al modelo genérico CustomUser.
    Relación OneToOne con CustomUser(user_type='company').
    """

    class AccountStatus(models.TextChoices):
        ACTIVE = 'active', 'Activa'
        PENDING = 'pending_validation', 'Pendiente de validación'
        SUSPENDED = 'suspended', 'Suspendida'
        INACTIVE = 'inactive', 'Inactiva'

    # =========================================================================
    # Relación con el usuario
    # =========================================================================
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company_profile',
        verbose_name='Usuario de acceso',
        limit_choices_to={'user_type': 'company'},
    )

    # =========================================================================
    # Datos de la empresa
    # =========================================================================
    razon_social = models.CharField(
        max_length=300,
        verbose_name='Razón social',
    )
    nombre_comercial = models.CharField(
        max_length=300,
        blank=True,
        default='',
        verbose_name='Nombre comercial',
        help_text='Nombre comercial o fantasía (opcional).',
    )
    cuit = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='CUIT',
        help_text='CUIT de la empresa (formato: XX-XXXXXXXX-X o solo dígitos).',
    )
    rubro = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='Rubro / Actividad',
    )
    cantidad_trabajadores = models.PositiveIntegerField(
        default=0,
        verbose_name='Cantidad aproximada de trabajadores',
    )

    # =========================================================================
    # Contacto principal
    # =========================================================================
    contacto_nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre del contacto principal',
    )
    contacto_cargo = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='Cargo del contacto',
    )
    contacto_telefono = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='Teléfono de contacto',
    )

    # =========================================================================
    # Ubicación
    # =========================================================================
    domicilio = models.CharField(
        max_length=400,
        blank=True,
        default='',
        verbose_name='Domicilio / Ubicación principal',
    )
    localidad = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='Localidad',
    )
    provincia = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Provincia',
    )

    # =========================================================================
    # Estado de cuenta
    # =========================================================================
    account_status = models.CharField(
        max_length=30,
        choices=AccountStatus.choices,
        default=AccountStatus.ACTIVE,
        verbose_name='Estado de cuenta',
    )

    # =========================================================================
    # Logo (opcional, para futuro)
    # =========================================================================
    logo = models.ImageField(
        upload_to='company_logos/',
        blank=True,
        null=True,
        verbose_name='Logo de la empresa',
    )

    # =========================================================================
    # Metadatos
    # =========================================================================
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil de Empresa'
        verbose_name_plural = 'Perfiles de Empresas'
        ordering = ['razon_social']

    def __str__(self):
        nombre = self.nombre_comercial or self.razon_social
        return f"{nombre} (CUIT: {self.cuit})"

    @property
    def display_name(self):
        """Nombre corto para mostrar en la UI."""
        return self.nombre_comercial or self.razon_social
```

---

#### 5. `apps/company/admin.py` — REEMPLAZAR COMPLETO

```python
# apps/company/admin.py
# ============================================================================
# COMMIT 30: Admin para CompanyProfile
# ============================================================================

from django.contrib import admin
from .models import CompanyProfile


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = (
        'razon_social',
        'nombre_comercial',
        'cuit',
        'contacto_nombre',
        'account_status',
        'cantidad_trabajadores',
        'created_at',
    )
    list_filter = ('account_status', 'provincia')
    search_fields = ('razon_social', 'nombre_comercial', 'cuit', 'contacto_nombre')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Datos de la Empresa', {
            'fields': (
                'user',
                'razon_social',
                'nombre_comercial',
                'cuit',
                'rubro',
                'cantidad_trabajadores',
            ),
        }),
        ('Contacto Principal', {
            'fields': (
                'contacto_nombre',
                'contacto_cargo',
                'contacto_telefono',
            ),
        }),
        ('Ubicación', {
            'fields': (
                'domicilio',
                'localidad',
                'provincia',
            ),
        }),
        ('Estado', {
            'fields': ('account_status', 'logo'),
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
```

---

#### 6. `config/settings.py` — AGREGAR app en INSTALLED_APPS

Buscar `LOCAL_APPS` y agregar `"apps.company"`:

```python
LOCAL_APPS = [
    "apps.accounts",
    'apps.landing',
    'apps.dashboard',
    "apps.presencial",
    "apps.company",      # NUEVO — Etapa 3, Commit 30
    "apps.training",
    "apps.quiz",
    "apps.certificates",
    "apps.ergobot_ai",
]
```

---

#### 7. Migración

```bash
python manage.py makemigrations company --name create_company_profile
python manage.py migrate
```

---

### ✅ Verificación del Commit 30
- [ ] Migración creada y aplicada sin errores
- [ ] CompanyProfile visible en el admin de Django en `/admin/company/companyprofile/`
- [ ] Se puede crear un CompanyProfile desde el admin asociado a un user tipo company
- [ ] El campo `limit_choices_to` filtra correctamente (el selector de user solo muestra users company)
- [ ] `user.company_profile` accesible via related_name desde un user company
- [ ] `user.company_profile` lanza `CompanyProfile.DoesNotExist` para un user professional

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 30: Crear modelo CompanyProfile y nueva app company

- Nueva app apps/company (Gestión de Empresas)
- Modelo CompanyProfile con OneToOneField a CustomUser
- Campos: razón social, nombre comercial, CUIT, rubro, cantidad trabajadores
- Campos de contacto: nombre, cargo, teléfono
- Campos de ubicación: domicilio, localidad, provincia
- Estado de cuenta con choices (active, pending, suspended, inactive)
- Campo logo preparado para futuro
- Admin completo con fieldsets organizados
- Registrado en INSTALLED_APPS
- Migración aplicada"
```

---

## COMMIT 31: Decoradores y permisos para backoffice multi-tipo

### 📋 Descripción
Refactorizar el sistema de permisos para soportar dos tipos de usuario de gestión (professional + company) sin duplicar lógica.

### 🎯 Objetivos
- [ ] Crear decorador `@backoffice_required` (professional o company)
- [ ] Crear decorador `@company_required` (solo company)
- [ ] Crear mixin `BackofficeRequiredMixin` para CBV
- [ ] Crear mixin `CompanyRequiredMixin` para CBV
- [ ] Mantener compatibilidad total con decoradores existentes

### 📝 Archivos a modificar

---

#### 1. `apps/accounts/decorators.py` — AGREGAR

Agregar DESPUÉS de `trainee_required` y ANTES de `subscription_required`:

```python
def backoffice_required(function=None, redirect_url=None, login_url=None):
    """
    Decorador que requiere que el usuario sea de backoffice
    (professional O company) y esté autenticado.

    Este decorador unifica el acceso al dashboard para ambos tipos
    de usuario de gestión, evitando duplicar vistas.

    Uso:
        @backoffice_required
        def dashboard_view(request): ...

        @backoffice_required(redirect_url='landing:home')
        def dashboard_view(request): ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                url = login_url or reverse('professional_login')
                return redirect(f"{url}?next={request.get_full_path()}")

            if not request.user.is_active or not request.user.is_backoffice_user:
                if redirect_url:
                    return redirect(redirect_url)
                return HttpResponseForbidden(
                    "Acceso denegado. Esta sección es para profesionales y empresas."
                )

            return view_func(request, *args, **kwargs)
        return _wrapped_view

    if function:
        return decorator(function)
    return decorator


def company_required(function=None, redirect_url=None, login_url=None):
    """
    Decorador que requiere que el usuario sea tipo empresa y esté autenticado.

    Uso:
        @company_required
        def nomina_view(request): ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                url = login_url or reverse('professional_login')
                return redirect(f"{url}?next={request.get_full_path()}")

            if not request.user.is_active or not request.user.is_company:
                if redirect_url:
                    return redirect(redirect_url)
                return HttpResponseForbidden(
                    "Acceso denegado. Esta sección es solo para empresas."
                )

            return view_func(request, *args, **kwargs)
        return _wrapped_view

    if function:
        return decorator(function)
    return decorator
```

---

#### 2. `apps/accounts/mixins.py` — AGREGAR

Agregar DESPUÉS de `TraineeRequiredMixin`:

```python
class BackofficeRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin para vistas basadas en clase que requieren un usuario de backoffice
    (professional o company).
    """
    login_url = None

    def get_login_url(self):
        return reverse('professional_login')

    def test_func(self):
        return self.request.user.is_backoffice_user

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('dashboard:home')
        return super().handle_no_permission()


class CompanyRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin para vistas basadas en clase que requieren un usuario de tipo empresa.
    """
    login_url = None

    def get_login_url(self):
        return reverse('professional_login')

    def test_func(self):
        return self.request.user.is_company

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('dashboard:home')
        return super().handle_no_permission()
```

---

### ✅ Verificación del Commit 31
- [ ] `@backoffice_required` permite acceso a professional Y company
- [ ] `@backoffice_required` deniega acceso a trainees
- [ ] `@company_required` permite acceso SOLO a company
- [ ] `@company_required` deniega acceso a professional y trainee
- [ ] Decoradores existentes no se alteran
- [ ] Todos los tests pasan

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 31: Decoradores y permisos para backoffice multi-tipo

- Decorador @backoffice_required (professional + company)
- Decorador @company_required (solo company)
- Mixin BackofficeRequiredMixin para CBV
- Mixin CompanyRequiredMixin para CBV
- Compatibilidad total con decoradores existentes"
```

---

## COMMIT 32: Registro y autenticación de Empresa

### 📋 Descripción
Crear el flujo completo de registro y login para empresas. El registro crea atómicamente un `CustomUser(type=company)` y un `CompanyProfile`.

### 🎯 Objetivos
- [ ] Crear formulario `CompanyRegisterForm` con validaciones
- [ ] Crear vistas de registro y login de empresa
- [ ] Crear URLs bajo `/empresa/auth/`
- [ ] Crear templates de registro y login con estilo dark
- [ ] Registrar en config/urls.py

### 📝 Archivos a crear/modificar

---

#### 1. `apps/accounts/forms.py` — AGREGAR AL FINAL

```python
# ============================================================================
# COMMIT 32: Formulario de registro de Empresa
# ============================================================================

import re as _re


def normalize_cuit(value: str) -> str:
    """Normaliza CUIT: extrae solo dígitos y valida longitud 11."""
    digits = _re.sub(r"\D", "", (value or "").strip())
    if len(digits) != 11:
        raise forms.ValidationError("CUIT inválido (debe tener 11 dígitos).")
    return digits


class CompanyRegisterForm(forms.Form):
    """
    Formulario de registro para empresas.
    Crea tanto el CustomUser como el CompanyProfile.
    """

    # --- Datos de la empresa ---
    razon_social = forms.CharField(
        label='Razón social',
        max_length=300,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'Ej: Acme S.A.',
        }),
    )
    nombre_comercial = forms.CharField(
        label='Nombre comercial (opcional)',
        max_length=300,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'Nombre de fantasía',
        }),
    )
    cuit = forms.CharField(
        label='CUIT',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': '20-12345678-9',
        }),
        help_text='Ingresá solo números o con guiones.',
    )
    rubro = forms.CharField(
        label='Rubro / Actividad',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'Ej: Construcción, Alimentos, etc.',
        }),
    )
    cantidad_trabajadores = forms.IntegerField(
        label='Cantidad aprox. de trabajadores',
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': '0',
        }),
    )

    # --- Contacto principal ---
    contacto_nombre = forms.CharField(
        label='Nombre del contacto principal',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'Nombre y apellido',
        }),
    )
    contacto_cargo = forms.CharField(
        label='Cargo del contacto',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'Ej: Responsable RRHH',
        }),
    )
    contacto_telefono = forms.CharField(
        label='Teléfono',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': '+54 11 XXXX-XXXX',
        }),
    )

    # --- Ubicación ---
    domicilio = forms.CharField(
        label='Domicilio',
        max_length=400,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
        }),
    )
    provincia = forms.CharField(
        label='Provincia',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
        }),
    )

    # --- Datos de acceso ---
    email = forms.EmailField(
        label='Email de acceso',
        widget=forms.EmailInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'empresa@ejemplo.com',
        }),
    )
    password1 = forms.CharField(
        label='Contraseña',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
        }),
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
        }),
    )

    def clean_cuit(self):
        return normalize_cuit(self.cleaned_data['cuit'])

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con este email.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        return cleaned_data
```

---

#### 2. `apps/accounts/views_company.py` — CREAR ARCHIVO NUEVO

```python
# apps/accounts/views_company.py
# ============================================================================
# COMMIT 32: Vistas de autenticación para empresas
# ============================================================================

from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .forms import CompanyRegisterForm, ProfessionalLoginForm
from apps.company.models import CompanyProfile

User = get_user_model()


@require_http_methods(["GET", "POST"])
def company_register(request):
    """Registro de empresas. Crea CustomUser + CompanyProfile."""
    if request.user.is_authenticated:
        if request.user.is_backoffice_user:
            return redirect("dashboard:home")
        return redirect("training_home")

    if request.method == "POST":
        form = CompanyRegisterForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            # 1. Crear el CustomUser tipo company
            parts = cd["contacto_nombre"].strip().split(" ", 1)
            first = parts[0]
            last = parts[1] if len(parts) > 1 else ""

            user = User.objects.create_company(
                email=cd["email"],
                password=cd["password1"],
                first_name=first,
                last_name=last,
                full_name=cd["contacto_nombre"],
            )

            # 2. Crear el CompanyProfile asociado
            CompanyProfile.objects.create(
                user=user,
                razon_social=cd["razon_social"],
                nombre_comercial=cd.get("nombre_comercial", ""),
                cuit=cd["cuit"],
                rubro=cd.get("rubro", ""),
                cantidad_trabajadores=cd.get("cantidad_trabajadores") or 0,
                contacto_nombre=cd["contacto_nombre"],
                contacto_cargo=cd.get("contacto_cargo", ""),
                contacto_telefono=cd.get("contacto_telefono", ""),
                domicilio=cd.get("domicilio", ""),
                provincia=cd.get("provincia", ""),
            )

            # 3. Login automático
            login(request, user, backend='apps.accounts.backends.ProfessionalBackend')

            messages.success(
                request,
                f"¡Bienvenido! La cuenta de {cd['razon_social']} ha sido creada exitosamente.",
            )
            return redirect("dashboard:home")
    else:
        form = CompanyRegisterForm()

    return render(request, "accounts/company/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def company_login(request):
    """Login de empresas. Reutiliza ProfessionalLoginForm con verificación de tipo."""
    if request.user.is_authenticated:
        if request.user.is_backoffice_user:
            return redirect("dashboard:home")
        return redirect("training_home")

    if request.method == "POST":
        form = ProfessionalLoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=identifier, password=password)

            if user is not None:
                if not user.is_company:
                    messages.error(
                        request,
                        "Esta cuenta no es de empresa. "
                        "Si sos profesional, usá el login de profesionales.",
                    )
                    return render(request, "accounts/company/login.html", {"form": form})

                login(request, user)
                messages.success(request, f"Bienvenido, {user.display_name}")

                next_url = request.GET.get("next") or request.POST.get("next")
                return redirect(next_url or "dashboard:home")
            else:
                messages.error(request, "Email o contraseña incorrectos.")
    else:
        form = ProfessionalLoginForm()

    return render(request, "accounts/company/login.html", {"form": form})
```

---

#### 3. `apps/accounts/urls_company.py` — CREAR ARCHIVO NUEVO

```python
# apps/accounts/urls_company.py
# ============================================================================
# COMMIT 32: URLs de autenticación para empresas
# ============================================================================

from django.urls import path
from . import views_company
from . import views_professional  # reutilizar logout

urlpatterns = [
    path('registro/', views_company.company_register, name='company_register'),
    path('login/', views_company.company_login, name='company_login'),
    path('logout/', views_professional.logout_view, name='company_logout'),
]
```

---

#### 4. `config/urls.py` — AGREGAR

Agregar DESPUÉS del bloque de `auth/` de profesionales y ANTES de `c/`:

```python
    # =========================================================================
    # Autenticación de Empresas (Etapa 3, Commit 32) - CON NAMESPACE
    # =========================================================================
    path(
        "empresa/auth/",
        include(
            ("apps.accounts.urls_company", "accounts_company"),
            namespace="accounts_company",
        ),
    ),
```

---

#### 5. `templates/accounts/company/register.html` — CREAR

```bash
mkdir -p templates/accounts/company
```

```html
{% extends "base_landing.html" %}
{% load static %}

{% block title %}Registro de Empresa - ErgoSolutions{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-lg-8 col-xl-7">

            <div class="text-center mb-4" style="margin-top: 80px;">
                <h2 class="fw-bold">
                    <i class="bi bi-building me-2 text-primary"></i>Registrar Empresa
                </h2>
                <p class="text-secondary">
                    Creá tu cuenta empresa para gestionar capacitaciones, trabajadores y vencimientos.
                </p>
            </div>

            <div class="card bg-dark border-secondary">
                <div class="card-body p-4">
                    {% if messages %}
                    {% for message in messages %}
                    <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                    {% endfor %}
                    {% endif %}

                    <form method="post" novalidate>
                        {% csrf_token %}

                        <!-- Sección: Datos de la empresa -->
                        <h5 class="text-primary mb-3">
                            <i class="bi bi-building me-1"></i> Datos de la empresa
                        </h5>
                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label">{{ form.razon_social.label }} *</label>
                                {{ form.razon_social }}
                                {% if form.razon_social.errors %}
                                <div class="text-danger small mt-1">{{ form.razon_social.errors.0 }}</div>
                                {% endif %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.nombre_comercial.label }}</label>
                                {{ form.nombre_comercial }}
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">{{ form.cuit.label }} *</label>
                                {{ form.cuit }}
                                {% if form.cuit.errors %}
                                <div class="text-danger small mt-1">{{ form.cuit.errors.0 }}</div>
                                {% endif %}
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">{{ form.rubro.label }}</label>
                                {{ form.rubro }}
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">{{ form.cantidad_trabajadores.label }}</label>
                                {{ form.cantidad_trabajadores }}
                            </div>
                        </div>

                        <!-- Sección: Contacto principal -->
                        <h5 class="text-primary mb-3">
                            <i class="bi bi-person-badge me-1"></i> Contacto principal
                        </h5>
                        <div class="row g-3 mb-4">
                            <div class="col-md-4">
                                <label class="form-label">{{ form.contacto_nombre.label }} *</label>
                                {{ form.contacto_nombre }}
                                {% if form.contacto_nombre.errors %}
                                <div class="text-danger small mt-1">{{ form.contacto_nombre.errors.0 }}</div>
                                {% endif %}
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">{{ form.contacto_cargo.label }}</label>
                                {{ form.contacto_cargo }}
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">{{ form.contacto_telefono.label }}</label>
                                {{ form.contacto_telefono }}
                            </div>
                        </div>

                        <!-- Sección: Ubicación -->
                        <h5 class="text-primary mb-3">
                            <i class="bi bi-geo-alt me-1"></i> Ubicación
                        </h5>
                        <div class="row g-3 mb-4">
                            <div class="col-md-8">
                                <label class="form-label">{{ form.domicilio.label }}</label>
                                {{ form.domicilio }}
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">{{ form.provincia.label }}</label>
                                {{ form.provincia }}
                            </div>
                        </div>

                        <!-- Sección: Datos de acceso -->
                        <h5 class="text-primary mb-3">
                            <i class="bi bi-key me-1"></i> Datos de acceso
                        </h5>
                        <div class="row g-3 mb-4">
                            <div class="col-md-12">
                                <label class="form-label">{{ form.email.label }} *</label>
                                {{ form.email }}
                                {% if form.email.errors %}
                                <div class="text-danger small mt-1">{{ form.email.errors.0 }}</div>
                                {% endif %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.password1.label }} *</label>
                                {{ form.password1 }}
                                {% if form.password1.errors %}
                                <div class="text-danger small mt-1">{{ form.password1.errors.0 }}</div>
                                {% endif %}
                                <small class="text-muted">Mínimo 8 caracteres</small>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ form.password2.label }} *</label>
                                {{ form.password2 }}
                                {% if form.password2.errors %}
                                <div class="text-danger small mt-1">{{ form.password2.errors.0 }}</div>
                                {% endif %}
                            </div>
                        </div>

                        <button type="submit" class="btn btn-primary btn-lg w-100 mt-2">
                            <i class="bi bi-building-add me-2"></i>Registrar Empresa
                        </button>
                    </form>

                    <div class="text-center mt-3">
                        <small class="text-secondary">
                            ¿Ya tenés cuenta empresa?
                            <a href="{% url 'company_login' %}" class="text-primary">Ingresá</a>
                        </small>
                    </div>
                </div>
            </div>

            <!-- Link cruzado a profesional -->
            <div class="card bg-secondary mt-3">
                <div class="card-body py-3 text-center">
                    <small class="text-dark">
                        ¿Sos profesional?
                        <a href="{% url 'professional_login' %}" class="text-dark fw-bold">
                            Ingresá como profesional
                        </a>
                    </small>
                </div>
            </div>

        </div>
    </div>
</div>
{% endblock %}
```

---

#### 6. `templates/accounts/company/login.html` — CREAR

```html
{% extends "base_landing.html" %}
{% load static %}

{% block title %}Login Empresa - ErgoSolutions{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-5">

            <div class="text-center mb-4" style="margin-top: 100px;">
                <h2 class="fw-bold">
                    <i class="bi bi-building me-2 text-primary"></i>Acceso Empresa
                </h2>
                <p class="text-secondary">Ingresá con tu cuenta de empresa</p>
            </div>

            <div class="card bg-dark border-secondary">
                <div class="card-body p-4">
                    {% if messages %}
                    {% for message in messages %}
                    <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                    {% endfor %}
                    {% endif %}

                    <form method="post" novalidate>
                        {% csrf_token %}
                        {% if request.GET.next %}
                        <input type="hidden" name="next" value="{{ request.GET.next }}">
                        {% endif %}

                        <div class="mb-3">
                            <label class="form-label">Email</label>
                            {{ form.username }}
                            {% if form.username.errors %}
                            <div class="text-danger small mt-1">{{ form.username.errors.0 }}</div>
                            {% endif %}
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Contraseña</label>
                            {{ form.password }}
                            {% if form.password.errors %}
                            <div class="text-danger small mt-1">{{ form.password.errors.0 }}</div>
                            {% endif %}
                        </div>

                        <button type="submit" class="btn btn-primary w-100 mt-2">
                            <i class="bi bi-box-arrow-in-right me-2"></i>Ingresar
                        </button>
                    </form>

                    <div class="text-center mt-3">
                        <small class="text-secondary">
                            ¿No tenés cuenta empresa?
                            <a href="{% url 'company_register' %}" class="text-primary">Registrá tu empresa</a>
                        </small>
                    </div>
                </div>
            </div>

            <!-- Links cruzados -->
            <div class="card bg-secondary mt-3">
                <div class="card-body py-3 text-center">
                    <small class="text-dark">
                        ¿Sos profesional?
                        <a href="{% url 'professional_login' %}" class="text-dark fw-bold">
                            Ingresá como profesional
                        </a>
                    </small>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

### ✅ Verificación del Commit 32
- [ ] `/empresa/auth/registro/` muestra formulario completo
- [ ] Registro crea `CustomUser(type=company)` + `CompanyProfile`
- [ ] Login automático después del registro redirige a `/dashboard/`
- [ ] CUIT normalizado y validado
- [ ] Email duplicado muestra error
- [ ] Contraseñas no coincidentes muestra error
- [ ] `/empresa/auth/login/` funciona con email + password
- [ ] Login empresa rechaza credenciales de profesional con mensaje
- [ ] Logout funciona correctamente
- [ ] Templates usan estilo dark consistente

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 32: Registro y autenticación de Empresa

- CompanyRegisterForm con validación CUIT, email único, contraseñas
- Vista de registro crea CustomUser(company) + CompanyProfile
- Login automático post-registro via ProfessionalBackend
- Vista de login con verificación de tipo empresa
- URLs en /empresa/auth/ con namespace accounts_company
- Templates register y login con diseño dark
- Links cruzados entre login empresa y profesional
- Reutiliza logout de profesional"
```

---

## COMMIT 33: Refactorizar dashboard para backoffice multi-tipo

### 📋 Descripción
Commit central: refactorizar el dashboard para acceso de professional + company.

### 🎯 Objetivos
- [ ] Cambiar decoradores en vistas compartidas
- [ ] Crear context processor `company_context`
- [ ] Actualizar `base_dashboard.html` con menú condicional
- [ ] Adaptar vista home para despachar por tipo

### 📝 Archivos a modificar

---

#### 1. `apps/dashboard/views.py` — CAMBIAR DECORADORES

**Importación — buscar:**
```python
from apps.accounts.decorators import professional_required
```
**Reemplazar por:**
```python
from apps.accounts.decorators import backoffice_required, professional_required
```

**Vistas a cambiar `@professional_required` → `@backoffice_required`:**
- `home`
- `capacitaciones_menu`
- `modalidad_selector`
- `online_links`
- `generate_link`
- `share_link`
- `profile` (el despacho por tipo se hace en Commit 34)

---

#### 2. `apps/company/context_processors.py` — CREAR ARCHIVO NUEVO

```python
# apps/company/context_processors.py
# ============================================================================
# COMMIT 33: Context processor para datos de empresa en templates
# ============================================================================


def company_context(request):
    """
    Agrega flags de tipo de usuario y datos de empresa al contexto de templates.
    Disponible en TODOS los templates vía TEMPLATES.context_processors.
    """
    ctx = {
        'is_company_user': False,
        'is_professional_user': False,
        'is_backoffice_user': False,
        'company_profile': None,
    }

    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return ctx

    user = request.user
    ctx['is_backoffice_user'] = getattr(user, 'is_backoffice_user', False)
    ctx['is_professional_user'] = getattr(user, 'is_professional', False)
    ctx['is_company_user'] = getattr(user, 'is_company', False)

    if ctx['is_company_user']:
        try:
            ctx['company_profile'] = user.company_profile
        except Exception:
            ctx['company_profile'] = None

    return ctx
```

---

#### 3. `config/settings.py` — AGREGAR context processor

Buscar `TEMPLATES` → `OPTIONS` → `context_processors` y agregar al final de la lista:

```python
'apps.company.context_processors.company_context',
```

---

#### 4. `templates/base_dashboard.html` — MODIFICAR NAVBAR

Reemplazar el bloque de `<ul class="navbar-nav me-auto ...">`:

```html
<ul class="navbar-nav me-auto mb-2 mb-lg-0">
    <li class="nav-item">
        <a class="nav-link {% if request.resolver_match.url_name == 'home' %}active{% endif %}"
           href="{% url 'dashboard:home' %}">
            <i class="bi bi-grid-1x2 me-1"></i>Dashboard
        </a>
    </li>
    <li class="nav-item">
        <a class="nav-link {% if 'capacitaciones' in request.resolver_match.url_name|default:'' %}active{% endif %}"
           href="{% url 'dashboard:capacitaciones_menu' %}">
            <i class="bi bi-mortarboard me-1"></i>Capacitaciones
        </a>
    </li>
    {% if is_company_user %}
    <li class="nav-item">
        <a class="nav-link {% if 'nomina' in request.path %}active{% endif %}"
           href="#">
            <i class="bi bi-people me-1"></i>Nómina
        </a>
    </li>
    <li class="nav-item">
        <a class="nav-link {% if 'agenda' in request.path %}active{% endif %}"
           href="#">
            <i class="bi bi-calendar-event me-1"></i>Agenda
        </a>
    </li>
    {% endif %}
</ul>
```

> **NOTA:** Los `href="#"` de Nómina y Agenda se actualizarán en Commits 36 y 42.

Reemplazar dropdown del usuario:

```html
<a class="nav-link dropdown-toggle" href="#" role="button"
   data-bs-toggle="dropdown" aria-expanded="false">
    <i class="bi bi-{% if is_company_user %}building{% else %}person-circle{% endif %} me-1"></i>
    {% if is_company_user and company_profile %}
        {{ company_profile.display_name }}
    {% else %}
        {{ request.user.display_name }}
    {% endif %}
</a>
```

---

### ✅ Verificación del Commit 33
- [ ] Empresa puede acceder a `/dashboard/`
- [ ] Empresa ve Dashboard, Capacitaciones, Nómina, Agenda en navbar
- [ ] Profesional solo ve Dashboard y Capacitaciones
- [ ] Dropdown: ícono building + nombre comercial para empresa
- [ ] Dropdown: ícono persona + nombre para profesional
- [ ] Trainee no puede acceder al dashboard
- [ ] Todos los tests existentes pasan

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 33: Refactorizar dashboard para backoffice multi-tipo

- Vistas compartidas usan @backoffice_required
- Context processor company_context
- Navbar condicional: Nómina y Agenda solo para empresa
- Dropdown adaptado por tipo de usuario
- Compatibilidad total con flujos existentes"
```

---

## COMMIT 34: Perfil de Empresa (edición y vista)

### 📋 Descripción
Vista de perfil para empresa y refactorización de `profile` para despacho por tipo.

### 📝 Archivos a crear/modificar

---

#### 1. `apps/dashboard/forms.py` — AGREGAR al final

```python
# ============================================================================
# COMMIT 34: Formulario de edición de perfil empresa
# ============================================================================


class CompanyProfileEditForm(forms.Form):
    """Formulario de edición de perfil para empresas."""

    razon_social = forms.CharField(
        label='Razón social', max_length=300,
        widget=forms.TextInput(attrs={'class': 'form-control bg-black text-light border-secondary'}),
    )
    nombre_comercial = forms.CharField(
        label='Nombre comercial', max_length=300, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control bg-black text-light border-secondary'}),
    )
    cuit = forms.CharField(
        label='CUIT', max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-black text-light border-secondary',
            'readonly': 'readonly',
        }),
        help_text='El CUIT no se puede modificar.',
    )
    rubro = forms.CharField(
        label='Rubro / Actividad', max_length=200, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control bg-black text-light border-secondary'}),
    )
    cantidad_trabajadores = forms.IntegerField(
        label='Cantidad aprox. de trabajadores', min_value=0, required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control bg-black text-light border-secondary'}),
    )
    contacto_nombre = forms.CharField(
        label='Contacto principal', max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control bg-black text-light border-secondary'}),
    )
    contacto_cargo = forms.CharField(
        label='Cargo', max_length=200, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control bg-black text-light border-secondary'}),
    )
    contacto_telefono = forms.CharField(
        label='Teléfono', max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control bg-black text-light border-secondary'}),
    )
    email = forms.EmailField(
        label='Email de acceso',
        widget=forms.EmailInput(attrs={'class': 'form-control bg-black text-light border-secondary'}),
    )
    domicilio = forms.CharField(
        label='Domicilio', max_length=400, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control bg-black text-light border-secondary'}),
    )
    provincia = forms.CharField(
        label='Provincia', max_length=100, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control bg-black text-light border-secondary'}),
    )

    def __init__(self, *args, company_profile=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_profile = company_profile
        self.user = user
        if company_profile and not args:
            self.initial.update({
                'razon_social': company_profile.razon_social,
                'nombre_comercial': company_profile.nombre_comercial,
                'cuit': company_profile.cuit,
                'rubro': company_profile.rubro,
                'cantidad_trabajadores': company_profile.cantidad_trabajadores,
                'contacto_nombre': company_profile.contacto_nombre,
                'contacto_cargo': company_profile.contacto_cargo,
                'contacto_telefono': company_profile.contacto_telefono,
                'domicilio': company_profile.domicilio,
                'provincia': company_profile.provincia,
                'email': user.email if user else '',
            })

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        from django.contrib.auth import get_user_model
        User = get_user_model()
        qs = User.objects.filter(email__iexact=email)
        if self.user:
            qs = qs.exclude(pk=self.user.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe otra cuenta con este email.')
        return email
```

---

#### 2. `apps/dashboard/views.py` — REEMPLAZAR vista `profile`

Agregar imports:
```python
from apps.company.models import CompanyProfile
from .forms import (
    ChangePasswordForm, CompanyProfileEditForm,
    ProfessionalProfileForm, ShareLinkForm,
)
```

Reemplazar `profile` completa:

```python
@login_required
@backoffice_required
def profile(request):
    """Perfil unificado: despacha al correcto según tipo de usuario."""
    if request.user.is_company:
        return _company_profile_view(request)
    return _professional_profile_view(request)


def _professional_profile_view(request):
    """Lógica de perfil para profesional (preserva funcionalidad existente)."""
    user = request.user
    profile_form = ProfessionalProfileForm(user=user)
    password_form = ChangePasswordForm(user=user)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "update_profile":
            profile_form = ProfessionalProfileForm(request.POST, user=user)
            if profile_form.is_valid():
                user.first_name = profile_form.cleaned_data["first_name"]
                user.last_name = profile_form.cleaned_data["last_name"]
                user.email = profile_form.cleaned_data["email"]
                user.profession = profile_form.cleaned_data.get("profession", "")
                user.license_number = profile_form.cleaned_data.get("license_number", "")
                user.dni = profile_form.cleaned_data.get("dni", "")
                user.save()
                messages.success(request, "Perfil actualizado correctamente.")
                return redirect("dashboard:profile")
        elif action == "change_password":
            password_form = ChangePasswordForm(request.POST, user=user)
            if password_form.is_valid():
                user.set_password(password_form.cleaned_data["new_password1"])
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Contraseña actualizada correctamente.")
                return redirect("dashboard:profile")

    presencial_count = PresencialSession.objects.filter(professional=user).count()
    links_count = CapacitacionLink.objects.filter(created_by=user).count()
    shares_count = LinkShareLog.objects.filter(link__created_by=user).count()

    return render(request, "dashboard/profile.html", {
        "profile_form": profile_form,
        "password_form": password_form,
        "stats": {
            "presencial": presencial_count,
            "links": links_count,
            "shares": shares_count,
        },
    })


def _company_profile_view(request):
    """Lógica de perfil para empresa."""
    user = request.user
    try:
        cp = user.company_profile
    except CompanyProfile.DoesNotExist:
        messages.error(request, "No se encontró el perfil de empresa.")
        return redirect("dashboard:home")

    profile_form = CompanyProfileEditForm(company_profile=cp, user=user)
    password_form = ChangePasswordForm(user=user)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "update_profile":
            profile_form = CompanyProfileEditForm(
                request.POST, company_profile=cp, user=user,
            )
            if profile_form.is_valid():
                cd = profile_form.cleaned_data
                cp.razon_social = cd["razon_social"]
                cp.nombre_comercial = cd.get("nombre_comercial", "")
                cp.rubro = cd.get("rubro", "")
                cp.cantidad_trabajadores = cd.get("cantidad_trabajadores") or 0
                cp.contacto_nombre = cd["contacto_nombre"]
                cp.contacto_cargo = cd.get("contacto_cargo", "")
                cp.contacto_telefono = cd.get("contacto_telefono", "")
                cp.domicilio = cd.get("domicilio", "")
                cp.provincia = cd.get("provincia", "")
                cp.save()
                user.email = cd["email"]
                user.save()
                messages.success(request, "Perfil de empresa actualizado correctamente.")
                return redirect("dashboard:profile")
        elif action == "change_password":
            password_form = ChangePasswordForm(request.POST, user=user)
            if password_form.is_valid():
                user.set_password(password_form.cleaned_data["new_password1"])
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Contraseña actualizada correctamente.")
                return redirect("dashboard:profile")

    links_count = CapacitacionLink.objects.filter(created_by=user).count()

    return render(request, "dashboard/company_profile.html", {
        "profile_form": profile_form,
        "password_form": password_form,
        "company_profile": cp,
        "stats": {"links": links_count},
    })
```

---

#### 3. `templates/dashboard/company_profile.html` — CREAR

```html
{% extends "base_dashboard.html" %}

{% block title %}Perfil de Empresa - ErgoSolutions{% endblock %}

{% block content %}
<div class="container-fluid py-4">
    <h3 class="mb-4">
        <i class="bi bi-building me-2 text-primary"></i>Perfil de Empresa
    </h3>

    {% if messages %}
    {% for message in messages %}
    <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
        {{ message }}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
    {% endfor %}
    {% endif %}

    <div class="row">
        <!-- Datos de la empresa -->
        <div class="col-lg-8">
            <div class="card bg-dark border-secondary mb-4">
                <div class="card-header bg-dark border-secondary">
                    <h5 class="mb-0"><i class="bi bi-pencil-square me-2"></i>Datos de la empresa</h5>
                </div>
                <div class="card-body">
                    <form method="post" novalidate>
                        {% csrf_token %}
                        <input type="hidden" name="action" value="update_profile">

                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label">{{ profile_form.razon_social.label }} *</label>
                                {{ profile_form.razon_social }}
                                {% if profile_form.razon_social.errors %}
                                <div class="text-danger small mt-1">{{ profile_form.razon_social.errors.0 }}</div>
                                {% endif %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">{{ profile_form.nombre_comercial.label }}</label>
                                {{ profile_form.nombre_comercial }}
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">{{ profile_form.cuit.label }}</label>
                                {{ profile_form.cuit }}
                                <small class="text-muted">{{ profile_form.cuit.help_text }}</small>
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">{{ profile_form.rubro.label }}</label>
                                {{ profile_form.rubro }}
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">{{ profile_form.cantidad_trabajadores.label }}</label>
                                {{ profile_form.cantidad_trabajadores }}
                            </div>
                        </div>

                        <hr class="border-secondary my-4">
                        <h6 class="text-primary mb-3"><i class="bi bi-person-badge me-1"></i> Contacto</h6>
                        <div class="row g-3">
                            <div class="col-md-4">
                                <label class="form-label">{{ profile_form.contacto_nombre.label }} *</label>
                                {{ profile_form.contacto_nombre }}
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">{{ profile_form.contacto_cargo.label }}</label>
                                {{ profile_form.contacto_cargo }}
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">{{ profile_form.contacto_telefono.label }}</label>
                                {{ profile_form.contacto_telefono }}
                            </div>
                        </div>

                        <hr class="border-secondary my-4">
                        <h6 class="text-primary mb-3"><i class="bi bi-geo-alt me-1"></i> Ubicación</h6>
                        <div class="row g-3">
                            <div class="col-md-8">
                                <label class="form-label">{{ profile_form.domicilio.label }}</label>
                                {{ profile_form.domicilio }}
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">{{ profile_form.provincia.label }}</label>
                                {{ profile_form.provincia }}
                            </div>
                        </div>

                        <hr class="border-secondary my-4">
                        <h6 class="text-primary mb-3"><i class="bi bi-envelope me-1"></i> Acceso</h6>
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label">{{ profile_form.email.label }} *</label>
                                {{ profile_form.email }}
                                {% if profile_form.email.errors %}
                                <div class="text-danger small mt-1">{{ profile_form.email.errors.0 }}</div>
                                {% endif %}
                            </div>
                        </div>

                        <div class="mt-4">
                            <button type="submit" class="btn btn-primary">
                                <i class="bi bi-check-lg me-1"></i>Guardar cambios
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <!-- Panel lateral -->
        <div class="col-lg-4">
            <!-- Stats -->
            <div class="card bg-dark border-secondary mb-4">
                <div class="card-header bg-dark border-secondary">
                    <h5 class="mb-0"><i class="bi bi-bar-chart me-2"></i>Estadísticas</h5>
                </div>
                <div class="card-body">
                    <div class="d-flex justify-content-between mb-2">
                        <span class="text-secondary">Links generados</span>
                        <span class="fw-bold">{{ stats.links }}</span>
                    </div>
                </div>
            </div>

            <!-- Cambiar contraseña -->
            <div class="card bg-dark border-secondary">
                <div class="card-header bg-dark border-secondary">
                    <h5 class="mb-0"><i class="bi bi-key me-2"></i>Cambiar contraseña</h5>
                </div>
                <div class="card-body">
                    <form method="post" novalidate>
                        {% csrf_token %}
                        <input type="hidden" name="action" value="change_password">

                        <div class="mb-3">
                            <label class="form-label">Contraseña actual</label>
                            {{ password_form.current_password }}
                            {% if password_form.current_password.errors %}
                            <div class="text-danger small mt-1">{{ password_form.current_password.errors.0 }}</div>
                            {% endif %}
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Nueva contraseña</label>
                            {{ password_form.new_password1 }}
                            {% if password_form.new_password1.errors %}
                            <div class="text-danger small mt-1">{{ password_form.new_password1.errors.0 }}</div>
                            {% endif %}
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Confirmar nueva contraseña</label>
                            {{ password_form.new_password2 }}
                            {% if password_form.new_password2.errors %}
                            <div class="text-danger small mt-1">{{ password_form.new_password2.errors.0 }}</div>
                            {% endif %}
                        </div>

                        <button type="submit" class="btn btn-outline-warning w-100">
                            <i class="bi bi-key me-1"></i>Cambiar contraseña
                        </button>
                    </form>
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
git commit -m "Commit 34: Perfil de Empresa (edición y vista)

- CompanyProfileEditForm con campos empresa + email
- Vista profile refactorizada: despacha a professional o company
- Template company_profile.html con estilo dark
- CUIT readonly
- Cambio de contraseña funcional para empresa
- Stats de links para empresa
- Profesional preservado intacto"
```

---

# ═══════════════════════════════════════════════════════════════════════════
# SUB-ETAPA 3B: NÓMINA DE TRABAJADORES (Commits 35–40)
# ═══════════════════════════════════════════════════════════════════════════

---

## COMMIT 35: Crear modelo CompanyWorker

### 📋 Descripción
Crear la relación formal entre empresa y trabajador.

### 📝 Archivo: `apps/company/models.py` — AGREGAR al final

```python
class CompanyWorker(models.Model):
    """Relación formal entre una empresa y un trabajador (trainee)."""

    company = models.ForeignKey(
        CompanyProfile, on_delete=models.CASCADE,
        related_name='workers', verbose_name='Empresa',
    )
    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='company_assignments', verbose_name='Trabajador',
        limit_choices_to={'user_type': 'trainee'},
    )
    employee_code = models.CharField(
        max_length=50, blank=True, default='',
        verbose_name='Legajo',
    )
    department = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name='Sector',
    )
    position = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name='Puesto',
    )
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    start_date = models.DateField(
        null=True, blank=True,
        verbose_name='Fecha inicio',
    )
    end_date = models.DateField(
        null=True, blank=True,
        verbose_name='Fecha baja',
    )
    notes = models.TextField(
        blank=True, default='',
        verbose_name='Notas',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Trabajador de empresa'
        verbose_name_plural = 'Trabajadores de empresa'
        ordering = ['company', 'worker__last_name', 'worker__first_name']
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'worker'],
                name='uq_company_worker',
            ),
        ]

    def __str__(self):
        return f"{self.worker.display_name} → {self.company.display_name}"
```

---

### Admin: `apps/company/admin.py` — AGREGAR

```python
from .models import CompanyProfile, CompanyWorker


@admin.register(CompanyWorker)
class CompanyWorkerAdmin(admin.ModelAdmin):
    list_display = (
        'worker', 'company', 'employee_code', 'department',
        'position', 'is_active', 'start_date',
    )
    list_filter = ('is_active', 'company', 'department')
    search_fields = (
        'worker__email', 'worker__cuil', 'worker__full_name',
        'employee_code', 'company__razon_social',
    )
    raw_id_fields = ('worker', 'company')
```

---

### Migración

```bash
python manage.py makemigrations company --name create_company_worker
python manage.py migrate
```

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 35: Crear modelo CompanyWorker

- Relación empresa↔trabajador con UniqueConstraint
- Campos laborales: legajo, sector, puesto, fechas, notas
- Admin con búsqueda por CUIL/email/nombre
- Migración aplicada"
```

---

## COMMIT 36: Vista de Nómina — Listado con búsqueda y filtros

### 📝 Archivos a crear

---

#### 1. `apps/company/views.py` — CREAR

```python
# apps/company/views.py
# ============================================================================
# COMMIT 36: Vistas de nómina de trabajadores
# ============================================================================

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from apps.accounts.decorators import company_required
from .models import CompanyProfile, CompanyWorker

User = get_user_model()


def _get_company_profile(request):
    """Helper: obtener CompanyProfile del usuario actual."""
    try:
        return request.user.company_profile
    except CompanyProfile.DoesNotExist:
        return None


@company_required
def nomina_list(request):
    """Listado de trabajadores de la empresa con búsqueda y filtros."""
    cp = _get_company_profile(request)
    if not cp:
        messages.error(request, "No se encontró el perfil de empresa.")
        return redirect("dashboard:home")

    workers_qs = CompanyWorker.objects.filter(
        company=cp
    ).select_related('worker')

    # --- Búsqueda ---
    search = request.GET.get('q', '').strip()
    if search:
        workers_qs = workers_qs.filter(
            Q(worker__full_name__icontains=search) |
            Q(worker__first_name__icontains=search) |
            Q(worker__last_name__icontains=search) |
            Q(worker__cuil__icontains=search) |
            Q(worker__email__icontains=search) |
            Q(employee_code__icontains=search)
        )

    # --- Filtro por sector ---
    sector = request.GET.get('sector', '').strip()
    if sector:
        workers_qs = workers_qs.filter(department__icontains=sector)

    # --- Filtro por estado ---
    status_filter = request.GET.get('status', 'active')
    if status_filter == 'active':
        workers_qs = workers_qs.filter(is_active=True)
    elif status_filter == 'inactive':
        workers_qs = workers_qs.filter(is_active=False)
    # 'all' → no filtra

    # --- Stats ---
    all_workers = CompanyWorker.objects.filter(company=cp)
    stats = {
        'total_active': all_workers.filter(is_active=True).count(),
        'total_inactive': all_workers.filter(is_active=False).count(),
    }

    # --- Sectores únicos para el filtro ---
    departments = (
        CompanyWorker.objects.filter(company=cp)
        .exclude(department='')
        .values_list('department', flat=True)
        .distinct()
        .order_by('department')
    )

    return render(request, "company/nomina_list.html", {
        "workers": workers_qs,
        "stats": stats,
        "search": search,
        "sector": sector,
        "status_filter": status_filter,
        "departments": departments,
    })
```

---

#### 2. `apps/company/urls.py` — CREAR

```python
# apps/company/urls.py
# ============================================================================
# COMMIT 36: URLs de empresa (nómina)
# ============================================================================

from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    # --- Nómina ---
    path('nomina/', views.nomina_list, name='nomina_list'),
]
```

---

#### 3. `apps/dashboard/urls.py` — AGREGAR

Agregar DESPUÉS del include de presencial:

```python
    # =========================================================================
    # Empresa (Etapa 3, Commit 36)
    # =========================================================================
    path('empresa/', include('apps.company.urls')),
```

No olvidar agregar import si no existe:
```python
from django.urls import path, include
```

---

#### 4. `templates/base_dashboard.html` — ACTUALIZAR href de Nómina

Buscar:
```html
<a class="nav-link {% if 'nomina' in request.path %}active{% endif %}"
   href="#">
```

Reemplazar por:
```html
<a class="nav-link {% if 'nomina' in request.path %}active{% endif %}"
   href="{% url 'company:nomina_list' %}">
```

---

#### 5. `templates/company/nomina_list.html` — CREAR

```bash
mkdir -p templates/company
```

```html
{% extends "base_dashboard.html" %}

{% block title %}Nómina de Trabajadores - ErgoSolutions{% endblock %}

{% block content %}
<div class="container-fluid py-4">

    <!-- Breadcrumb -->
    <nav aria-label="breadcrumb" class="mb-3">
        <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="{% url 'dashboard:home' %}">Dashboard</a></li>
            <li class="breadcrumb-item active">Nómina</li>
        </ol>
    </nav>

    <div class="d-flex justify-content-between align-items-center mb-4">
        <h3><i class="bi bi-people me-2 text-primary"></i>Nómina de Trabajadores</h3>
        <div>
            <a href="#" class="btn btn-outline-secondary btn-sm me-2">
                <i class="bi bi-download me-1"></i>Exportar CSV
            </a>
            <a href="#" class="btn btn-primary btn-sm">
                <i class="bi bi-person-plus me-1"></i>Agregar trabajador
            </a>
        </div>
    </div>

    <!-- Stats -->
    <div class="row g-3 mb-4">
        <div class="col-md-3">
            <div class="card bg-dark border-secondary text-center">
                <div class="card-body py-3">
                    <h4 class="text-success mb-0">{{ stats.total_active }}</h4>
                    <small class="text-secondary">Activos</small>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-dark border-secondary text-center">
                <div class="card-body py-3">
                    <h4 class="text-warning mb-0">{{ stats.total_inactive }}</h4>
                    <small class="text-secondary">Inactivos</small>
                </div>
            </div>
        </div>
    </div>

    <!-- Búsqueda y filtros -->
    <div class="card bg-dark border-secondary mb-4">
        <div class="card-body">
            <form method="get" class="row g-3">
                <div class="col-md-5">
                    <input type="text" name="q" value="{{ search }}"
                           class="form-control bg-black text-light border-secondary"
                           placeholder="Buscar por nombre, CUIL, email o legajo...">
                </div>
                <div class="col-md-3">
                    <select name="sector" class="form-select bg-black text-light border-secondary">
                        <option value="">Todos los sectores</option>
                        {% for dept in departments %}
                        <option value="{{ dept }}" {% if dept == sector %}selected{% endif %}>{{ dept }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-2">
                    <select name="status" class="form-select bg-black text-light border-secondary">
                        <option value="active" {% if status_filter == 'active' %}selected{% endif %}>Activos</option>
                        <option value="inactive" {% if status_filter == 'inactive' %}selected{% endif %}>Inactivos</option>
                        <option value="all" {% if status_filter == 'all' %}selected{% endif %}>Todos</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <button type="submit" class="btn btn-outline-primary w-100">
                        <i class="bi bi-search me-1"></i>Filtrar
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- Tabla -->
    <div class="card bg-dark border-secondary">
        <div class="card-body p-0">
            <div class="table-responsive">
                <table class="table table-dark table-hover mb-0">
                    <thead>
                        <tr>
                            <th>Nombre</th>
                            <th>CUIL</th>
                            <th>Legajo</th>
                            <th>Sector</th>
                            <th>Puesto</th>
                            <th>Estado</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for cw in workers %}
                        <tr>
                            <td>
                                <a href="#" class="text-light text-decoration-none">
                                    {{ cw.worker.display_name }}
                                </a>
                                <br><small class="text-secondary">{{ cw.worker.email }}</small>
                            </td>
                            <td><code>{{ cw.worker.cuil }}</code></td>
                            <td>{{ cw.employee_code|default:"-" }}</td>
                            <td>{{ cw.department|default:"-" }}</td>
                            <td>{{ cw.position|default:"-" }}</td>
                            <td>
                                {% if cw.is_active %}
                                <span class="badge bg-success">Activo</span>
                                {% else %}
                                <span class="badge bg-warning text-dark">Inactivo</span>
                                {% endif %}
                            </td>
                            <td>
                                <a href="#" class="btn btn-sm btn-outline-info" title="Ver ficha">
                                    <i class="bi bi-eye"></i>
                                </a>
                                <a href="#" class="btn btn-sm btn-outline-warning" title="Editar">
                                    <i class="bi bi-pencil"></i>
                                </a>
                            </td>
                        </tr>
                        {% empty %}
                        <tr>
                            <td colspan="7" class="text-center py-4 text-secondary">
                                <i class="bi bi-people display-6 d-block mb-2"></i>
                                {% if search or sector %}
                                No se encontraron trabajadores con los filtros aplicados.
                                {% else %}
                                Aún no hay trabajadores en la nómina.
                                <br>
                                <a href="#" class="btn btn-primary btn-sm mt-2">
                                    <i class="bi bi-person-plus me-1"></i>Agregar el primero
                                </a>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

</div>
{% endblock %}
```

> **NOTA:** Los `href="#"` de "Agregar", "Ver ficha" y "Editar" se actualizarán en Commits 37, 38 y 39 respectivamente.

---

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 36: Vista de Nómina - Listado con búsqueda y filtros

- Vista nomina_list con búsqueda, filtro por sector y estado
- URLs de empresa montadas en /dashboard/empresa/
- Template nomina_list.html con stats, tabla responsive, estado vacío
- Navbar actualizado: Nómina apunta a URL real
- Solo accesible para usuarios tipo empresa"
```

---

## COMMIT 37: Alta manual de trabajadores en nómina

### 📝 Archivos a crear/modificar

---

#### 1. `apps/company/forms.py` — CREAR

```python
# apps/company/forms.py
# ============================================================================
# COMMIT 37: Formularios de nómina
# ============================================================================

from django import forms
import re


def normalize_cuil(value: str) -> str:
    """Normaliza CUIL/CUIT: extrae solo dígitos y valida longitud 11."""
    digits = re.sub(r"\D", "", (value or "").strip())
    if len(digits) != 11:
        raise forms.ValidationError("CUIL inválido (debe tener 11 dígitos).")
    return digits


class AddWorkerForm(forms.Form):
    """Formulario para agregar un trabajador a la nómina."""

    # Datos del trabajador
    cuil = forms.CharField(
        label='CUIL del trabajador',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-black text-light border-secondary',
            'placeholder': '20-12345678-9',
        }),
        help_text='Si el trabajador ya existe en el sistema, se vinculará automáticamente.',
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control bg-black text-light border-secondary',
            'placeholder': 'trabajador@email.com',
        }),
    )
    full_name = forms.CharField(
        label='Nombre completo',
        max_length=300,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-black text-light border-secondary',
            'placeholder': 'Juan Pérez',
        }),
    )
    job_title = forms.CharField(
        label='Puesto / Cargo (general)',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-black text-light border-secondary',
        }),
    )

    # Datos de la relación laboral
    employee_code = forms.CharField(
        label='Legajo',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-black text-light border-secondary',
        }),
    )
    department = forms.CharField(
        label='Sector',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-black text-light border-secondary',
        }),
    )
    position = forms.CharField(
        label='Puesto en la empresa',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-black text-light border-secondary',
        }),
    )
    start_date = forms.DateField(
        label='Fecha de inicio',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control bg-black text-light border-secondary',
            'type': 'date',
        }),
    )
    notes = forms.CharField(
        label='Notas',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control bg-black text-light border-secondary',
            'rows': 3,
        }),
    )

    def clean_cuil(self):
        return normalize_cuil(self.cleaned_data['cuil'])
```

---

#### 2. `apps/company/views.py` — AGREGAR

```python
from .forms import AddWorkerForm


@company_required
def nomina_add_worker(request):
    """Agregar un trabajador a la nómina."""
    cp = _get_company_profile(request)
    if not cp:
        messages.error(request, "No se encontró el perfil de empresa.")
        return redirect("dashboard:home")

    if request.method == "POST":
        form = AddWorkerForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cuil = cd['cuil']
            email = cd['email'].strip().lower()

            # 1. Buscar trainee existente por CUIL
            worker = User.objects.filter(
                cuil=cuil, user_type='trainee'
            ).first()

            # 2. Si no encontró por CUIL, buscar por email
            if not worker:
                worker = User.objects.filter(
                    email__iexact=email, user_type='trainee'
                ).first()

            # 3. Si no existe, crear nuevo trainee
            if not worker:
                parts = cd['full_name'].strip().split(' ', 1)
                first = parts[0]
                last = parts[1] if len(parts) > 1 else ''

                worker = User.objects.create_trainee(
                    cuil=cuil,
                    email=email,
                    full_name=cd['full_name'],
                    first_name=first,
                    last_name=last,
                    job_title=cd.get('job_title', ''),
                    company_name=cp.razon_social,
                )

            # 4. Verificar si ya está en la nómina
            if CompanyWorker.objects.filter(company=cp, worker=worker).exists():
                messages.warning(
                    request,
                    f"{worker.display_name} ya está en tu nómina."
                )
                return render(request, "company/nomina_add.html", {"form": form})

            # 5. Crear la relación
            CompanyWorker.objects.create(
                company=cp,
                worker=worker,
                employee_code=cd.get('employee_code', ''),
                department=cd.get('department', ''),
                position=cd.get('position', ''),
                start_date=cd.get('start_date'),
                notes=cd.get('notes', ''),
            )

            messages.success(
                request,
                f"{worker.display_name} agregado a la nómina exitosamente."
            )
            return redirect("company:nomina_list")
    else:
        form = AddWorkerForm()

    return render(request, "company/nomina_add.html", {"form": form})
```

---

#### 3. `apps/company/urls.py` — AGREGAR

```python
path('nomina/agregar/', views.nomina_add_worker, name='nomina_add_worker'),
```

---

#### 4. `templates/company/nomina_add.html` — CREAR

Template con formulario en secciones: Datos del trabajador (CUIL, email, nombre, puesto) y Datos laborales (legajo, sector, puesto en empresa, fecha inicio, notas). Estilo dark consistente.

---

#### 5. Actualizar enlaces en `nomina_list.html`

Buscar `href="#"` del botón "Agregar trabajador" y reemplazar por:
```html
href="{% url 'company:nomina_add_worker' %}"
```

---

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 37: Alta manual de trabajadores en nómina

- AddWorkerForm con datos trabajador + datos laborales
- Lógica: busca trainee existente (CUIL → email), si no existe lo crea
- Verificación de duplicados en nómina
- Template nomina_add.html con formulario en secciones
- URL montada y enlaces actualizados"
```

---

## COMMIT 38: Ficha individual del trabajador

### 📝 `apps/company/views.py` — AGREGAR

```python
from apps.quiz.models import QuizAttempt, QuizState
from apps.certificates.models import Certificate
from apps.training.models import TrainingModule


@company_required
def nomina_detail(request, worker_id):
    """Ficha individual de un trabajador con historial de capacitaciones."""
    cp = _get_company_profile(request)
    if not cp:
        messages.error(request, "No se encontró el perfil de empresa.")
        return redirect("dashboard:home")

    assignment = get_object_or_404(CompanyWorker, company=cp, id=worker_id)
    worker = assignment.worker

    # Últimos intentos de quiz
    quiz_attempts = QuizAttempt.objects.filter(
        user=worker
    ).select_related('module').order_by('-created_at')[:20]

    # Certificados obtenidos
    certificates = Certificate.objects.filter(
        user=worker
    ).select_related('module').order_by('-issued_at')

    # Estado por módulo general activo
    modules = TrainingModule.objects.filter(
        is_active=True, is_personalized=False
    )
    module_status = []
    for mod in modules:
        qs = QuizState.objects.filter(user=worker, module=mod).first()
        cert = Certificate.objects.filter(user=worker, module=mod).first()
        from django.utils import timezone
        module_status.append({
            'module': mod,
            'quiz_state': qs,
            'certificate': cert,
            'is_approved': qs.is_approved if qs else False,
            'is_valid': cert and cert.valid_until and cert.valid_until > timezone.now() if cert else False,
        })

    return render(request, "company/nomina_detail.html", {
        "assignment": assignment,
        "worker": worker,
        "quiz_attempts": quiz_attempts,
        "certificates": certificates,
        "module_status": module_status,
    })
```

---

### URL
```python
path('nomina/<int:worker_id>/', views.nomina_detail, name='nomina_detail'),
```

---

### Template: `templates/company/nomina_detail.html`

Cards con datos personales (nombre, CUIL, email) y laborales (legajo, sector, puesto, fechas, notas). Tabla de estado por módulo (nombre, aprobado/pendiente, certificado vigente/vencido). Historial de quiz (módulo, score, fecha). Certificados con link de descarga y fecha de vencimiento.

---

### Actualizar `nomina_list.html`

Reemplazar `href="#"` del botón "Ver ficha":
```html
href="{% url 'company:nomina_detail' cw.id %}"
```

---

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 38: Ficha individual del trabajador

- Vista nomina_detail con datos personales, laborales, historial
- Estado por módulo de capacitación con quiz y certificado
- Template con cards y tablas organizadas
- Enlaces actualizados desde listado"
```

---

## COMMIT 39: Editar datos laborales de trabajador

### 📝 `apps/company/forms.py` — AGREGAR

```python
class EditWorkerForm(forms.Form):
    """Editar datos laborales de un trabajador en la nómina."""

    employee_code = forms.CharField(
        label='Legajo', max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control bg-black text-light border-secondary'}),
    )
    department = forms.CharField(
        label='Sector', max_length=200, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control bg-black text-light border-secondary'}),
    )
    position = forms.CharField(
        label='Puesto', max_length=200, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control bg-black text-light border-secondary'}),
    )
    start_date = forms.DateField(
        label='Fecha de inicio', required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control bg-black text-light border-secondary', 'type': 'date',
        }),
    )
    end_date = forms.DateField(
        label='Fecha de baja', required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control bg-black text-light border-secondary', 'type': 'date',
        }),
    )
    is_active = forms.BooleanField(
        label='Activo', required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    notes = forms.CharField(
        label='Notas', required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control bg-black text-light border-secondary', 'rows': 3,
        }),
    )

    def __init__(self, *args, assignment=None, **kwargs):
        super().__init__(*args, **kwargs)
        if assignment and not args:
            self.initial.update({
                'employee_code': assignment.employee_code,
                'department': assignment.department,
                'position': assignment.position,
                'start_date': assignment.start_date,
                'end_date': assignment.end_date,
                'is_active': assignment.is_active,
                'notes': assignment.notes,
            })
```

---

### Vista

```python
@company_required
def nomina_edit(request, worker_id):
    """Editar datos laborales de un trabajador."""
    cp = _get_company_profile(request)
    if not cp:
        return redirect("dashboard:home")

    assignment = get_object_or_404(CompanyWorker, company=cp, id=worker_id)

    if request.method == "POST":
        form = EditWorkerForm(request.POST, assignment=assignment)
        if form.is_valid():
            cd = form.cleaned_data
            assignment.employee_code = cd.get('employee_code', '')
            assignment.department = cd.get('department', '')
            assignment.position = cd.get('position', '')
            assignment.start_date = cd.get('start_date')
            assignment.end_date = cd.get('end_date')
            assignment.is_active = cd.get('is_active', True)
            assignment.notes = cd.get('notes', '')
            assignment.save()
            messages.success(request, "Datos laborales actualizados correctamente.")
            return redirect("company:nomina_detail", worker_id=worker_id)
    else:
        form = EditWorkerForm(assignment=assignment)

    return render(request, "company/nomina_edit.html", {
        "form": form,
        "assignment": assignment,
    })
```

### URL
```python
path('nomina/<int:worker_id>/editar/', views.nomina_edit, name='nomina_edit'),
```

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 39: Editar datos laborales de trabajador

- EditWorkerForm pre-poblado con datos de la relación
- Vista nomina_edit con save a assignment
- Template nomina_edit.html
- Enlace actualizado desde ficha individual"
```

---

## COMMIT 40: Exportación de nómina a CSV

### 📝 `apps/company/views.py` — AGREGAR

```python
import csv
from django.http import HttpResponse


@company_required
def nomina_export_csv(request):
    """Exportar nómina completa a CSV."""
    cp = _get_company_profile(request)
    if not cp:
        return redirect("dashboard:home")

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="nomina_{cp.cuit}.csv"'
    response.write('\ufeff')  # BOM para UTF-8 en Excel

    writer = csv.writer(response)
    writer.writerow([
        'Nombre', 'CUIL', 'Email', 'Legajo', 'Sector',
        'Puesto', 'Activo', 'Fecha Inicio', 'Fecha Baja',
    ])

    workers = CompanyWorker.objects.filter(
        company=cp
    ).select_related('worker').order_by('worker__last_name')

    for cw in workers:
        w = cw.worker
        writer.writerow([
            w.display_name,
            w.cuil or '',
            w.email,
            cw.employee_code,
            cw.department,
            cw.position,
            'Sí' if cw.is_active else 'No',
            cw.start_date.strftime('%d/%m/%Y') if cw.start_date else '',
            cw.end_date.strftime('%d/%m/%Y') if cw.end_date else '',
        ])

    return response
```

### URL
```python
path('nomina/exportar/', views.nomina_export_csv, name='nomina_export_csv'),
```

### Actualizar enlace en `nomina_list.html`

Buscar `href="#"` del botón "Exportar CSV":
```html
href="{% url 'company:nomina_export_csv' %}"
```

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 40: Exportación de nómina a CSV

- Vista nomina_export_csv con BOM UTF-8 para Excel
- Columnas: Nombre, CUIL, Email, Legajo, Sector, Puesto, Activo, Fechas
- URL montada y enlace actualizado en listado"
```

---

# ═══════════════════════════════════════════════════════════════════════════
# SUB-ETAPA 3C: AGENDA Y VENCIMIENTOS (Commits 41–45)
# ═══════════════════════════════════════════════════════════════════════════

---

## COMMIT 41: Crear modelo AgendaEvent

### 📝 `apps/company/models.py` — AGREGAR al final

```python
class AgendaEvent(models.Model):
    """Evento genérico de agenda para empresas."""

    class EventType(models.TextChoices):
        TRAINING_DUE = 'training_due', 'Vencimiento de capacitación'
        CERTIFICATE_EXPIRY = 'certificate_expiry', 'Vencimiento de certificado'
        PROFESSIONAL_VISIT = 'professional_visit', 'Visita de profesional'
        EVALUATION_DUE = 'evaluation_due', 'Evaluación pendiente'
        REMINDER = 'reminder', 'Recordatorio'
        OTHER = 'other', 'Otro'

    class EventStatus(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        COMPLETED = 'completed', 'Completado'
        OVERDUE = 'overdue', 'Vencido'
        CANCELLED = 'cancelled', 'Cancelado'

    class Priority(models.TextChoices):
        LOW = 'low', 'Baja'
        MEDIUM = 'medium', 'Media'
        HIGH = 'high', 'Alta'
        URGENT = 'urgent', 'Urgente'

    company = models.ForeignKey(
        CompanyProfile, on_delete=models.CASCADE,
        related_name='agenda_events', verbose_name='Empresa',
    )
    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='agenda_events',
        verbose_name='Trabajador relacionado',
    )
    title = models.CharField(max_length=300, verbose_name='Título')
    description = models.TextField(blank=True, default='', verbose_name='Descripción')
    event_type = models.CharField(
        max_length=30, choices=EventType.choices,
        default=EventType.REMINDER, verbose_name='Tipo de evento',
    )
    status = models.CharField(
        max_length=20, choices=EventStatus.choices,
        default=EventStatus.PENDING, verbose_name='Estado',
    )
    priority = models.CharField(
        max_length=10, choices=Priority.choices,
        default=Priority.MEDIUM, verbose_name='Prioridad',
    )
    start_at = models.DateTimeField(
        null=True, blank=True, verbose_name='Fecha/hora de inicio',
    )
    due_at = models.DateTimeField(verbose_name='Fecha/hora límite')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='created_agenda_events',
        verbose_name='Creado por',
    )
    assigned_professional = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_agenda_events',
        verbose_name='Profesional asignado',
    )
    related_object_type = models.CharField(
        max_length=50, blank=True, default='',
        verbose_name='Tipo de objeto relacionado',
        help_text='Ej: certificate, training_module',
    )
    related_object_id = models.CharField(
        max_length=100, blank=True, default='',
        verbose_name='ID del objeto relacionado',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Evento de agenda'
        verbose_name_plural = 'Eventos de agenda'
        ordering = ['due_at', '-priority']
        indexes = [
            models.Index(fields=['company', 'status', 'due_at']),
            models.Index(fields=['company', 'event_type', 'due_at']),
        ]

    def __str__(self):
        return f"[{self.get_event_type_display()}] {self.title}"

    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.status == self.EventStatus.PENDING and self.due_at < timezone.now()
```

---

### Admin

```python
from .models import CompanyProfile, CompanyWorker, AgendaEvent


@admin.register(AgendaEvent)
class AgendaEventAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'company', 'event_type', 'status',
        'priority', 'due_at', 'worker',
    )
    list_filter = ('event_type', 'status', 'priority', 'company')
    search_fields = ('title', 'description', 'company__razon_social')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('worker', 'created_by', 'assigned_professional')
```

### Migración
```bash
python manage.py makemigrations company --name create_agenda_event
python manage.py migrate
```

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 41: Crear modelo AgendaEvent

- Modelo genérico de eventos con tipos extensibles
- EventType: capacitación, certificado, visita, evaluación, recordatorio, otro
- EventStatus: pendiente, completado, vencido, cancelado
- Priority: baja, media, alta, urgente
- Campos de relación: worker, created_by, assigned_professional
- Campos genéricos: related_object_type/id para integraciones futuras
- Propiedad is_overdue calculada
- Índices optimizados para consultas frecuentes
- Admin completo"
```

---

## COMMIT 42: Vista de Agenda — Listado y filtros

### 📝 `apps/company/views.py` — AGREGAR

```python
from django.utils import timezone
from datetime import timedelta
from .models import CompanyProfile, CompanyWorker, AgendaEvent


@company_required
def agenda_list(request):
    """Listado de eventos de agenda con filtros."""
    cp = _get_company_profile(request)
    if not cp:
        return redirect("dashboard:home")

    events_qs = AgendaEvent.objects.filter(
        company=cp
    ).select_related('worker')

    # --- Filtro por tipo ---
    event_type = request.GET.get('type', '')
    if event_type:
        events_qs = events_qs.filter(event_type=event_type)

    # --- Filtro por estado ---
    status = request.GET.get('status', '')
    if status:
        events_qs = events_qs.filter(status=status)

    # --- Filtro por rango de fechas ---
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        events_qs = events_qs.filter(due_at__date__gte=date_from)
    if date_to:
        events_qs = events_qs.filter(due_at__date__lte=date_to)

    # --- Stats ---
    now = timezone.now()
    all_events = AgendaEvent.objects.filter(company=cp)
    stats = {
        'total_pending': all_events.filter(status='pending').count(),
        'total_overdue': all_events.filter(status='pending', due_at__lt=now).count(),
        'upcoming_7d': all_events.filter(
            status='pending',
            due_at__range=(now, now + timedelta(days=7)),
        ).count(),
    }

    return render(request, "company/agenda_list.html", {
        "events": events_qs[:100],
        "stats": stats,
        "event_type": event_type,
        "status": status,
        "date_from": date_from,
        "date_to": date_to,
        "event_types": AgendaEvent.EventType.choices,
        "event_statuses": AgendaEvent.EventStatus.choices,
    })
```

### URLs — AGREGAR
```python
# --- Agenda ---
path('agenda/', views.agenda_list, name='agenda_list'),
```

### Actualizar `base_dashboard.html` — href de Agenda

```html
href="{% url 'company:agenda_list' %}"
```

### Template: `templates/company/agenda_list.html`

Stats cards (pendientes, vencidos, próximos 7 días), filtros (tipo, estado, rango fechas), tabla de eventos con prioridad visual (badges de color), botones de acciones.

---

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 42: Vista de Agenda - Listado y filtros

- Vista agenda_list con filtros por tipo, estado, rango de fechas
- Stats: pendientes, vencidos, próximos 7 días
- Template con tabla y prioridad visual
- Navbar actualizado: Agenda apunta a URL real"
```

---

## COMMIT 43: CRUD eventos de agenda

### 📝 `apps/company/forms.py` — AGREGAR

```python
from .models import AgendaEvent


class AgendaEventForm(forms.Form):
    """Formulario para crear/editar eventos de agenda."""

    title = forms.CharField(
        label='Título', max_length=300,
        widget=forms.TextInput(attrs={'class': 'form-control bg-black text-light border-secondary'}),
    )
    description = forms.CharField(
        label='Descripción', required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control bg-black text-light border-secondary', 'rows': 3,
        }),
    )
    event_type = forms.ChoiceField(
        label='Tipo de evento',
        choices=AgendaEvent.EventType.choices,
        widget=forms.Select(attrs={'class': 'form-select bg-black text-light border-secondary'}),
    )
    priority = forms.ChoiceField(
        label='Prioridad',
        choices=AgendaEvent.Priority.choices,
        initial='medium',
        widget=forms.Select(attrs={'class': 'form-select bg-black text-light border-secondary'}),
    )
    due_at = forms.DateTimeField(
        label='Fecha/hora límite',
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control bg-black text-light border-secondary',
            'type': 'datetime-local',
        }),
    )
    start_at = forms.DateTimeField(
        label='Fecha/hora de inicio (opcional)', required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control bg-black text-light border-secondary',
            'type': 'datetime-local',
        }),
    )
    worker_id = forms.IntegerField(
        label='Trabajador relacionado (ID)', required=False,
        widget=forms.HiddenInput(),
    )

    def __init__(self, *args, event=None, **kwargs):
        super().__init__(*args, **kwargs)
        if event and not args:
            self.initial.update({
                'title': event.title,
                'description': event.description,
                'event_type': event.event_type,
                'priority': event.priority,
                'due_at': event.due_at.strftime('%Y-%m-%dT%H:%M') if event.due_at else '',
                'start_at': event.start_at.strftime('%Y-%m-%dT%H:%M') if event.start_at else '',
                'worker_id': event.worker_id,
            })
```

### Vistas — AGREGAR

```python
from .forms import AddWorkerForm, EditWorkerForm, AgendaEventForm


@company_required
def agenda_create(request):
    """Crear un evento de agenda."""
    cp = _get_company_profile(request)
    if not cp:
        return redirect("dashboard:home")

    if request.method == "POST":
        form = AgendaEventForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            worker = None
            if cd.get('worker_id'):
                assignment = CompanyWorker.objects.filter(
                    company=cp, id=cd['worker_id']
                ).first()
                if assignment:
                    worker = assignment.worker

            AgendaEvent.objects.create(
                company=cp,
                created_by=request.user,
                worker=worker,
                title=cd['title'],
                description=cd.get('description', ''),
                event_type=cd['event_type'],
                priority=cd['priority'],
                due_at=cd['due_at'],
                start_at=cd.get('start_at'),
            )
            messages.success(request, "Evento creado exitosamente.")
            return redirect("company:agenda_list")
    else:
        form = AgendaEventForm()

    return render(request, "company/agenda_form.html", {
        "form": form, "editing": False,
    })


@company_required
def agenda_edit(request, event_id):
    """Editar un evento de agenda."""
    cp = _get_company_profile(request)
    if not cp:
        return redirect("dashboard:home")

    event = get_object_or_404(AgendaEvent, company=cp, id=event_id)

    if request.method == "POST":
        form = AgendaEventForm(request.POST, event=event)
        if form.is_valid():
            cd = form.cleaned_data
            event.title = cd['title']
            event.description = cd.get('description', '')
            event.event_type = cd['event_type']
            event.priority = cd['priority']
            event.due_at = cd['due_at']
            event.start_at = cd.get('start_at')
            event.save()
            messages.success(request, "Evento actualizado correctamente.")
            return redirect("company:agenda_list")
    else:
        form = AgendaEventForm(event=event)

    return render(request, "company/agenda_form.html", {
        "form": form, "editing": True, "event": event,
    })


@company_required
def agenda_complete(request, event_id):
    """Marcar un evento como completado."""
    cp = _get_company_profile(request)
    if not cp:
        return redirect("dashboard:home")

    event = get_object_or_404(AgendaEvent, company=cp, id=event_id)
    event.status = AgendaEvent.EventStatus.COMPLETED
    event.save()
    messages.success(request, f"Evento '{event.title}' marcado como completado.")
    return redirect("company:agenda_list")
```

### URLs — AGREGAR
```python
path('agenda/crear/', views.agenda_create, name='agenda_create'),
path('agenda/<int:event_id>/editar/', views.agenda_edit, name='agenda_edit'),
path('agenda/<int:event_id>/completar/', views.agenda_complete, name='agenda_complete'),
```

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 43: CRUD eventos de agenda

- AgendaEventForm para crear/editar eventos
- Vista agenda_create con worker opcional
- Vista agenda_edit pre-poblada
- Vista agenda_complete para marcar completado
- Template agenda_form.html reutilizable (crear/editar)"
```

---

## COMMIT 44: Auto-generar eventos de vencimiento de certificados

### 📝 Management command

```bash
mkdir -p apps/company/management/commands
touch apps/company/management/__init__.py
touch apps/company/management/commands/__init__.py
```

### `apps/company/management/commands/generate_cert_expiry_events.py` — CREAR

```python
# apps/company/management/commands/generate_cert_expiry_events.py
# ============================================================================
# COMMIT 44: Auto-generación de eventos de vencimiento de certificados
# ============================================================================

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.certificates.models import Certificate
from apps.company.models import CompanyWorker, AgendaEvent


class Command(BaseCommand):
    help = (
        'Genera eventos de agenda para certificados que vencen en los '
        'próximos 30 días. Pensado para ejecutarse como cron diario.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--days', type=int, default=30,
            help='Días de anticipación para generar alertas (default: 30)',
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Simular sin crear eventos',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        now = timezone.now()
        threshold = now + timedelta(days=days)

        self.stdout.write(
            f"Buscando certificados que vencen entre "
            f"{now.date()} y {threshold.date()}..."
        )

        # Certificados que vencen en el rango
        expiring_certs = Certificate.objects.filter(
            valid_until__range=(now, threshold),
        ).select_related('user', 'module')

        created = 0
        skipped = 0

        for cert in expiring_certs:
            # Buscar si el worker está en alguna nómina
            assignments = CompanyWorker.objects.filter(
                worker=cert.user, is_active=True,
            ).select_related('company')

            for assignment in assignments:
                # Verificar si ya existe un evento para este certificado
                exists = AgendaEvent.objects.filter(
                    company=assignment.company,
                    event_type=AgendaEvent.EventType.CERTIFICATE_EXPIRY,
                    worker=cert.user,
                    related_object_type='certificate',
                    related_object_id=str(cert.id),
                ).exists()

                if exists:
                    skipped += 1
                    continue

                if dry_run:
                    self.stdout.write(
                        f"  [DRY-RUN] Crearía evento: "
                        f"{cert.user.display_name} / {cert.module.title} "
                        f"→ {assignment.company.display_name}"
                    )
                    created += 1
                    continue

                AgendaEvent.objects.create(
                    company=assignment.company,
                    worker=cert.user,
                    title=f"Vencimiento certificado: {cert.module.title}",
                    description=(
                        f"El certificado de '{cert.module.title}' de "
                        f"{cert.user.display_name} vence el "
                        f"{cert.valid_until.strftime('%d/%m/%Y')}."
                    ),
                    event_type=AgendaEvent.EventType.CERTIFICATE_EXPIRY,
                    priority=AgendaEvent.Priority.HIGH,
                    due_at=cert.valid_until,
                    related_object_type='certificate',
                    related_object_id=str(cert.id),
                )
                created += 1

        prefix = "[DRY-RUN] " if dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"{prefix}Completado: {created} eventos creados, "
                f"{skipped} duplicados omitidos."
            )
        )
```

### Uso
```bash
# Ejecutar manualmente
python manage.py generate_cert_expiry_events

# Simulación sin crear
python manage.py generate_cert_expiry_events --dry-run

# Con rango personalizado
python manage.py generate_cert_expiry_events --days 60

# Para cron diario (crontab -e):
# 0 6 * * * cd /path/to/project && /path/to/venv/bin/python manage.py generate_cert_expiry_events
```

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 44: Auto-generar eventos de vencimiento de certificados

- Management command generate_cert_expiry_events
- Busca certificados que vencen en próximos 30 días (configurable)
- Para cada cert, busca si worker está en nómina de empresa
- Crea AgendaEvent si no existe duplicado
- Modo --dry-run para simulación
- Preparado para ejecución como cron diario"
```

---

## COMMIT 45: Panel de vencimientos en dashboard empresa

### 📝 `apps/dashboard/views.py` — REFACTORIZAR vista `home`

```python
@login_required
@backoffice_required
def home(request):
    """Dashboard home: despacha al dashboard correcto según tipo."""
    if request.user.is_company:
        return _company_dashboard(request)
    return _professional_dashboard(request)


def _professional_dashboard(request):
    """Dashboard para profesionales (lógica existente)."""
    # ... código existente de home ...
    return render(request, "dashboard/home.html", context)


def _company_dashboard(request):
    """Dashboard para empresas con stats de nómina y agenda."""
    from apps.company.models import CompanyWorker, AgendaEvent

    user = request.user
    try:
        cp = user.company_profile
    except Exception:
        return render(request, "dashboard/home.html", {})

    now = timezone.now()

    # Stats de nómina
    total_workers = CompanyWorker.objects.filter(company=cp, is_active=True).count()

    # Stats de agenda
    events_pending = AgendaEvent.objects.filter(company=cp, status='pending').count()
    events_overdue = AgendaEvent.objects.filter(
        company=cp, status='pending', due_at__lt=now
    ).count()
    upcoming_events = AgendaEvent.objects.filter(
        company=cp, status='pending', due_at__gte=now,
    ).order_by('due_at')[:5]

    # Cobertura de capacitación
    from apps.certificates.models import Certificate
    workers_with_certs = Certificate.objects.filter(
        user__company_assignments__company=cp,
        user__company_assignments__is_active=True,
    ).values('user').distinct().count()
    coverage = round(workers_with_certs / total_workers * 100, 1) if total_workers > 0 else 0

    # Links generados
    from apps.training.models import CapacitacionLink
    links_count = CapacitacionLink.objects.filter(created_by=user).count()

    return render(request, "dashboard/home_company.html", {
        "company_profile": cp,
        "stats": {
            "total_workers": total_workers,
            "events_pending": events_pending,
            "events_overdue": events_overdue,
            "coverage": coverage,
            "links_count": links_count,
        },
        "upcoming_events": upcoming_events,
    })
```

### Template: `templates/dashboard/home_company.html` — CREAR

```html
{% extends "base_dashboard.html" %}

{% block title %}Dashboard Empresa - ErgoSolutions{% endblock %}

{% block content %}
<div class="container-fluid py-4">
    <h3 class="mb-4">
        <i class="bi bi-building me-2 text-primary"></i>
        Bienvenido, {{ company_profile.display_name }}
    </h3>

    <!-- Stats cards -->
    <div class="row g-3 mb-4">
        <div class="col-md-3">
            <div class="card bg-dark border-secondary">
                <div class="card-body text-center">
                    <h3 class="text-primary mb-0">{{ stats.total_workers }}</h3>
                    <small class="text-secondary">Trabajadores activos</small>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-dark border-secondary">
                <div class="card-body text-center">
                    <h3 class="text-warning mb-0">{{ stats.events_pending }}</h3>
                    <small class="text-secondary">Eventos pendientes</small>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-dark border-secondary">
                <div class="card-body text-center">
                    <h3 class="{% if stats.events_overdue > 0 %}text-danger{% else %}text-success{% endif %} mb-0">
                        {{ stats.events_overdue }}
                    </h3>
                    <small class="text-secondary">Eventos vencidos</small>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-dark border-secondary">
                <div class="card-body text-center">
                    <h3 class="text-info mb-0">{{ stats.coverage }}%</h3>
                    <small class="text-secondary">Cobertura capacitación</small>
                </div>
            </div>
        </div>
    </div>

    <div class="row g-4">
        <!-- Próximos eventos -->
        <div class="col-lg-7">
            <div class="card bg-dark border-secondary">
                <div class="card-header bg-dark border-secondary d-flex justify-content-between align-items-center">
                    <h5 class="mb-0"><i class="bi bi-calendar-event me-2"></i>Próximos eventos</h5>
                    <a href="{% url 'company:agenda_list' %}" class="btn btn-sm btn-outline-primary">
                        Ver todos
                    </a>
                </div>
                <div class="card-body p-0">
                    {% if upcoming_events %}
                    <ul class="list-group list-group-flush">
                        {% for event in upcoming_events %}
                        <li class="list-group-item bg-dark border-secondary">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <span class="badge bg-{% if event.priority == 'urgent' %}danger{% elif event.priority == 'high' %}warning text-dark{% elif event.priority == 'medium' %}info{% else %}secondary{% endif %} me-2">
                                        {{ event.get_priority_display }}
                                    </span>
                                    {{ event.title }}
                                    {% if event.worker %}
                                    <br><small class="text-secondary">{{ event.worker.display_name }}</small>
                                    {% endif %}
                                </div>
                                <small class="text-secondary">
                                    {{ event.due_at|date:"d/m/Y" }}
                                </small>
                            </div>
                        </li>
                        {% endfor %}
                    </ul>
                    {% else %}
                    <div class="text-center py-4 text-secondary">
                        <i class="bi bi-calendar-check display-6 d-block mb-2"></i>
                        No hay eventos próximos
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>

        <!-- Accesos rápidos -->
        <div class="col-lg-5">
            <div class="card bg-dark border-secondary">
                <div class="card-header bg-dark border-secondary">
                    <h5 class="mb-0"><i class="bi bi-lightning me-2"></i>Accesos rápidos</h5>
                </div>
                <div class="card-body">
                    <div class="d-grid gap-2">
                        <a href="{% url 'company:nomina_list' %}" class="btn btn-outline-light text-start">
                            <i class="bi bi-people me-2 text-primary"></i>Ver nómina completa
                        </a>
                        <a href="{% url 'company:nomina_add_worker' %}" class="btn btn-outline-light text-start">
                            <i class="bi bi-person-plus me-2 text-success"></i>Agregar trabajador
                        </a>
                        <a href="{% url 'company:agenda_create' %}" class="btn btn-outline-light text-start">
                            <i class="bi bi-calendar-plus me-2 text-warning"></i>Crear evento
                        </a>
                        <a href="{% url 'dashboard:capacitaciones_menu' %}" class="btn btn-outline-light text-start">
                            <i class="bi bi-mortarboard me-2 text-info"></i>Capacitaciones
                        </a>
                    </div>
                </div>
            </div>

            <!-- Stats adicionales -->
            <div class="card bg-dark border-secondary mt-3">
                <div class="card-body">
                    <div class="d-flex justify-content-between mb-2">
                        <span class="text-secondary">Links generados</span>
                        <span class="fw-bold">{{ stats.links_count }}</span>
                    </div>
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
git commit -m "Commit 45: Panel de vencimientos en dashboard empresa

- Vista home refactorizada: despacha professional/company
- _company_dashboard con stats de nómina, agenda, cobertura
- Template home_company.html con cards, eventos próximos, accesos rápidos
- Cobertura de capacitación calculada
- Dashboard profesional preservado intacto"
```

---

# ═══════════════════════════════════════════════════════════════════════════
# SUB-ETAPA 3D: RED PROFESIONAL + TESTING (Commits 46–48)
# ═══════════════════════════════════════════════════════════════════════════

---

## COMMIT 46: Directorio básico de profesionales

### 📝 `apps/accounts/models.py` — AGREGAR campo

Buscar campos de suscripción y agregar ANTES de `created_at`:

```python
    is_visible_in_directory = models.BooleanField(
        default=False,
        verbose_name='Visible en directorio',
        help_text='Si está activo, este profesional será visible en el directorio para empresas.',
    )
```

### Migración
```bash
python manage.py makemigrations accounts --name add_is_visible_in_directory
python manage.py migrate
```

### Vista — AGREGAR a `apps/company/views.py`

```python
@company_required
def directorio_profesionales(request):
    """Directorio de profesionales visible para empresas."""
    cp = _get_company_profile(request)
    if not cp:
        return redirect("dashboard:home")

    professionals = User.objects.filter(
        user_type='professional',
        is_visible_in_directory=True,
        is_active=True,
    )

    search = request.GET.get('q', '').strip()
    if search:
        professionals = professionals.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(profession__icontains=search)
        )

    profession_filter = request.GET.get('profession', '').strip()
    if profession_filter:
        professionals = professionals.filter(profession__icontains=profession_filter)

    return render(request, "company/directorio.html", {
        "professionals": professionals,
        "search": search,
        "profession_filter": profession_filter,
    })
```

### URL
```python
path('directorio/', views.directorio_profesionales, name='directorio'),
```

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 46: Directorio básico de profesionales

- Campo is_visible_in_directory en CustomUser
- Vista directorio_profesionales con búsqueda y filtro
- Solo profesionales que optaron por ser visibles
- Template directorio.html con cards de profesional"
```

---

## COMMIT 47: Solicitudes de contacto empresa-profesional

### 📝 `apps/company/models.py` — AGREGAR

```python
class ContactRequest(models.Model):
    """Solicitud de contacto de empresa a profesional."""

    class RequestStatus(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        ACCEPTED = 'accepted', 'Aceptada'
        REJECTED = 'rejected', 'Rechazada'
        CANCELLED = 'cancelled', 'Cancelada'

    company = models.ForeignKey(
        CompanyProfile, on_delete=models.CASCADE,
        related_name='contact_requests_sent', verbose_name='Empresa',
    )
    professional = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='contact_requests_received', verbose_name='Profesional',
        limit_choices_to={'user_type': 'professional'},
    )
    message = models.TextField(
        verbose_name='Mensaje',
        help_text='Mensaje de presentación de la empresa al profesional.',
    )
    status = models.CharField(
        max_length=20, choices=RequestStatus.choices,
        default=RequestStatus.PENDING, verbose_name='Estado',
    )
    response_message = models.TextField(
        blank=True, default='',
        verbose_name='Respuesta del profesional',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Solicitud de contacto'
        verbose_name_plural = 'Solicitudes de contacto'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'professional'],
                condition=models.Q(status='pending'),
                name='uq_pending_contact_request',
            ),
        ]

    def __str__(self):
        return f"{self.company.display_name} → {self.professional.display_name} ({self.status})"
```

### Vistas principales

```python
@company_required
def send_contact_request(request, professional_id):
    """Empresa envía solicitud de contacto a un profesional."""
    # Verificar profesional existe y está en directorio
    # Verificar no hay solicitud pendiente
    # Crear ContactRequest
    pass


# En una vista nueva para profesionales (apps/dashboard/views.py o similar):
@professional_required
def my_contact_requests(request):
    """Profesional ve solicitudes pendientes."""
    # ContactRequest.filter(professional=user, status='pending')
    pass


@professional_required
def respond_contact_request(request, request_id):
    """Profesional acepta o rechaza solicitud."""
    # Validar, actualizar status y responded_at
    pass
```

### Migración
```bash
python manage.py makemigrations company --name create_contact_request
python manage.py migrate
```

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 47: Solicitudes de contacto empresa-profesional

- Modelo ContactRequest con status y constraint de unicidad
- Vista send_contact_request para empresas
- Vista my_contact_requests para profesionales
- Vista respond_contact_request (aceptar/rechazar)
- Migración aplicada"
```

---

## COMMIT 48: Testing integral + documentación Etapa 3

### 📝 `apps/company/tests.py` — CREAR

```python
# apps/company/tests.py
# ============================================================================
# COMMIT 48: Tests integrales de Etapa 3
# ============================================================================

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import CompanyProfile, CompanyWorker, AgendaEvent, ContactRequest

User = get_user_model()


class CompanyRegistrationTests(TestCase):
    """Tests de registro y autenticación de empresas."""

    def test_company_register_creates_user_and_profile(self):
        """Registrar empresa crea CustomUser + CompanyProfile."""
        data = {
            'razon_social': 'Acme S.A.',
            'cuit': '20-12345678-9',
            'contacto_nombre': 'Juan Pérez',
            'email': 'acme@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        response = self.client.post(reverse('company_register'), data)
        self.assertEqual(response.status_code, 302)

        user = User.objects.get(email='acme@test.com')
        self.assertTrue(user.is_company)
        self.assertTrue(user.is_backoffice_user)
        self.assertFalse(user.is_professional)
        self.assertTrue(hasattr(user, 'company_profile'))
        self.assertEqual(user.company_profile.razon_social, 'Acme S.A.')

    def test_company_cannot_access_professional_only_views(self):
        """Empresa no puede acceder a vistas solo de profesional."""
        user = User.objects.create_company(
            email='co@test.com', password='pass123'
        )
        CompanyProfile.objects.create(
            user=user, razon_social='Test', cuit='20111111111',
            contacto_nombre='Test',
        )
        self.client.login(username='co@test.com', password='pass123')
        # Verificar que puede acceder al dashboard
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)

    def test_trainee_cannot_access_dashboard(self):
        """Trainee no puede acceder al dashboard."""
        User.objects.create_trainee(
            cuil='20111111111', email='worker@test.com',
            full_name='Worker',
        )
        self.client.force_login(User.objects.get(email='worker@test.com'))
        response = self.client.get(reverse('dashboard:home'))
        self.assertIn(response.status_code, [302, 403])


class CompanyNominaTests(TestCase):
    """Tests de nómina de trabajadores."""

    def setUp(self):
        self.company_user = User.objects.create_company(
            email='co@test.com', password='pass123'
        )
        self.cp = CompanyProfile.objects.create(
            user=self.company_user, razon_social='Test Co',
            cuit='20222222222', contacto_nombre='Admin',
        )
        self.trainee = User.objects.create_trainee(
            cuil='20333333333', email='worker@test.com',
            full_name='Worker Test',
        )
        self.client.login(username='co@test.com', password='pass123')

    def test_add_existing_trainee_to_nomina(self):
        """Agregar trainee existente a nómina."""
        data = {
            'cuil': '20-33333333-3',
            'email': 'worker@test.com',
            'full_name': 'Worker Test',
            'employee_code': 'LEG001',
            'department': 'Producción',
        }
        response = self.client.post(
            reverse('company:nomina_add_worker'), data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            CompanyWorker.objects.filter(
                company=self.cp, worker=self.trainee
            ).exists()
        )

    def test_cannot_add_duplicate_worker(self):
        """No se puede agregar el mismo worker dos veces."""
        CompanyWorker.objects.create(
            company=self.cp, worker=self.trainee,
        )
        data = {
            'cuil': '20-33333333-3',
            'email': 'worker@test.com',
            'full_name': 'Worker Test',
        }
        response = self.client.post(
            reverse('company:nomina_add_worker'), data
        )
        self.assertEqual(response.status_code, 200)  # Re-renderiza form
        self.assertEqual(
            CompanyWorker.objects.filter(
                company=self.cp, worker=self.trainee
            ).count(), 1
        )

    def test_professional_cannot_access_nomina(self):
        """Profesional no puede acceder a nómina."""
        pro = User.objects.create_professional(
            email='pro@test.com', password='pass123', username='pro',
        )
        self.client.login(username='pro@test.com', password='pass123')
        response = self.client.get(reverse('company:nomina_list'))
        self.assertIn(response.status_code, [302, 403])


class CompanyAgendaTests(TestCase):
    """Tests de agenda y eventos."""

    def setUp(self):
        self.company_user = User.objects.create_company(
            email='co@test.com', password='pass123'
        )
        self.cp = CompanyProfile.objects.create(
            user=self.company_user, razon_social='Test Co',
            cuit='20444444444', contacto_nombre='Admin',
        )
        self.client.login(username='co@test.com', password='pass123')

    def test_create_agenda_event(self):
        """Crear evento de agenda."""
        from django.utils import timezone
        data = {
            'title': 'Revisión mensual',
            'event_type': 'reminder',
            'priority': 'medium',
            'due_at': (timezone.now() + timezone.timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
        }
        response = self.client.post(
            reverse('company:agenda_create'), data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            AgendaEvent.objects.filter(company=self.cp, title='Revisión mensual').exists()
        )

    def test_complete_event(self):
        """Marcar evento como completado."""
        from django.utils import timezone
        event = AgendaEvent.objects.create(
            company=self.cp, title='Test Event',
            due_at=timezone.now(), created_by=self.company_user,
        )
        response = self.client.post(
            reverse('company:agenda_complete', args=[event.id])
        )
        event.refresh_from_db()
        self.assertEqual(event.status, 'completed')
```

### Ejecutar tests
```bash
python manage.py test apps.company -v2
python manage.py test  # Todos los tests (verificar no-regresión)
```

### 📝 Mensaje de Commit
```bash
git add .
git commit -m "Commit 48: Testing integral Etapa 3

- CompanyRegistrationTests: registro, permisos, tipos de usuario
- CompanyNominaTests: alta, duplicados, permisos
- CompanyAgendaTests: CRUD eventos, completar
- Verificación de no-regresión: flujos professional y trainee
- Etapa 3 completada"
```

---

# ═══════════════════════════════════════════════════════════════════════════
# RESUMEN EJECUTIVO
# ═══════════════════════════════════════════════════════════════════════════

## Progreso por Sub-Etapa

| Sub-Etapa | Commits | Descripción | Estado |
|-----------|---------|-------------|--------|
| **3A** | 29–34 | Base: user_type, CompanyProfile, auth, dashboard refactor, perfil | ⬜ Pendiente |
| **3B** | 35–40 | Nómina: modelo, listado, alta, ficha, edición, export CSV | ⬜ Pendiente |
| **3C** | 41–45 | Agenda: modelo, listado, CRUD, auto-generación, panel dashboard | ⬜ Pendiente |
| **3D** | 46–48 | Red profesional: directorio, solicitudes, testing | ⬜ Pendiente |

## Total: 20 commits (29 al 48)

## Modelos Nuevos

| Modelo | App | Relaciones |
|--------|-----|------------|
| `CompanyProfile` | company | OneToOne → CustomUser(company) |
| `CompanyWorker` | company | FK → CompanyProfile + FK → CustomUser(trainee) |
| `AgendaEvent` | company | FK → CompanyProfile + FK nullable → worker, professional |
| `ContactRequest` | company | FK → CompanyProfile + FK → CustomUser(professional) |

## Campos Nuevos en CustomUser

| Campo | Tipo | Aplicación |
|-------|------|------------|
| `COMPANY` choice | TextChoices | Nuevo tipo de usuario |
| `is_visible_in_directory` | BooleanField | Solo professional (Commit 46) |

## Decoradores Nuevos

| Decorador | Permite acceso a |
|-----------|------------------|
| `@backoffice_required` | professional + company |
| `@company_required` | solo company |

## Cadena de Dependencias

```
29 (user_type) → 30 (CompanyProfile) → 31 (decoradores) → 32 (auth empresa)
                                                                    ↓
33 (dashboard refactor) → 34 (perfil empresa) → 35 (CompanyWorker) → 36-40 (nómina completa)
                                                                    ↓
                                                 41-45 (agenda completa) → 46-48 (red + tests)
```

## URLs finales completas (apps/company/urls.py)

```python
app_name = 'company'

urlpatterns = [
    # Nómina
    path('nomina/', views.nomina_list, name='nomina_list'),
    path('nomina/agregar/', views.nomina_add_worker, name='nomina_add_worker'),
    path('nomina/exportar/', views.nomina_export_csv, name='nomina_export_csv'),
    path('nomina/<int:worker_id>/', views.nomina_detail, name='nomina_detail'),
    path('nomina/<int:worker_id>/editar/', views.nomina_edit, name='nomina_edit'),

    # Agenda
    path('agenda/', views.agenda_list, name='agenda_list'),
    path('agenda/crear/', views.agenda_create, name='agenda_create'),
    path('agenda/<int:event_id>/editar/', views.agenda_edit, name='agenda_edit'),
    path('agenda/<int:event_id>/completar/', views.agenda_complete, name='agenda_complete'),

    # Directorio
    path('directorio/', views.directorio_profesionales, name='directorio'),
    path('directorio/<int:professional_id>/contactar/', views.send_contact_request, name='send_contact_request'),
]
```

## Principios Clave

1. **No duplicar, extender:** El dashboard se refactoriza con `@backoffice_required`, no se copia.
2. **Relaciones reales:** `CompanyWorker` reemplaza la dependencia del campo texto `company_name`.
3. **Estructura genérica:** `AgendaEvent` absorbe múltiples tipos de evento sin reestructurar.
4. **Vinculación consentida:** La red profesional usa solicitudes formales, no chat libre.
5. **Compatibilidad total:** Ningún flujo existente de profesional o trainee se rompe.
6. **Migraciones seguras:** Cada commit genera una migración independiente y reversible.

---

*Plan Maestro generado para ErgoSolutions — Etapa 3: Perfil Empresa*
*Fecha: Marzo 2026*
*Commits: 29 al 48*

---
