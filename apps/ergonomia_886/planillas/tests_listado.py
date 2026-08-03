"""Pruebas del listado de evaluaciones ergonómicas."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.company.models import CompanyProfile

from .models import Evaluacion, Planilla1


class EvaluacionListTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.profesional = User.objects.create_user(
            email="listado-prof@example.com", username="listado-prof",
            password="test-password", user_type="professional",
        )
        cls.otro_profesional = User.objects.create_user(
            email="listado-otro@example.com", username="listado-otro",
            password="test-password", user_type="professional",
        )
        cls.user_empresa = User.objects.create_user(
            email="listado-empresa@example.com", username="listado-empresa",
            password="test-password", user_type="company",
        )
        cls.empresa = CompanyProfile.objects.create(
            user=cls.user_empresa, razon_social="Empresa vinculada S.A.",
            cuit="30-55555555-5", contacto_nombre="Contacto listado",
        )
        cls.principal = cls._crear(
            cls.profesional, "Alfa Industrial", "30-11111111-1",
            "Córdoba", "Parque Industrial Norte",
        )
        Planilla1.objects.create(
            evaluacion=cls.principal,
            area_sector="Depósito Central",
            puesto_trabajo="Operario de expedición",
        )
        cls.ajena = cls._crear(
            cls.otro_profesional, "Beta Logística", "30-22222222-2",
            "Mendoza", "Ruta Nacional 7",
        )
        for index in range(21):
            cls._crear(
                cls.profesional, f"Empresa {index:02d}", f"30-{index:08d}-0",
                "Buenos Aires", f"Domicilio {index}", empresa=None,
            )
        ayer = timezone.now() - timedelta(days=1)
        Evaluacion.objects.filter(pk=cls.principal.pk).update(
            fecha_creacion=ayer, fecha_modificacion=ayer,
        )

    @classmethod
    def _crear(cls, usuario, razon, cuit, provincia, domicilio, empresa=None):
        if empresa is None and hasattr(cls, "empresa"):
            empresa = cls.empresa
        return Evaluacion.objects.create(
            usuario=usuario, empresa=empresa, razon_social=razon, cuit=cuit,
            direccion_establecimiento=domicilio, provincia=provincia,
        )

    def setUp(self):
        self.url = reverse("ergonomia_886:evaluacion_list")

    def test_ruta_template_ayuda_y_propiedad_profesional(self):
        self.client.force_login(self.profesional)
        response = self.client.get(self.url, {"search": "Alfa Industrial"})
        self.assertEqual(self.url, "/evaluacion-ergonomica/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "planillas/evaluacion_list.html")
        self.assertContains(response, 'data-page-slug="dashboard"')
        self.assertContains(response, self.principal.razon_social)
        self.assertNotContains(response, self.ajena.razon_social)
        self.assertTrue(response.context["puede_crear"])

    def test_busqueda_cubre_los_seis_campos(self):
        self.client.force_login(self.profesional)
        for termino in (
            "Alfa", "30-11111111-1", "Córdoba", "Parque Industrial",
            "Depósito Central", "Operario de expedición",
        ):
            with self.subTest(termino=termino):
                response = self.client.get(self.url, {"search": termino})
                self.assertEqual(response.context["total_resultados"], 1)
                self.assertEqual(
                    list(response.context["evaluaciones"]), [self.principal]
                )

    def test_tres_filtros_seis_ordenamientos_y_lista_blanca(self):
        self.client.force_login(self.profesional)
        hoy = timezone.localdate().isoformat()
        self.assertEqual(
            self.client.get(self.url, {"provincia": "Córdoba"}).context[
                "total_resultados"
            ],
            1,
        )
        self.assertGreaterEqual(
            self.client.get(self.url, {"fecha_desde": hoy}).context[
                "total_resultados"
            ],
            21,
        )
        self.assertGreaterEqual(
            self.client.get(self.url, {"fecha_hasta": hoy}).context[
                "total_resultados"
            ],
            22,
        )
        for orden in (
            "-fecha_modificacion", "fecha_modificacion", "-fecha_creacion",
            "fecha_creacion", "razon_social", "-razon_social",
        ):
            with self.subTest(orden=orden):
                self.assertEqual(
                    self.client.get(self.url, {"orden": orden}).context[
                        "current_orden"
                    ],
                    orden,
                )
        self.assertEqual(
            self.client.get(self.url, {"orden": "usuario__password"}).context[
                "current_orden"
            ],
            "-fecha_modificacion",
        )

    def test_paginacion_es_de_veinte(self):
        self.client.force_login(self.profesional)
        page = self.client.get(self.url).context["evaluaciones"]
        self.assertEqual(page.paginator.per_page, 20)
        self.assertTrue(page.has_next())

    def test_empresa_ve_su_empresa_pero_no_el_boton_de_alta(self):
        self.client.force_login(self.user_empresa)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Nueva Evaluación")
        self.assertFalse(response.context["puede_crear"])
        for evaluacion in (self.principal, self.ajena):
            with self.subTest(evaluacion=evaluacion.pk):
                filtered = self.client.get(
                    self.url, {"search": evaluacion.razon_social}
                )
                self.assertContains(filtered, evaluacion.razon_social)
