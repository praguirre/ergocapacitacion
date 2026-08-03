"""Vinculación opcional de Planilla 1 con la nómina de la empresa."""

import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.company.models import CompanyProfile, CompanyWorker
from apps.ergonomia_886.exportaciones import serializers
from apps.ergonomia_886.exportaciones.models import GeneratedReport, TipoDocumento
from apps.ergonomia_886.exportaciones.official.builders import build_planilla1_pages
from apps.ergonomia_886.exportaciones.reports.llm import sanitize_payload

from .forms import Planilla1Form
from .models import Evaluacion, Planilla1


class TrabajadoresPlanilla1Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.profesional = User.objects.create_professional(
            email="nomina-prof@test.local", username="nomina-prof", password="prueba"
        )
        cls.usuario_empresa = User.objects.create_company(
            email="nomina-empresa@test.local",
            username="nomina-empresa",
            password="prueba",
        )
        cls.empresa = CompanyProfile.objects.create(
            user=cls.usuario_empresa,
            razon_social="ACME",
            cuit="30-12345678-9",
            contacto_nombre="Contacto",
        )
        cls.trabajador = User.objects.create_trainee(
            cuil="20-11111111-1",
            email="persona.identificable@test.local",
            username="persona-identificable",
            dni="11111111",
            full_name="Persona de Nómina",
        )
        cls.relacion = CompanyWorker.objects.create(
            company=cls.empresa,
            worker=cls.trabajador,
            employee_code="L-001",
        )
        cls.evaluacion = Evaluacion.objects.create(
            usuario=cls.profesional,
            empresa=cls.empresa,
            razon_social="ACME",
            cuit="30-12345678-9",
            direccion_establecimiento="Ruta 8",
            provincia="Buenos Aires",
        )

    def _datos(self, **overrides):
        datos = {
            "area_sector": "Depósito",
            "puesto_trabajo": "Preparador",
            "nro_trabajadores": 20,
            "nombres_trabajadores": "",
            "trabajadores": [self.relacion.pk],
        }
        datos.update(overrides)
        return datos

    def test_la_nomina_se_ofrece_solo_para_la_empresa_de_la_evaluacion(self):
        planilla = Planilla1(evaluacion=self.evaluacion)
        form = Planilla1Form(instance=planilla)
        self.assertIn("trabajadores", form.fields)
        self.assertQuerySetEqual(
            form.fields["trabajadores"].queryset,
            [self.relacion],
            ordered=False,
        )

    def test_la_seleccion_deriva_el_snapshot_solo_si_esta_vacio(self):
        planilla = Planilla1(evaluacion=self.evaluacion)
        form = Planilla1Form(data=self._datos(), instance=planilla)
        self.assertTrue(form.is_valid(), form.errors)
        guardada = form.save()
        self.assertEqual(guardada.nombres_trabajadores, "Persona de Nómina")
        self.assertEqual(guardada.nro_trabajadores, 20)
        self.assertEqual(list(guardada.trabajadores.all()), [self.relacion])

    def test_el_texto_escrito_por_el_profesional_nunca_se_sobrescribe(self):
        form = Planilla1Form(
            data=self._datos(nombres_trabajadores="Personal de turno noche"),
            instance=Planilla1(evaluacion=self.evaluacion),
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().nombres_trabajadores, "Personal de turno noche")

    def test_sin_empresa_no_hay_selector_y_el_texto_funciona(self):
        evaluacion = Evaluacion.objects.create(
            usuario=self.profesional,
            razon_social="Empresa externa",
            cuit="30-99999999-9",
            direccion_establecimiento="Otra 100",
            provincia="Córdoba",
        )
        planilla = Planilla1(evaluacion=evaluacion)
        form = Planilla1Form(
            data={
                "area_sector": "Taller",
                "puesto_trabajo": "Mecánico",
                "nro_trabajadores": 4,
                "nombres_trabajadores": "Cuadrilla externa",
            },
            instance=planilla,
        )
        self.assertNotIn("trabajadores", form.fields)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().nombres_trabajadores, "Cuadrilla externa")

    def test_cf5_el_pdf_imprime_el_snapshot_y_no_la_relacion(self):
        planilla = Planilla1.objects.create(
            evaluacion=self.evaluacion,
            nombres_trabajadores="Snapshot declarado",
        )
        planilla.trabajadores.add(self.relacion)
        payload = serializers.build_planilla1_payload(self.evaluacion)
        textos = [op.text for op in build_planilla1_pages(payload)[0].ops]
        self.assertIn("Snapshot declarado", textos)
        self.assertNotIn("Persona de Nómina", textos)

    def test_cf4_un_reporte_real_no_conserva_cuil_dni_email_ni_relacion(self):
        planilla = Planilla1.objects.create(evaluacion=self.evaluacion)
        planilla.trabajadores.add(self.relacion)
        payload = {
            "factor_slug": "lmc",
            "nivel_riesgo": "alto",
            "trabajadores": [
                {
                    "cuil": relacion.worker.cuil,
                    "dni": relacion.worker.dni,
                    "email": relacion.worker.email,
                    "employee_code": relacion.employee_code,
                }
                for relacion in planilla.trabajadores.select_related("worker")
            ],
            "inputs": {"peso_kg": 25},
        }
        limpio = sanitize_payload(payload)
        reporte = GeneratedReport.objects.create(
            evaluacion=self.evaluacion,
            tipo=TipoDocumento.INFORME_FACTOR,
            factor_slug="lmc",
            payload_json=limpio,
            inputs_hash="a" * 64,
        )
        serializado = json.dumps(reporte.payload_json)
        for prohibido in (
            "20-11111111-1", "11111111", "persona.identificable@test.local",
            "L-001", "trabajadores",
        ):
            self.assertNotIn(prohibido, serializado)
        self.assertEqual(reporte.payload_json["inputs"]["peso_kg"], 25)
