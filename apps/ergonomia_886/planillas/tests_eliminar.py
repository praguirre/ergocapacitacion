"""Pruebas de eliminación segura de evaluaciones."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.company.models import CompanyProfile

from .models import Evaluacion


class EliminarEvaluacionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.autor = User.objects.create_user(
            email="autor-delete@example.com", username="autor-delete",
            password="test-password", user_type="professional",
        )
        cls.otro_profesional = User.objects.create_user(
            email="otro-delete@example.com", username="otro-delete",
            password="test-password", user_type="professional",
        )
        cls.usuario_empresa = User.objects.create_user(
            email="empresa-delete@example.com", username="empresa-delete",
            password="test-password", user_type="company",
        )
        cls.empresa = CompanyProfile.objects.create(
            user=cls.usuario_empresa, razon_social="Empresa Delete S.A.",
            cuit="30-44444444-4", contacto_nombre="Contacto Delete",
        )
        cls.evaluacion = Evaluacion.objects.create(
            usuario=cls.autor, empresa=cls.empresa,
            razon_social="Empresa Delete S.A.", cuit="30-44444444-4",
            direccion_establecimiento="Domicilio Delete",
            provincia="Buenos Aires",
        )

    def _url(self):
        return reverse(
            "ergonomia_886:eliminar_evaluacion", args=[self.evaluacion.pk]
        )

    def test_una_empresa_no_puede_eliminar_un_protocolo(self):
        self.client.force_login(self.usuario_empresa)
        self.assertEqual(self.client.post(self._url()).status_code, 404)
        self.assertTrue(
            Evaluacion.objects.filter(pk=self.evaluacion.pk).exists()
        )

    def test_un_profesional_no_puede_eliminar_la_evaluacion_de_otro(self):
        self.client.force_login(self.otro_profesional)
        self.assertEqual(self.client.post(self._url()).status_code, 404)
        self.assertTrue(
            Evaluacion.objects.filter(pk=self.evaluacion.pk).exists()
        )

    def test_el_autor_puede_eliminar_por_post(self):
        self.client.force_login(self.autor)
        response = self.client.post(self._url())
        self.assertRedirects(
            response, reverse("ergonomia_886:evaluacion_list")
        )
        self.assertFalse(
            Evaluacion.objects.filter(pk=self.evaluacion.pk).exists()
        )

    def test_get_no_elimina(self):
        self.client.force_login(self.autor)
        self.assertEqual(self.client.get(self._url()).status_code, 405)
        self.assertTrue(
            Evaluacion.objects.filter(pk=self.evaluacion.pk).exists()
        )
