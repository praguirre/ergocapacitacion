"""Sugerencias de capacitación que consumen niveles persistidos (CF-2)."""

from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.ergonomia_886.planillas.models import Evaluacion
from apps.training.models import TrainingModule

from .models import LMC_Eval, RiskEvaluation, Transporte_Eval
from .sugerencias import sugerencias_para_factores


class SugerenciasCapacitacionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.profesional = get_user_model().objects.create_professional(
            email="sugerencias-prof@test.local",
            username="sugerencias-prof",
            password="prueba",
        )
        cls.evaluacion = Evaluacion.objects.create(
            usuario=cls.profesional,
            razon_social="ACME",
            cuit="30-12345678-9",
            direccion_establecimiento="Ruta 8",
            provincia="Buenos Aires",
        )
        cls.risk = RiskEvaluation.objects.create(
            evaluacion=cls.evaluacion,
            factores_requeridos=["lmc", "transporte"],
        )
        cls.modulo = TrainingModule.objects.create(
            slug="ergonomia",
            title="Ergonomía",
            youtube_id="video-prueba",
            is_active=True,
        )

    def _factor(self, slug, label, nivel):
        return {"slug": slug, "label": label, "nivel": nivel}

    def test_la_sugerencia_aparece_solo_con_nivel_medio_o_alto(self):
        bajo = sugerencias_para_factores([
            self._factor("lmc", "Levantamiento manual", "bajo")
        ])
        medio = sugerencias_para_factores([
            self._factor("lmc", "Levantamiento manual", "medio")
        ])
        alto = sugerencias_para_factores([
            self._factor("lmc", "Levantamiento manual", "alto")
        ])
        self.assertEqual(bajo, [])
        self.assertEqual(len(medio), 1)
        self.assertEqual(len(alto), 1)

    def test_el_enlace_apunta_a_un_modulo_existente_y_activo(self):
        sugerencia = sugerencias_para_factores([
            self._factor("lmc", "Levantamiento manual", "alto")
        ])[0]
        self.assertEqual(sugerencia["module"], self.modulo)
        self.assertTrue(sugerencia["module"].is_active)
        self.assertEqual(
            sugerencia["url"],
            reverse("training_public:training_public", args=["ergonomia"]),
        )

    def test_cf2_el_wizard_no_recalcula_ni_modifica_niveles(self):
        lmc = LMC_Eval.objects.create(
            risk_evaluation=self.risk,
            nivel_riesgo="alto",
            calc_data={"estado_resultado": "calculado"},
        )
        transporte = Transporte_Eval.objects.create(
            risk_evaluation=self.risk,
            nivel_riesgo="bajo",
            calc_data={"estado_resultado": "calculado"},
        )
        self.client.force_login(self.profesional)
        with patch(
            "apps.ergonomia_886.evaluaciones.calculators.run_for_instance"
        ) as calcular:
            respuesta = self.client.get(
                reverse("evaluaciones:wizard_resumen_by_eval", args=[self.risk.pk])
            )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Capacitación sugerida")
        self.assertContains(respuesta, "Abrir capacitación")
        calcular.assert_not_called()
        lmc.refresh_from_db()
        transporte.refresh_from_db()
        self.assertEqual(lmc.nivel_riesgo, "alto")
        self.assertEqual(transporte.nivel_riesgo, "bajo")

    def test_apps_training_no_importa_el_modulo_886(self):
        training_dir = Path(settings.BASE_DIR) / "apps" / "training"
        fuentes = "\n".join(
            path.read_text(encoding="utf-8")
            for path in training_dir.rglob("*.py")
            if "migrations" not in path.parts and not path.name.startswith("test")
        )
        self.assertNotIn("apps.ergonomia_886", fuentes)
