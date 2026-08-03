from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import get_template, render_to_string
from django.test import SimpleTestCase, TestCase
from django.urls import resolve, reverse
from django.utils.module_loading import import_string

from apps.ergonomia_886.planillas.models import Evaluacion, Planilla2E

from .catalog import FACTOR_CATALOG, FACTOR_DEFINITIONS
from .calculators import (
    CalcResult,
    REGISTRY,
    _cat_por_duracion,
    _lookup_limite_transporte,
    apply_result,
    calc_bipedestacion,
    calc_posturas_forzadas,
    calc_vibracion_cuerpo_entero,
    calc_vibracion_mano_brazo,
    data_source_info,
    load_json,
    run_for_instance,
)
from .choices import FactorSlug
from .forms import (
    BipedestacionForm,
    ConfortTermicoForm,
    EmpujeInicialForm,
    EmpujeSostenidaForm,
    EstresContactoForm,
    LMCForm,
    PosturasForzadasForm,
    RepetitivosMSForm,
    TraccionInicialForm,
    TraccionSostenidaForm,
    TransporteForm,
    VCESegmentForm,
    VibracionCEForm,
    VibracionMBForm,
)
from .models import (
    Bipedestacion_Eval,
    ConfortTermico_Eval,
    EmpujeInicial_Eval,
    EstresContacto_Eval,
    LMC_Eval,
    PosturasForzadas_Eval,
    RepetitivosMS_Eval,
    RiskEvaluation,
    TraccionInicial_Eval,
    Transporte_Eval,
    VCESegment,
    VibracionCE_Eval,
    VibracionMB_Eval,
)


class FactorCatalogContractTests(SimpleTestCase):
    def test_application_uses_argentina_business_timezone(self):
        self.assertEqual(
            settings.TIME_ZONE,
            "America/Argentina/Buenos_Aires",
        )

    def test_catalog_is_the_shared_contract_for_every_factor(self):
        from apps.ergonomia_886.help_ai.catalog import PAGE_HELP_SLUGS

        catalog_slugs = [definition.slug for definition in FACTOR_DEFINITIONS]
        self.assertEqual(catalog_slugs, [choice.value for choice in FactorSlug])
        self.assertEqual(set(catalog_slugs), set(FACTOR_CATALOG))

        for definition in FACTOR_DEFINITIONS:
            with self.subTest(slug=definition.slug):
                form_class = import_string(definition.form_path)
                model_class = import_string(definition.model_path)
                view_class = import_string(
                    f"apps.ergonomia_886.evaluaciones.views.{definition.view_class}"
                )

                self.assertIs(form_class._meta.model, model_class)
                self.assertEqual(view_class.factor_slug, definition.slug)
                self.assertIs(view_class.form_class, form_class)
                self.assertEqual(
                    view_class.template_name,
                    definition.template_name,
                )
                self.assertEqual(
                    view_class.url_name,
                    definition.route_name_by_eval,
                )
                self.assertEqual(
                    resolve(
                        reverse(
                            f"evaluaciones:{definition.route_name_by_eval}",
                            kwargs={"evaluacion_id": 321},
                        )
                    ).view_name,
                    f"evaluaciones:{definition.route_name_by_eval}",
                )
                get_template(definition.template_name)
                self.assertIn(definition.calculator_slug, REGISTRY)
                self.assertIn(definition.help_slug, PAGE_HELP_SLUGS)

                for data_file in definition.data_files:
                    self.assertTrue(
                        (
                            Path(settings.BASE_DIR)
                            / "apps"
                            / "ergonomia_886"
                            / "evaluaciones"
                            / "data"
                            / data_file
                        ).is_file(),
                        f"Falta la fuente {data_file} de {definition.slug}",
                    )

    def test_every_declared_source_has_versioned_auditable_metadata(self):
        seen = set()
        for definition in FACTOR_DEFINITIONS:
            for data_file in definition.data_files:
                if data_file in seen:
                    continue
                seen.add(data_file)
                with self.subTest(data_file=data_file):
                    meta = load_json(data_file).get("meta")
                    self.assertIsInstance(meta, dict)
                    self.assertRegex(
                        meta["schema_version"],
                        r"^\d+\.\d+\.\d+$",
                    )
                    self.assertRegex(
                        meta["data_version"],
                        r"^\d+\.\d+\.\d+$",
                    )
                    date.fromisoformat(meta["artifact_effective_date"])
                    self.assertTrue(meta["source"].strip())
                    self.assertIn("provenance_status", meta)
                    if meta["source_url"] is not None:
                        self.assertTrue(meta["source_url"].startswith("https://"))

                    approval = meta["professional_approval"]
                    self.assertIn(
                        approval["status"],
                        {"pending", "not_recorded", "approved"},
                    )
                    self.assertIn("approved_by", approval)
                    self.assertIn("approved_at", approval)
                    if approval["status"] == "approved":
                        self.assertTrue(approval["approved_by"])
                        date.fromisoformat(approval["approved_at"])

                    source_info = data_source_info(data_file)
                    self.assertEqual(source_info["archivo"], data_file)
                    self.assertRegex(source_info["sha256"], r"^[0-9a-f]{64}$")


class QuantitativeEvaluationRegressionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="regression-user",
            email="regression-user@example.com",
            password="test-password",
        )
        cls.evaluacion = Evaluacion.objects.create(
            usuario=cls.user,
            razon_social="Empresa de prueba",
            cuit="30-00000000-0",
            direccion_establecimiento="Dirección de prueba",
            provincia="Buenos Aires",
        )
        cls.risk_eval = RiskEvaluation.objects.create(
            evaluacion=cls.evaluacion,
            creado_por=cls.user,
        )

    def test_vce_calculates_energy_integration_for_segments(self):
        evaluation = VibracionCE_Eval.objects.create(
            risk_evaluation=self.risk_eval,
            postura="sentado",
            ubicacion_sensor="isquiones",
        )
        VCESegment.objects.create(
            evaluation=evaluation,
            vehiculo_maquina="Autoelevador",
            tipo_asiento="mecanica",
            superficie_terreno="liso",
            estado_neumaticos="correcto",
            tiempo_horas=Decimal("8.00"),
            aw_x=Decimal("0.200"),
            aw_y=Decimal("0.100"),
            aw_z=Decimal("0.600"),
        )

        result = calc_vibracion_cuerpo_entero(evaluation)

        self.assertEqual(result.nivel, "medio")
        self.assertEqual(result.detalle["eje_dominante"], "Z")
        self.assertEqual(result.detalle["valor_final_a8"], 0.6)

    def test_every_factor_page_loads_for_its_authenticated_owner(self):
        """Cada formulario debe poder construir también el resumen transversal."""
        self.client.force_login(self.user)

        for definition in FACTOR_DEFINITIONS:
            with self.subTest(factor=definition.slug):
                response = self.client.get(
                    reverse(
                        f"evaluaciones:{definition.route_name_by_eval}",
                        kwargs={"evaluacion_id": self.risk_eval.pk},
                    )
                )
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, definition.template_name)

    def test_vce_save_redirects_to_wizard_summary(self):
        self.client.force_login(self.user)
        url = reverse(
            "evaluaciones:vibracion_cuerpo_entero_form_by_eval",
            kwargs={"evaluacion_id": self.risk_eval.pk},
        )
        response = self.client.post(
            url,
            {
                "risk_evaluation": self.risk_eval.pk,
                "metodo": "ponderadas",
                "postura": "sentado",
                "ubicacion_sensor": "isquiones",
                "aplicable": "on",
                "action": "save",
                "segmentos-TOTAL_FORMS": "1",
                "segmentos-INITIAL_FORMS": "0",
                "segmentos-MIN_NUM_FORMS": "0",
                "segmentos-MAX_NUM_FORMS": "1000",
                "segmentos-0-vehiculo_maquina": "Autoelevador",
                "segmentos-0-tipo_asiento": "mecanica",
                "segmentos-0-superficie_terreno": "liso",
                "segmentos-0-estado_neumaticos": "correcto",
                "segmentos-0-tiempo_horas": "8",
                "segmentos-0-aw_x": "0.2",
                "segmentos-0-aw_y": "0.1",
                "segmentos-0-aw_z": "0.6",
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "evaluaciones:wizard_resumen_by_eval",
                kwargs={"evaluacion_id": self.risk_eval.pk},
            ),
            fetch_redirect_response=False,
        )

    def test_contact_stress_persists_friendly_symptoms_and_controls(self):
        form = EstresContactoForm(
            data={
                "risk_evaluation": self.risk_eval.pk,
                "segmento_afectado": "muneca",
                "objeto_superficie": "Borde de mesa",
                "tipo_borde": "duro",
                "duracion_continua_min": "20",
                "frecuencia_exposicion": "moderado",
                "sintomas": ["dolor", "marcas"],
                "controles": ["bordes_redondeados", "rotacion_micropausas"],
                "aplicable": "on",
            }
        )
        self.assertTrue(form.is_valid(), form.errors.as_json())

        evaluation = form.save()
        evaluation.refresh_from_db()

        self.assertEqual(evaluation.sintomas_json, ["dolor", "marcas"])
        self.assertEqual(
            evaluation.controles_existentes_json,
            ["bordes_redondeados", "rotacion_micropausas"],
        )
        self.assertEqual(
            evaluation.calc_data["input"]["sintomas"],
            ["dolor", "marcas"],
        )

        edit_form = EstresContactoForm(instance=evaluation)
        self.assertEqual(edit_form["sintomas"].value(), ["dolor", "marcas"])
        self.assertEqual(
            edit_form["controles"].value(),
            ["bordes_redondeados", "rotacion_micropausas"],
        )

    def test_contact_high_pressure_escalates_one_level_not_directly_high(self):
        form = EstresContactoForm(
            data={
                "risk_evaluation": self.risk_eval.pk,
                "segmento_afectado": "muneca",
                "objeto_superficie": "Apoyo localizado",
                "tipo_borde": "acolchado",
                "duracion_continua_min": "4",
                "frecuencia_exposicion": "bajo",
                "fuerza_n": "16",
                "area_cm2": "1",
                "aplicable": "on",
                "action": "save_and_calc",
            }
        )
        self.assertTrue(form.is_valid(), form.errors.as_json())

        result = run_for_instance(form.save())

        self.assertEqual(result.detalle["presion_kpa"], 160)
        self.assertEqual(result.detalle["base_por_matriz"], "bajo")
        self.assertEqual(result.nivel, "medio")
        self.assertIn("eleva un nivel", result.detalle["nota"])

    def test_contact_pressure_requires_force_and_positive_area(self):
        missing_area = EstresContactoForm(
            data={
                "risk_evaluation": self.risk_eval.pk,
                "fuerza_n": "10",
                "aplicable": "on",
            }
        )
        zero_area = EstresContactoForm(
            data={
                "risk_evaluation": self.risk_eval.pk,
                "fuerza_n": "10",
                "area_cm2": "0",
                "aplicable": "on",
            }
        )

        self.assertFalse(missing_area.is_valid())
        self.assertIn("area_cm2", missing_area.errors)
        self.assertFalse(zero_area.is_valid())
        self.assertIn("area_cm2", zero_area.errors)

    def test_anonymous_factor_access_redirects_to_login(self):
        self.client.logout()
        response = self.client.get(
            reverse(
                "evaluaciones:lmc_form_by_eval",
                kwargs={"evaluacion_id": self.risk_eval.pk},
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response.url.startswith(reverse(settings.LOGIN_URL)),
            response.url,
        )

    def test_invalid_form_log_does_not_include_submitted_values(self):
        secret_value = "MEDICION-SENSIBLE-NO-LOGUEAR"
        self.client.force_login(self.user)

        with patch("apps.ergonomia_886.evaluaciones.views.logger.warning") as warning:
            response = self.client.post(
                reverse(
                    "evaluaciones:lmc_form_by_eval",
                    kwargs={"evaluacion_id": self.risk_eval.pk},
                ),
                {
                    "risk_evaluation": self.risk_eval.pk,
                    "aplicable": "on",
                    "peso_kg": secret_value,
                    "action": "save_and_calc",
                },
            )

        self.assertEqual(response.status_code, 200)
        warning.assert_called_once()
        logged_call = repr(warning.call_args)
        self.assertNotIn(secret_value, logged_call)
        self.assertIn("error_codes", logged_call)
        self.assertIn("peso_kg", logged_call)

    def test_bipedestation_controls_round_trip(self):
        form = BipedestacionForm(
            data={
                "risk_evaluation": self.risk_eval.pk,
                "horas_de_pie_total": "4",
                "tiempo_continuo_min": "120",
                "movilidad_tipo": "estatica",
                "controles_existentes": ["alfombra", "rotacion"],
                "sintomas_json": "[]",
                "aplicable": "on",
            }
        )
        self.assertTrue(form.is_valid(), form.errors.as_json())
        evaluation = form.save()
        evaluation.refresh_from_db()

        self.assertEqual(
            evaluation.controles_existentes_json,
            ["alfombra", "rotacion"],
        )
        edit_form = BipedestacionForm(instance=evaluation)
        self.assertEqual(
            edit_form["controles_existentes"].value(),
            ["alfombra", "rotacion"],
        )

    def test_nam_requires_finite_coordinates_when_method_applies(self):
        form = RepetitivosMSForm(
            data={
                "risk_evaluation": self.risk_eval.pk,
                "monotarea": "on",
                "horas_dia": "4",
                "aplicable": "on",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("nam_x_valor", form.errors)
        self.assertIn("borg_y_valor", form.errors)

        instance = RepetitivosMS_Eval(
            risk_evaluation=self.risk_eval,
            monotarea=True,
            horas_dia=Decimal("4.00"),
            nam_x_valor=None,
            borg_y_valor=None,
        )
        result = run_for_instance(instance)
        self.assertEqual(result.nivel, "no_aplicable")
        self.assertIn("Faltan valores válidos", result.detalle["motivo"])

    def test_nam_aggravants_require_review_without_inventing_level_change(self):
        base = RepetitivosMS_Eval(
            risk_evaluation=self.risk_eval,
            monotarea=True,
            horas_dia=Decimal("4"),
            nam_x_valor=0,
            borg_y_valor=0,
        )
        aggravated = RepetitivosMS_Eval(
            risk_evaluation=self.risk_eval,
            monotarea=True,
            horas_dia=Decimal("4"),
            nam_x_valor=0,
            borg_y_valor=0,
            posturas_obligadas=True,
        )

        base_result = run_for_instance(base)
        aggravated_result = run_for_instance(aggravated)

        self.assertEqual(base_result.nivel, "bajo")
        self.assertEqual(aggravated_result.nivel, "bajo")
        self.assertFalse(base_result.detalle["requiere_revision_profesional"])
        self.assertTrue(
            aggravated_result.detalle["requiere_revision_profesional"]
        )
        self.assertFalse(
            aggravated_result.detalle["regla_agravantes"][
                "automatic_level_change"
            ]
        )
        self.assertIn(
            "juicio profesional",
            aggravated_result.detalle["recomendaciones"][0],
        )

    def test_planilla_2e_uses_official_six_second_threshold(self):
        verbose_name = Planilla2E._meta.get_field(
            "p2_esfuerzo_borg_mayor_3"
        ).verbose_name
        help_text = (
            settings.BASE_DIR
            / "static"
            / "ayuda"
            / "help_texts"
            / "planilla2e.md"
        ).read_text(encoding="utf-8")

        self.assertIn("más de 6 segundos", verbose_name)
        self.assertIn("más de 6 segundos", help_text)
        self.assertNotIn("más de 5 segundos", help_text)

        config = load_json("repetitivos_ms_limites.json")
        self.assertEqual(
            config["agravantes"]["rule"],
            "professional_review_required",
        )
        self.assertIn("295/2003", config["meta"]["normative_source"])

    def test_lmc_records_versioned_source_without_aggravants(self):
        instance = LMC_Eval(
            risk_evaluation=self.risk_eval,
            peso_kg=Decimal("20"),
            duracion_h=Decimal("1"),
            frecuencia_h=10,
            v_altura="nudillos_hombro",
            h_dist="proximo",
        )

        result = run_for_instance(instance)

        self.assertEqual(result.nivel, "bajo")
        self.assertEqual(result.detalle["limite_base_kg"], 32)
        self.assertEqual(result.detalle["limite_ajustado_kg"], 32)
        self.assertFalse(result.detalle["penalizaciones"]["aplicada"])
        self.assertEqual(
            result.detalle["fuente"]["data_version"],
            "1.2.0",
        )
        self.assertEqual(len(result.detalle["fuente"]["sha256"]), 64)
        self.assertIn(
            "295/2003",
            result.detalle["fuente"]["normative_source"],
        )

    def test_lmc_aggravants_keep_official_result_and_require_review(self):
        instance = LMC_Eval(
            risk_evaluation=self.risk_eval,
            peso_kg=Decimal("20"),
            duracion_h=Decimal("1"),
            frecuencia_h=10,
            v_altura="nudillos_hombro",
            h_dist="proximo",
            giro_mayor_30=True,
        )

        result = run_for_instance(instance)

        self.assertEqual(result.nivel, "bajo")
        self.assertEqual(result.detalle["limite_base_kg"], 32)
        self.assertIsNone(result.detalle["limite_ajustado_kg"])
        self.assertEqual(result.detalle["clasificacion_tabla"], "tolerable")
        self.assertTrue(result.detalle["requiere_revision_profesional"])
        self.assertFalse(
            result.detalle["penalizaciones"]["politica_habilitada"]
        )
        self.assertEqual(
            result.detalle["penalizaciones"]["estado_politica"],
            "approved_no_automatic_adjustment",
        )
        self.assertEqual(result.detalle["penalizaciones"]["factores"], [])
        self.assertEqual(
            result.detalle["agravantes_presentes"],
            ["Giro mayor de 30°"],
        )

    def test_lmc_uses_binary_official_limit_without_medium_band(self):
        instance = LMC_Eval(
            risk_evaluation=self.risk_eval,
            peso_kg=Decimal("33"),
            duracion_h=Decimal("1"),
            frecuencia_h=10,
            v_altura="nudillos_hombro",
            h_dist="proximo",
        )

        result = run_for_instance(instance)

        self.assertEqual(result.detalle["limite_base_kg"], 32)
        self.assertEqual(result.nivel, "alto")
        self.assertEqual(result.detalle["clasificacion_tabla"], "no_tolerable")

    def test_not_applicable_short_circuits_every_calculator(self):
        instance = LMC_Eval(
            risk_evaluation=self.risk_eval,
            aplicable=False,
            peso_kg=Decimal("50"),
            duracion_h=Decimal("8"),
            frecuencia_h=100,
        )

        result = run_for_instance(instance)

        self.assertEqual(result.nivel, "no_aplicable")
        self.assertIn("no aplicable", result.detalle["motivo"])
        trace = result.detalle["calculation_trace"]
        self.assertEqual(trace["engine_version"], "1.0.0")
        self.assertEqual(trace["factor_slug"], "lmc")
        self.assertEqual(trace["sources"][0]["archivo"], "lmc_tablas.json")
        self.assertEqual(len(trace["sources"][0]["sha256"]), 64)

    def test_simple_save_invalidates_previous_result(self):
        evaluation = LMC_Eval.objects.create(
            risk_evaluation=self.risk_eval,
            peso_kg=Decimal("20"),
            duracion_h=Decimal("2"),
            frecuencia_h=10,
            v_altura="nudillos_hombro",
            h_dist="proximo",
            nivel_riesgo="alto",
            calc_data={
                "estado_resultado": "calculado",
                "motivo_override": "resultado anterior",
                "input": {"dato_tecnico": 1},
            },
        )
        form = LMCForm(
            data={
                "risk_evaluation": self.risk_eval.pk,
                "peso_kg": "10",
                "duracion_h": "1",
                "frecuencia_h": "2",
                "v_altura": "nudillos_hombro",
                "h_dist": "proximo",
                "aplicable": "on",
            },
            instance=evaluation,
        )
        self.assertTrue(form.is_valid(), form.errors.as_json())

        saved = form.save()
        saved.refresh_from_db()

        self.assertEqual(saved.nivel_riesgo, "no_aplicable")
        self.assertEqual(saved.calc_data["estado_resultado"], "desactualizado")
        self.assertNotIn("motivo_override", saved.calc_data)
        self.assertEqual(saved.calc_data["input"], {"dato_tecnico": 1})

    def test_apply_result_replaces_obsolete_calculation_keys(self):
        evaluation = LMC_Eval.objects.create(
            risk_evaluation=self.risk_eval,
            calc_data={
                "estado_resultado": "calculado",
                "motivo_override": "ya no corresponde",
                "input": {"dato_tecnico": 1},
            },
        )

        apply_result(
            evaluation,
            CalcResult(nivel="bajo", detalle={"limite_kg": 25}),
        )
        evaluation.refresh_from_db()

        self.assertEqual(evaluation.nivel_riesgo, "bajo")
        self.assertEqual(evaluation.calc_data["estado_resultado"], "calculado")
        self.assertNotIn("motivo_override", evaluation.calc_data)
        self.assertEqual(evaluation.calc_data["limite_kg"], 25)
        self.assertEqual(evaluation.calc_data["input"], {"dato_tecnico": 1})
        trace = evaluation.calc_data["calculation_trace"]
        self.assertEqual(trace["engine_version"], "1.0.0")
        self.assertEqual(trace["factor_slug"], "lmc")
        self.assertRegex(trace["sources"][0]["sha256"], r"^[0-9a-f]{64}$")

    def test_wizard_distinguishes_draft_stale_and_calculated_states(self):
        LMC_Eval.objects.create(
            risk_evaluation=self.risk_eval,
            nivel_riesgo="no_aplicable",
            calc_data={"estado_resultado": "desactualizado"},
        )
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "evaluaciones:wizard_resumen_by_eval",
                kwargs={"evaluacion_id": self.risk_eval.pk},
            )
        )

        self.assertContains(response, "Levantamiento manual de cargas")
        self.assertContains(response, "Requiere recálculo")

    def test_starting_a_factor_marks_it_required_without_duplicates(self):
        self.client.force_login(self.user)
        url = reverse(
            "evaluaciones:start_factor",
            kwargs={
                "plan_eval_id": self.evaluacion.pk,
                "factor": "lmc",
            },
        )

        first = self.client.get(url)
        second = self.client.get(url)
        self.risk_eval.refresh_from_db()

        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(self.risk_eval.factores_requeridos, ["lmc"])
        self.assertEqual(self.risk_eval.estado, "in_progress")

    def test_wizard_global_result_requires_current_review_of_all_required(self):
        self.risk_eval.factores_requeridos = ["lmc", "transporte"]
        self.risk_eval.save(update_fields=["factores_requeridos"])
        lmc = LMC_Eval.objects.create(
            risk_evaluation=self.risk_eval,
            nivel_riesgo="bajo",
            calc_data={"estado_resultado": "calculado"},
        )
        transport = Transporte_Eval.objects.create(
            risk_evaluation=self.risk_eval,
            nivel_riesgo="alto",
            calc_data={"estado_resultado": "calculado"},
        )
        self.client.force_login(self.user)
        url = reverse(
            "evaluaciones:wizard_resumen_by_eval",
            kwargs={"evaluacion_id": self.risk_eval.pk},
        )

        initial = self.client.get(url)
        self.risk_eval.refresh_from_db()
        self.assertContains(initial, "Preliminar: Alto")
        self.assertContains(initial, "Pendientes de revisión profesional")
        self.assertNotContains(initial, "{#")
        self.assertIsNone(self.risk_eval.resultado_global)
        self.assertEqual(self.risk_eval.estado, "in_progress")

        first_review = self.client.post(
            url,
            {"action": "review_factor", "factor_slug": "lmc"},
        )
        self.assertEqual(first_review.status_code, 302)
        lmc.refresh_from_db()
        self.assertEqual(
            lmc.calc_data["revisado_por"]["username"],
            self.user.get_username(),
        )

        second_review = self.client.post(
            url,
            {"action": "review_factor", "factor_slug": "transporte"},
        )
        self.assertEqual(second_review.status_code, 302)
        transport.refresh_from_db()
        self.risk_eval.refresh_from_db()
        self.assertIn("revisado_en", transport.calc_data)
        self.assertEqual(self.risk_eval.resultado_global, "alto")
        self.assertEqual(self.risk_eval.estado, "done")
        self.assertTrue(self.risk_eval.resumen_json["all_reviewed"])

    def test_lmc_professional_review_can_override_with_justification(self):
        self.risk_eval.factores_requeridos = ["lmc"]
        self.risk_eval.save(update_fields=["factores_requeridos"])
        lmc = LMC_Eval.objects.create(
            risk_evaluation=self.risk_eval,
            peso_kg=Decimal("20"),
            duracion_h=Decimal("1"),
            frecuencia_h=10,
            v_altura="nudillos_hombro",
            h_dist="proximo",
            giro_mayor_30=True,
        )
        apply_result(lmc, run_for_instance(lmc))
        self.client.force_login(self.user)
        url = reverse(
            "evaluaciones:wizard_resumen_by_eval",
            kwargs={"evaluacion_id": self.risk_eval.pk},
        )

        missing_reason = self.client.post(
            url,
            {
                "action": "review_factor",
                "factor_slug": "lmc",
                "manual_level": "alto",
            },
        )
        self.assertEqual(missing_reason.status_code, 400)

        response = self.client.post(
            url,
            {
                "action": "review_factor",
                "factor_slug": "lmc",
                "manual_level": "alto",
                "review_justification": (
                    "El giro observado, combinado con la inestabilidad del ciclo, "
                    "justifica reclasificar el resultado."
                ),
            },
        )

        self.assertEqual(response.status_code, 302)
        lmc.refresh_from_db()
        self.risk_eval.refresh_from_db()
        review = lmc.calc_data["revision_profesional"]
        self.assertEqual(review["clasificacion_tabla"], "bajo")
        self.assertEqual(review["clasificacion_final"], "alto")
        self.assertTrue(review["modificada"])
        self.assertEqual(review["agravantes_considerados"], ["Giro mayor de 30°"])
        self.assertEqual(lmc.nivel_riesgo, "alto")
        self.assertEqual(self.risk_eval.resultado_global, "alto")

    def test_wizard_rejects_review_of_a_non_required_factor(self):
        lmc = LMC_Eval.objects.create(
            risk_evaluation=self.risk_eval,
            nivel_riesgo="bajo",
            calc_data={"estado_resultado": "calculado"},
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "evaluaciones:wizard_resumen_by_eval",
                kwargs={"evaluacion_id": self.risk_eval.pk},
            ),
            {"action": "review_factor", "factor_slug": "lmc"},
        )
        lmc.refresh_from_db()

        self.assertEqual(response.status_code, 409)
        self.assertNotIn("revisado_en", lmc.calc_data)
        self.assertNotIn("revisado_por", lmc.calc_data)

    def test_partial_lmc_can_be_saved_but_not_calculated(self):
        common = {
            "risk_evaluation": self.risk_eval.pk,
            "aplicable": "on",
        }
        draft_form = LMCForm(data={**common, "action": "save"})
        calculation_form = LMCForm(
            data={**common, "action": "save_and_calc"}
        )

        self.assertTrue(draft_form.is_valid(), draft_form.errors.as_json())
        self.assertFalse(calculation_form.is_valid())
        self.assertIn("peso_kg", calculation_form.errors)
        self.assertIn("duracion_h", calculation_form.errors)

    def test_incomplete_calculators_return_controlled_result(self):
        cases = [
            LMC_Eval(risk_evaluation=self.risk_eval),
            EmpujeInicial_Eval(risk_evaluation=self.risk_eval),
            Bipedestacion_Eval(risk_evaluation=self.risk_eval),
            ConfortTermico_Eval(risk_evaluation=self.risk_eval),
        ]

        for instance in cases:
            with self.subTest(model=type(instance).__name__):
                result = run_for_instance(instance)
                self.assertEqual(result.nivel, "no_aplicable")
                self.assertIn("motivo", result.detalle)

    def test_force_forms_validate_table_combinations_and_method_scope(self):
        form_classes = (
            EmpujeInicialForm,
            EmpujeSostenidaForm,
            TraccionInicialForm,
            TraccionSostenidaForm,
        )
        scope = {
            "alcance_una_persona": "on",
            "alcance_de_pie": "on",
            "alcance_ambas_manos": "on",
            "alcance_objeto_frente": "on",
        }
        common = {
            "risk_evaluation": self.risk_eval.pk,
            "poblacion": "f",
            "altura_agarre_cm": "95",
            "fuerza_n": "10",
            "aplicable": "on",
            "action": "save_and_calc",
            **scope,
        }

        for form_class in form_classes:
            with self.subTest(form=form_class.__name__, case="valid"):
                valid_form = form_class(
                    data={
                        **common,
                        "distancia_m": "2",
                        "frecuencia_opcion": "10_min",
                    }
                )
                self.assertTrue(valid_form.is_valid(), valid_form.errors.as_json())

            with self.subTest(form=form_class.__name__, case="invalid-table-row"):
                invalid_combination = form_class(
                    data={
                        **common,
                        "distancia_m": "60",
                        "frecuencia_opcion": "10_min",
                    }
                )
                self.assertFalse(invalid_combination.is_valid())
                self.assertIn("frecuencia_opcion", invalid_combination.errors)

            with self.subTest(form=form_class.__name__, case="missing-scope"):
                missing_scope = form_class(
                    data={
                        key: value
                        for key, value in {
                            **common,
                            "distancia_m": "2",
                            "frecuencia_opcion": "10_min",
                        }.items()
                        if key not in scope
                    }
                )
                self.assertFalse(missing_scope.is_valid())
                for field in scope:
                    self.assertIn(field, missing_scope.errors)

    def test_force_scope_round_trip_and_engine_guard(self):
        scope = {
            "alcance_una_persona": "on",
            "alcance_de_pie": "on",
            "alcance_ambas_manos": "on",
            "alcance_objeto_frente": "on",
        }
        form = EmpujeInicialForm(
            data={
                "risk_evaluation": self.risk_eval.pk,
                "poblacion": "f",
                "altura_agarre_cm": "95",
                "distancia_m": "2",
                "frecuencia_opcion": "10_min",
                "fuerza_n": "10",
                "aplicable": "on",
                "action": "save",
                **scope,
            }
        )
        self.assertTrue(form.is_valid(), form.errors.as_json())
        evaluation = form.save()
        evaluation.refresh_from_db()

        stored_scope = evaluation.calc_data["input"]["alcance_metodo"]
        self.assertTrue(all(stored_scope.values()))
        edit_form = EmpujeInicialForm(instance=evaluation)
        for field in scope:
            self.assertTrue(edit_form[field].value())

        without_scope = EmpujeInicial_Eval(
            risk_evaluation=self.risk_eval,
            poblacion="f",
            altura_agarre_cm=95,
            distancia_m=2,
            frecuencia_opcion="10_min",
            fuerza_n=Decimal("10"),
        )
        rejected = run_for_instance(without_scope)
        self.assertEqual(rejected.nivel, "no_aplicable")
        self.assertIn("alcance", rejected.detalle["motivo"])

        without_scope.calc_data = {
            "input": {
                "alcance_metodo": {
                    key: True for key in EmpujeInicialForm.SCOPE_FIELDS
                }
            }
        }
        accepted = run_for_instance(without_scope)
        self.assertEqual(accepted.nivel, "bajo")
        self.assertTrue(all(accepted.detalle["alcance_metodo"].values()))

    def test_transport_uses_only_official_distances_without_extrapolation(self):
        self.assertEqual(_lookup_limite_transporte(1), 10000)
        self.assertEqual(_lookup_limite_transporte(1.1), 10000)
        self.assertEqual(_lookup_limite_transporte(4), 10000)
        self.assertEqual(_lookup_limite_transporte(10), 10000)
        self.assertEqual(_lookup_limite_transporte(10.1), 6000)
        self.assertEqual(_lookup_limite_transporte(20), 6000)
        self.assertIsNone(_lookup_limite_transporte(20.1))

        incomplete = Transporte_Eval(
            risk_evaluation=self.risk_eval,
            masa_kg=Decimal("10"),
            distancia_m=Decimal("100"),
            frecuencia_max_minuto=1,
            frecuencia_max_hora=2,
            frecuencia_jornada=10,
        )
        result = run_for_instance(incomplete)
        self.assertEqual(result.nivel, "no_aplicable")
        self.assertIn("Sección 2", result.detalle["motivo"])

    def test_transport_checks_short_medium_and_long_term_accumulation(self):
        common = {
            "risk_evaluation": self.risk_eval,
            "masa_kg": Decimal("15"),
            "distancia_m": Decimal("20"),
            "en_plano_horizontal": True,
            "jornada_8h": True,
            "velocidad_05a1_ms": True,
            "superficie_plana": True,
        }

        at_all_limits = run_for_instance(
            Transporte_Eval(
                **common,
                frecuencia_max_minuto=1,
                frecuencia_max_hora=50,
                frecuencia_jornada=400,
            )
        )
        self.assertEqual(at_all_limits.nivel, "bajo")
        self.assertEqual(at_all_limits.detalle["masa_acumulada_kg_minuto"], 15)
        self.assertEqual(at_all_limits.detalle["masa_acumulada_kg_hora"], 750)
        self.assertEqual(at_all_limits.detalle["masa_acumulada_kg_jornada"], 6000)

        cases = (
            (2, 50, 400, "masa_max_kg_min"),
            (1, 51, 400, "masa_max_kg_h"),
            (1, 50, 401, "masa_max_kg_jornada"),
        )
        for f_min, f_h, f_day, failed_check in cases:
            with self.subTest(failed_check=failed_check):
                result = run_for_instance(
                    Transporte_Eval(
                        **common,
                        frecuencia_max_minuto=f_min,
                        frecuencia_max_hora=f_h,
                        frecuencia_jornada=f_day,
                    )
                )
                self.assertEqual(result.nivel, "alto")
                self.assertFalse(result.detalle["verificaciones_tabla"][failed_check])

    def test_traction_initial_flags_the_single_internally_corrected_cell(self):
        scope = {
            "alcance_una_persona": True,
            "alcance_de_pie": True,
            "alcance_ambas_manos": True,
            "alcance_objeto_frente": True,
        }
        evaluation = TraccionInicial_Eval(
            risk_evaluation=self.risk_eval,
            poblacion="f",
            altura_agarre_cm=144,
            distancia_m=60,
            frecuencia_opcion="1_cada_8_h",
            fuerza_n=Decimal("100"),
            calc_data={"input": {"alcance_metodo": scope}},
        )

        result = run_for_instance(evaluation)

        self.assertEqual(result.nivel, "bajo")
        self.assertEqual(result.detalle["limite_N"], 140)
        self.assertTrue(result.detalle["requiere_revision_profesional"])
        self.assertIn("1460 N", result.detalle["advertencia_fuente"])
        self.assertEqual(result.detalle["fuente"]["data_version"], "1.1.0")

    def test_reba_rejects_incompatible_posture_and_derived_fields(self):
        data = {
            "risk_evaluation": self.risk_eval.pk,
            "cuello_base": "1",
            "piernas_base": "1",
            "piernas_flex_30_60": "on",
            "piernas_flex_mas_60": "on",
            "tronco_base": "1",
            "carga_categoria": "0",
            "brazo_base": "1",
            "antebrazo_base": "1",
            "muneca_base": "1",
            "agarre": "0",
            "puntaje_final": "15",
            "aplicable": "on",
        }
        form = PosturasForzadasForm(data=data)

        self.assertNotIn("puntaje_final", form.fields)
        self.assertFalse(form.is_valid())
        self.assertIn("no pueden seleccionarse juntas", form.non_field_errors()[0])

    def test_reba_table_failure_never_falls_back_to_minimum_score(self):
        instance = PosturasForzadas_Eval(
            risk_evaluation=self.risk_eval,
            calc_data={
                "input": {
                    "cuello_base": 1,
                    "piernas_base": 1,
                    "tronco_base": 1,
                    "carga_categoria": 0,
                    "brazo_base": 1,
                    "antebrazo_base": 1,
                    "muneca_base": 1,
                    "agarre": 0,
                }
            },
        )

        with patch(
            "apps.ergonomia_886.evaluaciones.calculators._reba_lookup_tabla_a",
            side_effect=KeyError("tabla corrupta"),
        ):
            result = calc_posturas_forzadas(instance)

        self.assertEqual(result.nivel, "no_aplicable")
        self.assertIn("Tabla A", result.detalle["motivo"])

    def test_negative_vibration_values_are_rejected_by_forms(self):
        vmb_form = VibracionMBForm(
            data={
                "risk_evaluation": self.risk_eval.pk,
                "tipo_exposicion": "simple",
                "duracion_h": "8",
                "ax_mps2": "-1",
                "ay_mps2": "0",
                "az_mps2": "0",
                "aplicable": "on",
            }
        )
        segment_form = VCESegmentForm(
            data={
                "vehiculo_maquina": "Autoelevador",
                "tipo_asiento": "mecanica",
                "superficie_terreno": "liso",
                "estado_neumaticos": "correcto",
                "tiempo_horas": "8",
                "aw_x": "-0.2",
                "aw_y": "0.1",
                "aw_z": "0.3",
            }
        )

        self.assertFalse(vmb_form.is_valid())
        self.assertFalse(segment_form.is_valid())
        self.assertIn("aw_x", segment_form.errors)

    def test_zero_scalar_vibration_is_a_valid_measurement(self):
        instance = VibracionMB_Eval(
            risk_evaluation=self.risk_eval,
            tipo_exposicion="multiple",
            exposiciones_json=[{"awi_mps2": 0, "Ti_h": 8}],
        )

        result = calc_vibracion_mano_brazo(instance)

        self.assertEqual(result.nivel, "bajo")
        self.assertEqual(result.detalle["valor_exposicion_mps2"], 0)

    def test_advanced_input_json_is_not_exposed_in_public_forms(self):
        for form_class in (
            LMCForm,
            BipedestacionForm,
            RepetitivosMSForm,
            VibracionCEForm,
        ):
            with self.subTest(form=form_class.__name__):
                self.assertNotIn("input_json", form_class().fields)

    def test_vce_spectral_contract_is_validated_and_used(self):
        spectrum = {
            "pico_x_hz": 2,
            "pico_x_mps2": 0.25,
            "pico_y_hz": 2,
            "pico_y_mps2": 0.20,
            "pico_z_hz": 5,
            "pico_z_mps2": 0.35,
        }
        valid_form = VibracionCEForm(
            data={
                "risk_evaluation": self.risk_eval.pk,
                "metodo": "espectral",
                "espectro_json": spectrum,
                "duracion_h": "8",
                "postura": "sentado",
                "ubicacion_sensor": "isquiones",
                "aplicable": "on",
            }
        )
        invalid_form = VibracionCEForm(
            data={
                "risk_evaluation": self.risk_eval.pk,
                "metodo": "espectral",
                "espectro_json": {"pico_x_hz": 2},
                "duracion_h": "8",
                "postura": "sentado",
                "ubicacion_sensor": "isquiones",
                "aplicable": "on",
            }
        )

        self.assertTrue(valid_form.is_valid(), valid_form.errors.as_json())
        self.assertFalse(invalid_form.is_valid())
        self.assertIn("espectro_json", invalid_form.errors)

        evaluation = valid_form.save()
        result = calc_vibracion_cuerpo_entero(evaluation)
        self.assertEqual(result.nivel, "bajo")
        self.assertEqual(
            result.detalle["calc_details"]["picos"]["z"],
            {"hz": 5.0, "mps2": 0.35},
        )

    def test_vce_crest_factor_warns_only_above_six(self):
        def calculate(crest_factor):
            evaluation = VibracionCE_Eval.objects.create(
                risk_evaluation=self.risk_eval,
                postura="sentado",
                ubicacion_sensor="isquiones",
            )
            VCESegment.objects.create(
                evaluation=evaluation,
                vehiculo_maquina=f"Equipo CF {crest_factor}",
                tipo_asiento="mecanica",
                superficie_terreno="liso",
                estado_neumaticos="correcto",
                tiempo_horas=Decimal("8"),
                aw_x=Decimal("0.2"),
                aw_y=Decimal("0.1"),
                aw_z=Decimal("0.6"),
                cf_z=Decimal(str(crest_factor)),
            )
            return calc_vibracion_cuerpo_entero(evaluation)

        at_threshold = calculate("6.00")
        above_threshold = calculate("6.01")

        self.assertEqual(at_threshold.nivel, above_threshold.nivel)
        self.assertFalse(
            at_threshold.detalle["calc_details"]["crest_factor_mayor_6"]
        )
        self.assertEqual(
            at_threshold.detalle["calc_details"]["warnings"],
            [],
        )
        self.assertTrue(
            above_threshold.detalle["calc_details"]["crest_factor_mayor_6"]
        )
        self.assertIn(
            "Factor de cresta > 6.0",
            above_threshold.detalle["calc_details"]["warnings"][0],
        )

    def test_bipedestation_duration_intervals_are_semi_open(self):
        bins = [
            {"id": "lt_2h", "min_min": 0, "max_min": 120},
            {"id": "2a4h", "min_min": 120, "max_min": 240},
            {"id": "ge_4h", "min_min": 240, "max_min": None},
        ]

        self.assertEqual(_cat_por_duracion(119, bins)["id"], "lt_2h")
        self.assertEqual(_cat_por_duracion(120, bins)["id"], "2a4h")
        self.assertEqual(_cat_por_duracion(240, bins)["id"], "ge_4h")
        self.assertEqual(_cat_por_duracion(241, bins)["id"], "ge_4h")

    def test_bipedestation_walk_reduction_starts_above_100_mph(self):
        def calculate(metres_per_hour):
            instance = Bipedestacion_Eval(
                risk_evaluation=self.risk_eval,
                horas_de_pie_total=Decimal("3"),
                tiempo_continuo_min=120,
                movilidad_tipo="deambulacion",
                movilidad_m_por_h=metres_per_hour,
            )
            return calc_bipedestacion(instance)

        at_99 = calculate(99)
        at_100 = calculate(100)
        at_101 = calculate(101)

        self.assertEqual(
            at_99.detalle["duracion"]["continuo_min_efectivo"],
            120,
        )
        self.assertEqual(
            at_100.detalle["duracion"]["continuo_min_efectivo"],
            120,
        )
        self.assertEqual(
            at_101.detalle["duracion"]["continuo_min_efectivo"],
            84,
        )

    def test_factor_templates_compile_and_render_child_result_blocks(self):
        template_names = [
            "evaluaciones/empuje_inicial_form.html",
            "evaluaciones/empuje_sostenida_form.html",
            "evaluaciones/traccion_inicial_form.html",
            "evaluaciones/traccion_sostenida_form.html",
            "evaluaciones/transporte_form.html",
            "evaluaciones/estres_contacto_form.html",
            "evaluaciones/vibracion_mano_brazo_form.html",
        ]
        for template_name in template_names:
            with self.subTest(template=template_name):
                get_template(template_name)

        evaluation = Transporte_Eval(
            risk_evaluation=self.risk_eval,
            nivel_riesgo="bajo",
            calc_data={
                "masa_acumulada_kg_jornada": 100,
                "limite_kg_jornada": 1500,
                "distancia_tabla_m": 20,
                "frecuencia_max_minuto_observada": 1,
                "frecuencia_max_hora_observada": 4,
                "masa_acumulada_kg_minuto": 10,
                "masa_max_kg_min": 15,
                "masa_acumulada_kg_hora": 40,
                "masa_max_kg_h": 750,
                "criterio": "Cumple el límite.",
            },
        )
        html = render_to_string(
            "evaluaciones/transporte_form.html",
            {
                "form": TransporteForm(instance=evaluation),
                "object": evaluation,
            },
        )
        self.assertIn("Masa acumulada", html)
        self.assertIn("100 kg/jornada", html)

        force_html = render_to_string(
            "evaluaciones/empuje_inicial_form.html",
            {"form": EmpujeInicialForm()},
        )
        self.assertIn("Condiciones de alcance del método", force_html)
        self.assertIn("data-valid-by-distance", force_html)

        repetitive_html = render_to_string(
            "evaluaciones/repetitivos_ms_form.html",
            {"form": RepetitivosMSForm()},
        )
        self.assertIn(
            "Movimientos Repetitivos de Miembros Superiores (NAM)",
            repetitive_html,
        )
        self.assertNotIn(
            '<h1 class="h3 mb-0">Evaluación de factor</h1>',
            repetitive_html,
        )

    def test_confort_requires_both_measurements_only_when_calculating(self):
        common = {
            "risk_evaluation": self.risk_eval.pk,
            "temperatura_operativa_c": "24",
            "aplicable": "on",
        }
        draft_form = ConfortTermicoForm(data={**common, "action": "save"})
        calculation_form = ConfortTermicoForm(
            data={**common, "action": "save_and_calc"}
        )

        self.assertTrue(draft_form.is_valid(), draft_form.errors.as_json())
        self.assertFalse(calculation_form.is_valid())
        self.assertIn("humedad_relativa_pct", calculation_form.errors)

    def test_wizard_generates_an_authorized_pdf(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse(
                "evaluaciones:wizard_resumen_by_eval",
                kwargs={"evaluacion_id": self.risk_eval.pk},
            ),
            {"action": "generate_pdf"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn(
            f'evaluacion-{self.risk_eval.pk}-resumen.pdf',
            response["Content-Disposition"],
        )
        self.assertGreater(len(response.content), 1000)
        self.assertTrue(response.content.startswith(b"%PDF-"))
        self.assertIn(b"%%EOF", response.content[-1024:])
