"""Proyección explícita y unidireccional de Planilla 4 a la agenda."""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.company.models import AgendaEvent, CompanyProfile

from .agenda import RELATED_OBJECT_TYPE, sincronizar_medida_con_agenda
from .models import Evaluacion, MedidaEspecifica, Planilla3, SeguimientoMedida


class SincronizacionAgendaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.profesional = User.objects.create_professional(
            email="agenda-886-prof@test.local",
            username="agenda-886-prof",
            password="prueba",
        )
        usuario_empresa = User.objects.create_company(
            email="agenda-886-empresa@test.local",
            username="agenda-886-empresa",
            password="prueba",
        )
        cls.empresa = CompanyProfile.objects.create(
            user=usuario_empresa,
            razon_social="ACME",
            cuit="30-12345678-9",
            contacto_nombre="Contacto",
        )

    def setUp(self):
        self.evaluacion = Evaluacion.objects.create(
            usuario=self.profesional,
            empresa=self.empresa,
            razon_social="ACME",
            cuit="30-12345678-9",
            direccion_establecimiento="Ruta 8",
            provincia="Buenos Aires",
        )
        self.planilla3 = Planilla3.objects.create(evaluacion=self.evaluacion)
        self.medida = MedidaEspecifica.objects.create(
            planilla3=self.planilla3,
            descripcion="Instalar ayuda mecánica",
            observaciones="Verificar antes del cierre",
        )
        self.seguimiento = SeguimientoMedida.objects.create(
            medida_especifica=self.medida,
            nombre_puesto="Preparador",
            fecha_evaluacion=date(2026, 8, 3),
            nivel_riesgo=3,
        )

    def _post_planilla4(self, *, fecha="2026-08-20", cierre=""):
        self.client.force_login(self.profesional)
        return self.client.post(
            reverse("planillas:planilla4", args=[self.evaluacion.pk]),
            {
                "seg-TOTAL_FORMS": "1",
                "seg-INITIAL_FORMS": "1",
                "seg-MIN_NUM_FORMS": "0",
                "seg-MAX_NUM_FORMS": "1000",
                "seg-0-id": str(self.seguimiento.pk),
                "seg-0-nombre_puesto": "Preparador",
                "seg-0-fecha_evaluacion": "2026-08-03",
                "seg-0-nivel_riesgo": "3",
                "seg-0-fecha_impl_admin": "",
                "seg-0-fecha_impl_ing": fecha,
                "seg-0-fecha_cierre": cierre,
            },
        )

    def test_guardar_la_planilla4_crea_un_evento_de_agenda(self):
        respuesta = self._post_planilla4()
        self.assertEqual(respuesta.status_code, 302)
        evento = AgendaEvent.objects.get()
        self.assertEqual(evento.company, self.empresa)
        self.assertEqual(evento.event_type, AgendaEvent.EventType.EVALUATION_DUE)
        self.assertEqual(evento.related_object_type, RELATED_OBJECT_TYPE)
        self.assertEqual(evento.related_object_id, str(self.seguimiento.pk))
        self.assertEqual(evento.assigned_professional, self.profesional)

    def test_reeditarla_actualiza_el_evento_sin_duplicarlo(self):
        self._post_planilla4(fecha="2026-08-20")
        self._post_planilla4(fecha="2026-09-15")
        self.assertEqual(AgendaEvent.objects.count(), 1)
        self.assertEqual(AgendaEvent.objects.get().due_at.date(), date(2026, 9, 15))

    def test_cerrar_la_medida_marca_el_evento_como_completado(self):
        self._post_planilla4(cierre="2026-08-18")
        self.assertEqual(
            AgendaEvent.objects.get().status,
            AgendaEvent.EventStatus.COMPLETED,
        )

    def test_una_evaluacion_sin_empresa_no_crea_evento_y_no_falla(self):
        self.evaluacion.empresa = None
        self.evaluacion.save(update_fields=["empresa"])
        self.seguimiento.fecha_impl_ing = date(2026, 8, 20)
        self.seguimiento.save(update_fields=["fecha_impl_ing"])
        self.assertIsNone(sincronizar_medida_con_agenda(self.seguimiento))
        self.assertFalse(AgendaEvent.objects.exists())

    def test_una_medida_sin_fecha_comprometida_no_crea_evento(self):
        self.assertIsNone(sincronizar_medida_con_agenda(self.seguimiento))
        self.assertFalse(AgendaEvent.objects.exists())

    def test_cf2_la_prioridad_no_altera_el_nivel_de_riesgo_persistido(self):
        self.seguimiento.fecha_impl_admin = date(2026, 8, 30)
        self.seguimiento.save(update_fields=["fecha_impl_admin"])
        evento = sincronizar_medida_con_agenda(self.seguimiento)
        self.assertEqual(evento.priority, AgendaEvent.Priority.URGENT)
        self.seguimiento.refresh_from_db()
        self.assertEqual(self.seguimiento.nivel_riesgo, 3)
