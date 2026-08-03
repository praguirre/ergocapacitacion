"""Pruebas del alta de evaluaciones y sus snapshots documentales."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.company.models import CompanyProfile

from .forms import EvaluacionForm
from .models import Evaluacion


class EvaluacionFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.profesional = User.objects.create_user(
            email="profesional-cf5@example.com",
            username="profesional-cf5",
            password="test-password",
            user_type="professional",
        )
        cls.user_empresa = User.objects.create_user(
            email="empresa-cf5@example.com",
            username="empresa-cf5",
            password="test-password",
            user_type="company",
        )
        cls.perfil = CompanyProfile.objects.create(
            user=cls.user_empresa,
            razon_social="ACME S.A.",
            cuit="30-12345678-9",
            contacto_nombre="Ana Gómez",
            domicilio="Av. Siempreviva 742",
            provincia="Buenos Aires",
        )
        otro_user = User.objects.create_user(
            email="otra-empresa-cf5@example.com",
            username="otra-empresa-cf5",
            password="test-password",
            user_type="company",
        )
        cls.otro_perfil = CompanyProfile.objects.create(
            user=otro_user,
            razon_social="Otra Empresa S.A.",
            cuit="30-87654321-9",
            contacto_nombre="Otro contacto",
        )

    def test_cf5_el_poblado_no_sobrescribe_lo_que_el_profesional_tipeo(self):
        form = EvaluacionForm(
            data={
                "empresa": self.perfil.pk,
                "razon_social": "",
                "cuit": "",
                "direccion_establecimiento": "Depósito Norte, Ruta 8 km 42",
                "provincia": "",
                "ciiu": "",
            },
            user=self.profesional,
        )
        self.assertTrue(form.is_valid(), form.errors)
        evaluacion = form.save()

        self.assertEqual(evaluacion.razon_social, self.perfil.razon_social)
        self.assertEqual(evaluacion.cuit, self.perfil.cuit)
        self.assertEqual(evaluacion.provincia, self.perfil.provincia)
        self.assertEqual(
            evaluacion.direccion_establecimiento,
            "Depósito Norte, Ruta 8 km 42",
        )

    def test_el_poblado_no_resincroniza_al_editar(self):
        evaluacion = Evaluacion.objects.create(
            usuario=self.profesional,
            empresa=self.perfil,
            razon_social="ACME S.A.",
            cuit="30-12345678-9",
            direccion_establecimiento="Av. Siempreviva 742",
            provincia="Buenos Aires",
        )
        self.perfil.domicilio = "Nueva sede — Av. Corrientes 1000"
        self.perfil.save()

        evaluacion.refresh_from_db()
        self.assertEqual(
            evaluacion.direccion_establecimiento,
            "Av. Siempreviva 742",
            "El documento emitido cambio retroactivamente de domicilio",
        )

    def test_company_solo_puede_seleccionar_su_propia_empresa(self):
        form = EvaluacionForm(user=self.user_empresa)
        self.assertQuerySetEqual(
            form.fields["empresa"].queryset,
            [self.perfil],
            ordered=False,
        )
        self.assertTrue(form.fields["empresa"].disabled)
        self.assertNotIn(self.otro_perfil, form.fields["empresa"].queryset)
