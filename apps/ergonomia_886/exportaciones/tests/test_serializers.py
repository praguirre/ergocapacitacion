"""Pruebas del ensamblado de datos y de la coherencia entre apps."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase

from planillas.models import Evaluacion

from exportaciones import vocabulario as voc


class VocabularioTests(TestCase):

    def test_conversion_de_niveles(self):
        self.assertEqual(voc.nivel_a_numero("bajo"), 1)
        self.assertEqual(voc.nivel_a_numero("medio"), 2)
        self.assertEqual(voc.nivel_a_numero("alto"), 3)
        self.assertIsNone(voc.nivel_a_numero("no_aplicable"))
        self.assertIsNone(voc.nivel_a_numero(None))

    def test_marca_si_no_respeta_el_hueco_g2(self):
        self.assertIsNone(voc.marca_si_no(False, respondido=False))
        self.assertIsNone(voc.marca_si_no(True, respondido=False))
        self.assertEqual(voc.marca_si_no(False, respondido=True), "no")
        self.assertEqual(voc.marca_si_no(True, respondido=True), "si")

    def test_formato_argentino_de_fecha_y_numero(self):
        from datetime import date
        from decimal import Decimal

        self.assertEqual(voc.fecha_es(date(2026, 8, 1)), "01/08/2026")
        self.assertEqual(voc.numero_es(Decimal("18.50")), "18,5")


class Planilla1PayloadTests(TestCase):

    def setUp(self):
        self.usuario = get_user_model().objects.create_user("tester", password="x")
        self.evaluacion = Evaluacion.objects.create(
            usuario=self.usuario,
            razon_social="ACME LOGÍSTICA S.A.",
            cuit="30-12345678-9",
            ciiu="5210",
            direccion_establecimiento="Ruta 8 km 60, Pilar",
            provincia="Buenos Aires",
        )

    def test_sin_planilla1_el_payload_declara_que_no_existe(self):
        from exportaciones import serializers
        payload = serializers.build_planilla1_payload(self.evaluacion)
        self.assertFalse(payload["existe"])
        self.assertEqual(payload["factores"], [])
        self.assertEqual(payload["razon_social"], "ACME LOGÍSTICA S.A.")

    def test_devuelve_siempre_los_nueve_factores_en_orden(self):
        from exportaciones import serializers
        from planillas.models import FactorRiesgo, Planilla1
        planilla1 = Planilla1.objects.create(
            evaluacion=self.evaluacion, area_sector="Depósito",
            puesto_trabajo="Preparador", nro_trabajadores=14,
        )
        FactorRiesgo.objects.create(planilla1=planilla1, tipo_factor="C",
                                    presente=True, tiempo_exposicion="4 h")
        payload = serializers.build_planilla1_payload(self.evaluacion)
        self.assertEqual(
            [f["tipo"] for f in payload["factores"]],
            ["A", "B", "C", "D", "E", "F", "G", "H", "I"],
        )

    def test_la_presencia_por_tarea_se_deriva_del_nivel_asignado(self):
        from exportaciones import serializers
        from planillas.models import FactorRiesgo, Planilla1
        planilla1 = Planilla1.objects.create(evaluacion=self.evaluacion)
        FactorRiesgo.objects.create(
            planilla1=planilla1, tipo_factor="A", presente=True,
            riesgo_tarea1=3, riesgo_tarea3=1,
        )
        factor = next(
            f for f in serializers.build_planilla1_payload(self.evaluacion)["factores"]
            if f["tipo"] == "A"
        )
        self.assertTrue(factor["tarea1"])
        self.assertFalse(factor["tarea2"])
        self.assertTrue(factor["tarea3"])
        self.assertEqual(factor["nivel1"], "3")
        self.assertEqual(factor["nivel2"], "")
        self.assertEqual(factor["nivel3"], "1")

    def test_los_booleanos_se_expresan_como_si_o_no(self):
        from exportaciones import serializers
        from planillas.models import Planilla1
        Planilla1.objects.create(
            evaluacion=self.evaluacion,
            procedimiento_escrito=True, capacitacion=False,
        )
        payload = serializers.build_planilla1_payload(self.evaluacion)
        self.assertEqual(payload["procedimiento_escrito"], "SI")
        self.assertEqual(payload["capacitacion"], "NO")


class Planilla2PayloadTests(TestCase):

    def setUp(self):
        self.usuario = get_user_model().objects.create_user("tester2", password="x")
        self.evaluacion = Evaluacion.objects.create(
            usuario=self.usuario, razon_social="ACME", cuit="30-1-9",
            direccion_establecimiento="X", provincia="Buenos Aires",
        )

    def test_sin_instancia_no_se_marca_ningun_item(self):
        from exportaciones import serializers
        payloads = serializers.build_planilla2_payloads(self.evaluacion, "planilla2a")
        self.assertEqual(len(payloads), 1)
        self.assertFalse(payloads[0]["existe"])
        self.assertEqual(payloads[0]["respuestas"], {})

    def test_guardada_distingue_si_de_no(self):
        from exportaciones import serializers
        from planillas.models import Planilla2A
        Planilla2A.objects.create(
            evaluacion=self.evaluacion, tarea_nro="1",
            p1_levanta_2_a_25kg=True, p1_ciclico_diario=False,
        )
        respuestas = serializers.build_planilla2_payloads(
            self.evaluacion, "planilla2a")[0]["respuestas"]
        self.assertEqual(respuestas["p1_levanta_2_a_25kg"], "si")
        self.assertEqual(respuestas["p1_ciclico_diario"], "no")
        self.assertEqual(len(respuestas), 9)

    def test_varias_tareas_producen_varios_payloads(self):
        from exportaciones import serializers
        from planillas.models import Planilla2A
        Planilla2A.objects.create(evaluacion=self.evaluacion, tarea_nro="1")
        Planilla2A.objects.create(evaluacion=self.evaluacion, tarea_nro="2")
        payloads = serializers.build_planilla2_payloads(self.evaluacion, "planilla2a")
        self.assertEqual(len(payloads), 2)
        self.assertEqual([p["tarea_nro"] for p in payloads], ["1", "2"])

    def test_las_nueve_planillas_responden(self):
        from exportaciones import serializers
        for slug in serializers.PLANILLA2_MODELOS:
            with self.subTest(slug=slug):
                payloads = serializers.build_planilla2_payloads(self.evaluacion, slug)
                self.assertEqual(len(payloads), 1)
                self.assertIn("respuestas", payloads[0])

    def test_2g_expone_los_nueve_campos_de_sus_cuatro_tablas(self):
        from exportaciones import serializers
        from planillas.models import Planilla2G
        Planilla2G.objects.create(
            evaluacion=self.evaluacion, p1_mb_trabaja_con_herramientas=True,
            p2_ce_supera_limites=True,
        )
        respuestas = serializers.build_planilla2_payloads(
            self.evaluacion, "planilla2g")[0]["respuestas"]
        self.assertEqual(len(respuestas), 9)
        self.assertEqual(respuestas["p1_mb_trabaja_con_herramientas"], "si")
        self.assertEqual(respuestas["p2_ce_supera_limites"], "si")
        self.assertEqual(respuestas["p1_ce_conduce_vehiculos"], "no")


class OrdenDeMedidasTests(TestCase):
    """Hueco G-6: la numeración debe ser estable y coincidir con la pantalla."""

    def test_las_medidas_se_numeran_por_pk_ascendente(self):
        from exportaciones import serializers
        from planillas.models import MedidaEspecifica, Planilla3
        usuario = get_user_model().objects.create_user("tester3", password="x")
        evaluacion = Evaluacion.objects.create(
            usuario=usuario, razon_social="ACME", cuit="30-1-9",
            direccion_establecimiento="X", provincia="Buenos Aires",
        )
        planilla3 = Planilla3.objects.create(evaluacion=evaluacion)
        for texto in ("Tercera", "Primera", "Segunda"):
            MedidaEspecifica.objects.create(planilla3=planilla3, descripcion=texto)
        payload = serializers.build_planilla3_payload(evaluacion)
        self.assertEqual([m["numero"] for m in payload["especificas"]], [1, 2, 3])
        self.assertEqual([m["descripcion"] for m in payload["especificas"]], ["Tercera", "Primera", "Segunda"])


class Planilla4PayloadTests(TestCase):

    def setUp(self):
        self.usuario = get_user_model().objects.create_user("tester4", password="x")
        self.evaluacion = Evaluacion.objects.create(
            usuario=self.usuario, razon_social="ACME", cuit="30-1-9",
            direccion_establecimiento="X", provincia="Buenos Aires",
        )

    def test_medida_sin_seguimiento_produce_fila_con_numero_y_resto_vacio(self):
        from exportaciones import serializers
        from planillas.models import MedidaEspecifica, Planilla3
        planilla3 = Planilla3.objects.create(evaluacion=self.evaluacion)
        MedidaEspecifica.objects.create(planilla3=planilla3, descripcion="Rediseñar mesa")
        fila = serializers.build_planilla4_payload(self.evaluacion)["filas"][0]
        self.assertEqual(fila["numero"], "1")
        self.assertEqual(fila["nombre_puesto"], "")
        self.assertEqual(fila["fecha_cierre"], "")
        self.assertEqual(fila["descripcion_medida"], "Rediseñar mesa")

    def test_las_fechas_salen_en_formato_argentino(self):
        from datetime import date
        from exportaciones import serializers
        from planillas.models import MedidaEspecifica, Planilla3, SeguimientoMedida
        planilla3 = Planilla3.objects.create(evaluacion=self.evaluacion)
        medida = MedidaEspecifica.objects.create(planilla3=planilla3, descripcion="M1")
        SeguimientoMedida.objects.create(
            medida_especifica=medida, nombre_puesto="Preparador",
            fecha_evaluacion=date(2026, 6, 12), nivel_riesgo=3,
        )
        fila = serializers.build_planilla4_payload(self.evaluacion)["filas"][0]
        self.assertEqual(fila["fecha_evaluacion"], "12/06/2026")
        self.assertEqual(fila["nivel_riesgo"], "3")


class CoherenciaConEvaluacionesTests(TestCase):
    """`exportaciones` replica `_factor_operational_state`; no debe divergir."""

    def setUp(self):
        from evaluaciones.models import RiskEvaluation
        usuario = get_user_model().objects.create_user("tester-coherencia", password="x")
        self.evaluacion = Evaluacion.objects.create(
            usuario=usuario, razon_social="ACME", cuit="30-1-9",
            direccion_establecimiento="X", provincia="Buenos Aires",
        )
        self.risk_eval = RiskEvaluation.objects.create(evaluacion=self.evaluacion)

    def test_estado_operativo_coincide_con_evaluaciones(self):
        from evaluaciones.models import LMC_Eval
        from evaluaciones.views import _factor_operational_state
        from exportaciones import serializers
        escenarios = [
            {"estado_resultado": "borrador"},
            {"estado_resultado": "desactualizado"},
            {"estado_resultado": "calculado"},
            {"estado_resultado": "calculado", "revisado_en": "2026-07-31T10:00:00",
             "revisado_por": {"id": 1, "username": "tester"}},
        ]
        for calc_data in escenarios:
            with self.subTest(calc_data=calc_data):
                instancia = LMC_Eval.objects.create(
                    risk_evaluation=self.risk_eval, factor_slug="lmc",
                    nivel_riesgo="alto", calc_data=calc_data,
                )
                self.assertEqual(
                    serializers._estado_operativo(instancia, calc_data),
                    _factor_operational_state(instancia),
                )
                instancia.delete()


class FactorPayloadTests(TestCase):

    def setUp(self):
        self.usuario = get_user_model().objects.create_user("factor", password="x")
        self.evaluacion = Evaluacion.objects.create(
            usuario=self.usuario, razon_social="ACME", cuit="30-1-9",
            direccion_establecimiento="X", provincia="Buenos Aires",
        )
        from evaluaciones.models import RiskEvaluation
        self.risk_eval = RiskEvaluation.objects.create(evaluacion=self.evaluacion)

    def test_factor_sin_iniciar_se_declara_como_inexistente(self):
        from exportaciones import serializers
        payload = serializers.build_factor_payload(self.risk_eval, "lmc")
        self.assertFalse(payload["existe"])
        self.assertEqual(payload["estado_operativo"], "sin_iniciar")

    def test_los_trece_factores_producen_payload(self):
        from evaluaciones.catalog import FACTOR_DEFINITIONS
        from exportaciones import serializers
        for definicion in FACTOR_DEFINITIONS:
            with self.subTest(slug=definicion.slug):
                payload = serializers.build_factor_payload(
                    self.risk_eval, definicion.slug)
                self.assertEqual(payload["factor_slug"], definicion.slug)
                self.assertEqual(payload["factor_label"], definicion.label)

    def test_el_payload_conserva_calc_data_integro(self):
        from evaluaciones.models import LMC_Eval
        from exportaciones import serializers
        trazas = {
            "estado_resultado": "calculado",
            "limite_base_kg": 14.0,
            "calculation_trace": {
                "engine_version": "1.0.0",
                "sources": [{"archivo": "lmc_tablas.json", "sha256": "abc123"}],
            },
        }
        LMC_Eval.objects.create(
            risk_evaluation=self.risk_eval, factor_slug="lmc",
            nivel_riesgo="alto", calc_data=trazas,
            peso_kg="18.50", duracion_h="6.00", frecuencia_h=20,
            v_altura="suelo_espinilla", h_dist="intermedio",
        )
        payload = serializers.build_factor_payload(self.risk_eval, "lmc")
        self.assertEqual(payload["calc_data"], trazas)
        self.assertEqual(payload["fuentes"][0]["sha256"], "abc123")
        self.assertEqual(payload["nivel_numerico_srt"], 3)

    def test_los_choices_se_exponen_con_su_etiqueta_legible(self):
        from evaluaciones.models import LMC_Eval
        from exportaciones import serializers
        LMC_Eval.objects.create(
            risk_evaluation=self.risk_eval, factor_slug="lmc",
            v_altura="espinilla_nudillos", h_dist="intermedio",
            calc_data={"estado_resultado": "calculado"},
        )
        inputs = serializers.build_factor_payload(self.risk_eval, "lmc")["inputs"]
        self.assertEqual(inputs["v_altura"], "Mitad espinilla a nudillos")
        self.assertEqual(inputs["h_dist"], "Intermedio (30–60 cm)")

    def test_vce_incluye_tramos_y_declara_evidencia_sin_adjuntarla(self):
        from evaluaciones.models import VCESegment, VibracionCE_Eval
        from exportaciones import serializers
        vce = VibracionCE_Eval.objects.create(
            risk_evaluation=self.risk_eval, factor_slug="vibracion_cuerpo_entero",
            calc_data={"estado_resultado": "calculado"},
        )
        VCESegment.objects.create(
            evaluation=vce, vehiculo_maquina="Autoelevador Toyota",
            tiempo_horas="3.50", aw_x="0.420", aw_y="0.380", aw_z="0.910",
        )
        payload = serializers.build_factor_payload(
            self.risk_eval, "vibracion_cuerpo_entero")
        self.assertEqual(len(payload["segmentos"]), 1)
        self.assertEqual(payload["segmentos"][0]["vehiculo_maquina"],
                         "Autoelevador Toyota")
        self.assertFalse(payload["evidencia_declarada"]["adjunta"])


class HuellaDePayloadTests(TestCase):

    def test_la_huella_es_estable_ante_el_orden_de_las_claves(self):
        from exportaciones.models import payload_fingerprint
        a = {"factor_slug": "lmc", "inputs": {"peso_kg": 18.5, "duracion_h": 6}}
        b = {"inputs": {"duracion_h": 6, "peso_kg": 18.5}, "factor_slug": "lmc"}
        self.assertEqual(payload_fingerprint(a), payload_fingerprint(b))

    def test_la_huella_cambia_si_cambia_un_valor(self):
        from exportaciones.models import payload_fingerprint
        a = {"inputs": {"peso_kg": 18.5}}
        b = {"inputs": {"peso_kg": 25.0}}
        self.assertNotEqual(payload_fingerprint(a), payload_fingerprint(b))
