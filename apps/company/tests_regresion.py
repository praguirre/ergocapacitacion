"""Regresiones verificadas de la Etapa 3 (N1 y N2).

Estas pruebas existen porque las 32 pruebas originales pasaban con ambos
defectos presentes: ninguna cubria el acceso anonimo ni la ficha con
QuizState poblado.
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.company.models import CompanyProfile, CompanyWorker
from apps.quiz.models import QuizState
from apps.training.models import TrainingModule

User = get_user_model()

TEST_STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


class AccesoAnonimoBackofficeTests(TestCase):
    """N1: ninguna ruta de backoffice devuelve HTTP 500 sin sesion."""

    RUTAS = [
        "/dashboard/",
        "/dashboard/capacitaciones/",
        "/dashboard/perfil/",
        "/dashboard/empresa/nomina/",
        "/dashboard/empresa/nomina/agregar/",
        "/dashboard/empresa/nomina/exportar/",
        "/dashboard/empresa/agenda/",
        "/dashboard/empresa/agenda/crear/",
        "/dashboard/empresa/directorio/",
        "/dashboard/solicitudes-contacto/",
    ]

    def test_ninguna_ruta_de_backoffice_devuelve_500_a_un_anonimo(self):
        cliente = Client()
        for ruta in self.RUTAS:
            with self.subTest(ruta=ruta):
                respuesta = cliente.get(ruta)
                self.assertNotEqual(
                    respuesta.status_code,
                    500,
                    f"{ruta} devuelve HTTP 500 a un usuario anonimo",
                )
                self.assertIn(
                    respuesta.status_code,
                    (302, 403),
                    f"{ruta} deberia redirigir o denegar, devolvio "
                    f"{respuesta.status_code}",
                )

    def test_el_anonimo_es_redirigido_a_un_login_que_existe(self):
        respuesta = Client().get("/dashboard/empresa/nomina/")
        self.assertEqual(respuesta.status_code, 302)
        # `login_required` es la capa exterior y usa el LOGIN_URL global.
        # El objetivo de N1 es que el destino exista y no produzca un 500.
        self.assertIn(resolve_url(settings.LOGIN_URL), respuesta.url)


@override_settings(STORAGES=TEST_STORAGES)
class FichaTrabajadorConQuizStateTests(TestCase):
    """N2: la ficha rompia cuando el trabajador ya habia rendido un quiz."""

    @classmethod
    def setUpTestData(cls):
        cls.empresa_user = User.objects.create_company(
            email="empresa@test.local", password="x", username="empresa-test",
        )
        cls.perfil = CompanyProfile.objects.create(
            user=cls.empresa_user,
            razon_social="ACME S.A.",
            cuit="30-12345678-9",
            contacto_nombre="Contacto",
        )
        cls.trabajador = User.objects.create_trainee(
            cuil="20-11111111-1", email="trabajador@test.local",
            first_name="Juan", last_name="Perez",
        )
        cls.asignacion = CompanyWorker.objects.create(
            company=cls.perfil, worker=cls.trabajador,
        )
        cls.modulo = TrainingModule.objects.create(
            slug="ergonomia-regresion",
            title="Ergonomía — prueba de regresión",
            youtube_id="test-video",
            is_active=True,
        )

    def setUp(self):
        self.client.force_login(self.empresa_user)

    def test_ficha_sin_quizstate_responde_200(self):
        url = reverse(
            "dashboard:company:nomina_detail",
            kwargs={"worker_id": self.asignacion.pk},
        )
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_ficha_con_quizstate_responde_200(self):
        """Es el caso que rompia: QuizState existe y se consulta is_approved."""
        QuizState.objects.create(
            user=self.trabajador, module=self.modulo,
            attempts_used=1, last_passed=True,
        )
        url = reverse(
            "dashboard:company:nomina_detail",
            kwargs={"worker_id": self.asignacion.pk},
        )
        respuesta = self.client.get(url)
        self.assertEqual(
            respuesta.status_code,
            200,
            "La ficha con QuizState poblado debe renderizar (N2)",
        )
        estados = respuesta.context["module_status"]
        aprobados = [e for e in estados if e["module"].pk == self.modulo.pk]
        self.assertTrue(aprobados[0]["is_approved"])
