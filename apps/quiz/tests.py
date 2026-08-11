from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.training.models import CapacitacionLink, TrainingModule

from .models import Question, QuizAttempt


class QuizAttemptAttributionTests(TestCase):
    """La identidad del emisor se fija al iniciar el intento online."""

    def setUp(self):
        User = get_user_model()
        self.client = Client()
        self.professional = User.objects.create_professional(
            email="responsable@test.local",
            username="responsable",
            password="prueba",
            full_name="Responsable Correcta",
            profession="Lic. en Higiene y Seguridad",
            license_number="MP 456",
        )
        self.trainee = User.objects.create_trainee(
            cuil="20-20000000-2",
            email="intento@test.local",
            full_name="Trabajador Intento",
        )
        self.module = TrainingModule.objects.create(
            slug="modulo-attrib",
            title="Módulo atribuido",
            youtube_id="attrib123",
            is_active=True,
        )
        Question.objects.create(module=self.module, order=1, text="Pregunta")
        self.link = CapacitacionLink.objects.create(
            module=self.module,
            created_by=self.professional,
        )
        self.client.force_login(self.trainee)

    def _remember_link(self, link):
        session = self.client.session
        session["capacitacion_ref"] = str(link.id)
        session.save()

    def test_start_persiste_el_link_validado(self):
        self._remember_link(self.link)

        response = self.client.post(
            reverse("quiz:quiz_start", args=[self.module.slug])
        )

        self.assertEqual(response.status_code, 200)
        attempt = QuizAttempt.objects.get(user=self.trainee)
        self.assertEqual(attempt.capacitacion_link, self.link)

    def test_start_sin_link_rechaza_la_emision_no_atribuible(self):
        response = self.client.post(
            reverse("quiz:quiz_start", args=[self.module.slug])
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], "missing_training_link")
        self.assertFalse(QuizAttempt.objects.exists())

    def test_link_de_otro_modulo_no_se_reutiliza_y_se_limpia(self):
        other = TrainingModule.objects.create(
            slug="otro-modulo",
            title="Otro módulo",
            youtube_id="other123",
            is_active=True,
        )
        other_link = CapacitacionLink.objects.create(
            module=other,
            created_by=self.professional,
        )
        self._remember_link(other_link)

        response = self.client.post(
            reverse("quiz:quiz_start", args=[self.module.slug])
        )

        self.assertEqual(response.status_code, 403)
        self.assertNotIn("capacitacion_ref", self.client.session)

    def test_link_creado_por_empresa_no_finge_ser_profesional(self):
        company = get_user_model().objects.create_company(
            email="empresa-link@test.local",
            username="empresa-link",
            password="prueba",
        )
        company_link = CapacitacionLink.objects.create(
            module=self.module,
            created_by=company,
        )
        self._remember_link(company_link)

        response = self.client.post(
            reverse("quiz:quiz_start", args=[self.module.slug])
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            response.json()["error"],
            "invalid_training_responsible",
        )

    def test_link_inactivo_se_rechaza_y_se_limpia(self):
        self.link.is_active = False
        self.link.save(update_fields=["is_active"])
        self._remember_link(self.link)

        response = self.client.post(
            reverse("quiz:quiz_start", args=[self.module.slug])
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(QuizAttempt.objects.exists())
        self.assertNotIn("capacitacion_ref", self.client.session)
