"""Enlace autorizado desde la agenda de empresa hacia Planilla 4."""

from datetime import date
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.company.models import AgendaEvent, CompanyProfile

from .agenda import sincronizar_medida_con_agenda
from .models import Evaluacion, MedidaEspecifica, Planilla3, SeguimientoMedida
from .templatetags.ergonomia_886_agenda import medida_protocolo_url


class EnlaceAgendaPlanilla4Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.profesional = User.objects.create_professional(
            email="link-agenda-prof@test.local",
            username="link-agenda-prof",
            password="prueba",
        )
        cls.usuario_empresa = User.objects.create_company(
            email="link-agenda-empresa@test.local",
            username="link-agenda-empresa",
            password="prueba",
        )
        cls.empresa = CompanyProfile.objects.create(
            user=cls.usuario_empresa,
            razon_social="ACME",
            cuit="30-12345678-9",
            contacto_nombre="Contacto",
        )
        otro_usuario = User.objects.create_company(
            email="link-agenda-otra@test.local",
            username="link-agenda-otra",
            password="prueba",
        )
        cls.otra_empresa = CompanyProfile.objects.create(
            user=otro_usuario,
            razon_social="Otra",
            cuit="30-99999999-9",
            contacto_nombre="Otro",
        )
        cls.evaluacion = Evaluacion.objects.create(
            usuario=cls.profesional,
            empresa=cls.empresa,
            razon_social="ACME",
            cuit="30-12345678-9",
            direccion_establecimiento="Ruta 8",
            provincia="Buenos Aires",
        )
        planilla3 = Planilla3.objects.create(evaluacion=cls.evaluacion)
        medida = MedidaEspecifica.objects.create(
            planilla3=planilla3,
            descripcion="Instalar ayuda mecánica",
        )
        cls.seguimiento = SeguimientoMedida.objects.create(
            medida_especifica=medida,
            fecha_impl_ing=date(2026, 8, 20),
            nivel_riesgo=3,
        )
        cls.evento = sincronizar_medida_con_agenda(cls.seguimiento)

    def test_la_agenda_muestra_el_enlace_hacia_la_planilla4(self):
        self.client.force_login(self.usuario_empresa)
        respuesta = self.client.get(reverse("dashboard:company:agenda_list"))
        destino = reverse("planillas:planilla4", args=[self.evaluacion.pk])
        self.assertContains(respuesta, "Ver medida en el protocolo")
        self.assertContains(respuesta, f'href="{destino}"')

    def test_el_tag_no_revela_una_evaluacion_a_otra_empresa(self):
        self.assertEqual(
            medida_protocolo_url(self.evento, self.otra_empresa.user),
            "",
        )

    def test_apps_company_no_importa_el_modulo_886(self):
        company_dir = Path(settings.BASE_DIR) / "apps" / "company"
        fuentes = "\n".join(
            path.read_text(encoding="utf-8")
            for path in company_dir.rglob("*.py")
            if "migrations" not in path.parts and not path.name.startswith("test")
        )
        self.assertNotIn("apps.ergonomia_886", fuentes)
