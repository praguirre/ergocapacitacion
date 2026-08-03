"""Pruebas de la propiedad mixta de evaluaciones (decisión D-9)."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from apps.company.models import CompanyProfile

from .models import Evaluacion
from .querysets import evaluaciones_visibles_para, puede_editar_evaluaciones


class EvaluacionesVisiblesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.profesional = User.objects.create_user(
            email="profesional-d9@example.com",
            username="profesional-d9",
            password="test-password",
            user_type="professional",
        )
        cls.otro_profesional = User.objects.create_user(
            email="otro-profesional-d9@example.com",
            username="otro-profesional-d9",
            password="test-password",
            user_type="professional",
        )
        cls.usuario_empresa = User.objects.create_user(
            email="empresa-d9@example.com",
            username="empresa-d9",
            password="test-password",
            user_type="company",
        )
        cls.empresa = CompanyProfile.objects.create(
            user=cls.usuario_empresa,
            razon_social="Empresa D9 S.A.",
            cuit="30-99999991-9",
            contacto_nombre="Contacto D9",
        )
        cls.empresa_sin_perfil = User.objects.create_user(
            email="empresa-sin-perfil-d9@example.com",
            username="empresa-sin-perfil-d9",
            password="test-password",
            user_type="company",
        )
        cls.trainee = User.objects.create_user(
            email="trainee-d9@example.com",
            user_type="trainee",
        )
        cls.evaluacion_propia = cls._crear_evaluacion(cls.profesional, "30-1-9")
        cls.evaluacion_ajena = cls._crear_evaluacion(
            cls.otro_profesional, "30-2-8"
        )

    @classmethod
    def _crear_evaluacion(cls, usuario, cuit):
        return Evaluacion.objects.create(
            usuario=usuario,
            empresa=cls.empresa,
            razon_social=cls.empresa.razon_social,
            cuit=cuit,
            direccion_establecimiento="Domicilio de prueba",
            provincia="Buenos Aires",
        )

    def test_profesional_solo_ve_las_que_creo_aunque_compartan_empresa(self):
        self.assertQuerySetEqual(
            evaluaciones_visibles_para(self.profesional),
            [self.evaluacion_propia],
            ordered=False,
        )

    def test_empresa_ve_todas_las_de_su_empresa(self):
        self.assertQuerySetEqual(
            evaluaciones_visibles_para(self.usuario_empresa),
            [self.evaluacion_propia, self.evaluacion_ajena],
            ordered=False,
        )

    def test_empresa_sin_perfil_no_ve_evaluaciones(self):
        self.assertFalse(
            evaluaciones_visibles_para(self.empresa_sin_perfil).exists()
        )

    def test_trainee_y_anonimo_no_ven_evaluaciones(self):
        self.assertFalse(evaluaciones_visibles_para(self.trainee).exists())
        self.assertFalse(evaluaciones_visibles_para(AnonymousUser()).exists())

    def test_solo_el_profesional_activo_puede_editar(self):
        self.assertTrue(puede_editar_evaluaciones(self.profesional))
        self.assertFalse(puede_editar_evaluaciones(self.usuario_empresa))
        self.assertFalse(puede_editar_evaluaciones(self.trainee))
        self.profesional.is_active = False
        self.assertFalse(puede_editar_evaluaciones(self.profesional))
