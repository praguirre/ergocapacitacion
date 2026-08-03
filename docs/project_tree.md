.
├── AGENTS.md
├── README.md
├── apps
│   ├── __init__.py
│   ├── accounts
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── backends.py
│   │   ├── decorators.py
│   │   ├── forms.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_add_company_user_type.py
│   │   │   ├── 0003_add_is_visible_in_directory.py
│   │   │   └── __init__.py
│   │   ├── mixins.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── urls_company.py
│   │   ├── urls_professional.py
│   │   ├── views.py
│   │   ├── views_company.py
│   │   └── views_professional.py
│   ├── certificates
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── emailer.py
│   │   ├── management
│   │   │   ├── __init__.py
│   │   │   └── commands
│   │   │       ├── __init__.py
│   │   │       └── send_test_email.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── pdf.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── company
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── context_processors.py
│   │   ├── forms.py
│   │   ├── management
│   │   │   ├── __init__.py
│   │   │   └── commands
│   │   │       ├── __init__.py
│   │   │       └── generate_cert_expiry_events.py
│   │   ├── migrations
│   │   │   ├── 0001_create_company_profile.py
│   │   │   ├── 0002_create_company_worker.py
│   │   │   ├── 0003_create_agenda_event.py
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── dashboard
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── migrations
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── utils.py
│   │   └── views.py
│   ├── ergobot_ai
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── agents.py
│   │   ├── apps.py
│   │   ├── migrations
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── prompts
│   │   │   ├── modules
│   │   │   └── system_base.md
│   │   ├── prompts.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── landing
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── presencial
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations
│   │   │   ├── 0001_create_presencial_session.py
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── pdf.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── quiz
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── fixtures
│   │   │   └── backup_quiz_questions.json
│   │   ├── management
│   │   │   ├── __init__.py
│   │   │   └── commands
│   │   │       ├── __init__.py
│   │   │       ├── import_quiz_backup.py
│   │   │       └── seed_quiz.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   └── training
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── content
│       │   └── ergonomia
│       │       ├── intro.md
│       │       ├── material.md
│       │       └── transcript.txt
│       ├── fixtures
│       │   └── training_modules.json
│       ├── management
│       │   ├── __init__.py
│       │   └── commands
│       │       ├── __init__.py
│       │       ├── seed_module_content.py
│       │       └── seed_modules.py
│       ├── migrations
│       │   ├── 0001_initial.py
│       │   ├── 0002_add_icon_color_order_description.py
│       │   ├── 0003_add_capacitacion_link.py
│       │   ├── 0004_add_link_share_log.py
│       │   ├── 0005_add_personalized_training_fields.py
│       │   └── __init__.py
│       ├── models.py
│       ├── tests.py
│       ├── urls.py
│       ├── urls_public.py
│       ├── views.py
│       └── views_public.py
├── backup_contenido.json
├── config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── docs
│   ├── DEPLOY_CLAUDE_RUNBOOK.md
│   ├── ERGOSOLUTIONS_ARQUITECTURA_ROADMAP.md
│   ├── INFORME_TECNICO_AUDITORIA_PRODUCCION_2026-07-30.md
│   ├── MAPA_CONCEPTUAL_VISUAL.md
│   ├── PLAN_CAPACITACIONES_PERSONALIZADAS.md
│   ├── PLAN_EMAIL_PRODUCCION.md
│   ├── PLAN_MAESTRO_COMMITS_FASES_3_4_5_6.md
│   ├── PLAN_MAESTRO_COMMITS_GENERAL_FASES_1_2.md
│   ├── PLAN_MAESTRO_ETAPA_3_PERFIL_EMPRESA.md
│   ├── README.md
│   └── project_tree.md
├── manage.py
├── media
│   └── certificates
│       ├── certificado_5585f74e-32da-4c6b-8a62-fbe96d597860.pdf
│       ├── certificado_751eab1d-696c-45d0-a43c-294c33b77969.pdf
│       ├── certificado_88ca612b-1599-42e2-9e92-7793dadf5660.pdf
│       ├── certificado_95197435-fb2f-43a5-ae26-b2697df77e86.pdf
│       ├── certificado_ee64cb37-ea3a-46b6-b49f-fb032daf33c6.pdf
│       └── certificado_f533bcb0-b772-4040-9b7b-bf71d2f38e8c.pdf
├── requirements.txt
├── static
│   ├── css
│   │   ├── app.css
│   │   └── dashboard.css
│   └── js
│       ├── ergobot_chat.js
│       └── quiz.js
├── templates
│   ├── accounts
│   │   ├── company
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── confirm.html
│   │   ├── professional
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   └── trainee_landing.html
│   ├── base.html
│   ├── base_dashboard.html
│   ├── base_landing.html
│   ├── company
│   │   ├── agenda_form.html
│   │   ├── agenda_list.html
│   │   ├── directorio.html
│   │   ├── nomina_add.html
│   │   ├── nomina_detail.html
│   │   ├── nomina_edit.html
│   │   └── nomina_list.html
│   ├── dashboard
│   │   ├── capacitaciones_menu.html
│   │   ├── company_profile.html
│   │   ├── home.html
│   │   ├── home_company.html
│   │   ├── modalidad_selector.html
│   │   ├── online_links.html
│   │   ├── profile.html
│   │   └── share_link.html
│   ├── includes
│   │   └── messages.html
│   ├── landing
│   │   └── home.html
│   ├── presencial
│   │   ├── capacitacion.html
│   │   ├── historial.html
│   │   └── quiz.html
│   ├── quiz
│   │   ├── quiz_widget.html
│   │   └── result.html
│   └── training
│       └── training_page.html
└── training_modules.json

51 directories, 188 files
