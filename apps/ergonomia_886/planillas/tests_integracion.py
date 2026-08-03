"""Cobertura consolidada de la normalización de dominio de la Fase 3."""

import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.company.models import CompanyProfile
from apps.ergonomia_886.exportaciones.reports.llm import sanitize_payload

from .forms import EvaluacionForm
from .models import Evaluacion
from .querysets import evaluaciones_visibles_para, puede_editar_evaluaciones


class PropiedadMixtaTests(TestCase):
    """D-9: una evaluación pertenece a un profesional y, opcionalmente, empresa."""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.prof_a = User.objects.create_professional(
            email="prof-a@test.local", password="clave-de-prueba",
            username="prof-a",
        )
        cls.prof_b = User.objects.create_professional(
            email="prof-b@test.local", password="clave-de-prueba",
            username="prof-b",
        )
        cls.user_empresa = User.objects.create_company(
            email="empresa@test.local", password="clave-de-prueba",
            username="empresa",
        )
        cls.trainee = User.objects.create_trainee(
            cuil="20-11111111-1", email="trab@test.local",
        )
        cls.perfil = CompanyProfile.objects.create(
            user=cls.user_empresa, razon_social="ACME S.A.",
            cuit="30-12345678-9", contacto_nombre="Contacto",
            domicilio="Av. Siempreviva 742", provincia="Buenos Aires",
        )
        cls.eval_a = Evaluacion.objects.create(
            usuario=cls.prof_a, empresa=cls.perfil, razon_social="ACME S.A.",
            cuit="30-12345678-9",
            direccion_establecimiento="Av. Siempreviva 742",
            provincia="Buenos Aires",
        )
        cls.eval_b = Evaluacion.objects.create(
            usuario=cls.prof_b, razon_social="OTRA S.R.L.",
            cuit="30-99999999-9", direccion_establecimiento="Otra 100",
            provincia="Córdoba",
        )

    def test_un_profesional_solo_ve_las_suyas(self):
        visibles = evaluaciones_visibles_para(self.prof_a)
        self.assertIn(self.eval_a, visibles)
        self.assertNotIn(self.eval_b, visibles)

    def test_una_empresa_ve_las_de_su_empresa(self):
        visibles = evaluaciones_visibles_para(self.user_empresa)
        self.assertIn(self.eval_a, visibles)
        self.assertNotIn(self.eval_b, visibles)

    def test_un_trainee_no_ve_ninguna(self):
        self.assertEqual(evaluaciones_visibles_para(self.trainee).count(), 0)

    def test_una_evaluacion_ajena_responde_404_y_no_403(self):
        self.client.force_login(self.prof_a)
        url = reverse("planillas:detalle_evaluacion", args=[self.eval_b.pk])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_una_empresa_no_puede_crear_evaluaciones(self):
        self.assertFalse(puede_editar_evaluaciones(self.user_empresa))
        self.assertTrue(puede_editar_evaluaciones(self.prof_a))

    def test_ninguna_ruta_clave_devuelve_500_a_un_anonimo(self):
        for url in (
            reverse("ergonomia_886:evaluacion_list"),
            reverse("planillas:detalle_evaluacion", args=[self.eval_a.pk]),
            reverse("exportaciones:panel", args=[self.eval_a.pk]),
        ):
            with self.subTest(url=url):
                self.assertIn(self.client.get(url).status_code, (302, 403, 404))

    def test_cf5_el_poblado_conserva_lo_declarado(self):
        form = EvaluacionForm(
            data={
                "empresa": self.perfil.pk,
                "razon_social": "",
                "cuit": "",
                "ciiu": "",
                "direccion_establecimiento": "Depósito confirmado por el profesional",
                "provincia": "",
            },
            user=self.prof_a,
        )
        self.assertTrue(form.is_valid(), form.errors)
        evaluacion = form.save()
        self.assertEqual(evaluacion.razon_social, self.perfil.razon_social)
        self.assertEqual(
            evaluacion.direccion_establecimiento,
            "Depósito confirmado por el profesional",
        )

    def test_cf4_sanea_claves_y_valores_personales(self):
        limpio = sanitize_payload({
            "factor": "lmc",
            "trabajadores": [{
                "cuil": "20-11111111-1",
                "email": "persona@example.com",
                "first_name": "Persona Identificable",
            }],
            "inputs": {"peso_kg": 25},
        })
        serializado = json.dumps(limpio)
        for valor in (
            "trabajadores", "20-11111111-1", "persona@example.com",
            "Persona Identificable",
        ):
            self.assertNotIn(valor, serializado)
        self.assertEqual(limpio["inputs"]["peso_kg"], 25)

    def test_indices_de_consulta_declarados(self):
        self.assertEqual(
            {index.name for index in Evaluacion._meta.indexes},
            {"idx_eval_usuario_fmod", "idx_eval_empresa_fmod", "idx_eval_cuit"},
        )
