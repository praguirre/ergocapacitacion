import io
import re
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone


User = get_user_model()


class AttributionCommandTests(TestCase):
    def run_command(self, **options):
        output = io.StringIO()
        call_command("atribucion", stdout=output, **options)
        return output.getvalue()

    @staticmethod
    def create_professional(index, **extra_fields):
        defaults = {
            "first_name": f"NombrePrivado{index}",
            "last_name": f"ApellidoPrivado{index}",
            "dni": str(30000000 + index),
            "profession": "Lic. en Higiene y Seguridad",
            "date_joined": timezone.now(),
        }
        defaults.update(extra_fields)
        return User.objects.create_professional(
            email=f"privado{index}@example.test",
            password="clave-segura-123",
            username=f"privado{index}",
            **defaults,
        )

    def test_empty_and_unattributed_bases_exit_with_zero_counts(self):
        empty_output = self.run_command(dias=30)

        self.assertRegex(empty_output, r"Total de registros profesionales:\s+0")
        self.assertRegex(empty_output, r"Con atribución:\s+0\s+\(0\.0 %\)")
        self.assertIn("POR CAMPAÑA", empty_output)
        self.assertIn("POR ORIGEN Y MEDIO", empty_output)
        self.assertIn("TOP BORRADORES", empty_output)

        self.create_professional(1)
        direct_output = self.run_command(dias=30)

        self.assertRegex(direct_output, r"Total de registros profesionales:\s+1")
        self.assertRegex(direct_output, r"Con atribución:\s+0\s+\(0\.0 %\)")
        self.assertRegex(
            direct_output,
            r"Sin atribución \(directo/desconocido\):\s+1\s+\(100\.0 %\)",
        )

    def test_campaign_origin_and_content_counts_are_correct(self):
        for index, content in enumerate(
            ["d_a3f9c2b1", "d_a3f9c2b1", "d_otro"],
            start=1,
        ):
            self.create_professional(
                index,
                attribution_campaign="ergoreach",
                attribution_source="x",
                attribution_medium="reply",
                attribution_content=content,
            )
        self.create_professional(
            4,
            attribution_campaign="youtube",
            attribution_source="youtube",
            attribution_medium="video",
            attribution_content="d_video",
        )

        output = self.run_command(dias=30)

        self.assertRegex(output, r"Total de registros profesionales:\s+4")
        self.assertRegex(output, r"Con atribución:\s+4\s+\(100\.0 %\)")
        self.assertRegex(output, r"ergoreach\s+3")
        self.assertRegex(output, r"youtube\s+1")
        self.assertRegex(output, r"x\s+reply\s+3")
        self.assertRegex(output, r"d_a3f9c2b1\s+2")

    def test_campaign_filter_scopes_the_entire_universe(self):
        self.create_professional(
            1,
            attribution_campaign="ergoreach",
            attribution_source="x",
        )
        self.create_professional(
            2,
            attribution_campaign="ergoreach",
            attribution_source="linkedin",
        )
        self.create_professional(
            3,
            attribution_campaign="youtube",
            attribution_source="youtube",
        )
        self.create_professional(4)

        output = self.run_command(dias=30, campana="ergoreach")

        self.assertRegex(output, r"Total de registros profesionales:\s+2")
        self.assertRegex(output, r"Con atribución:\s+2\s+\(100\.0 %\)")
        self.assertRegex(
            output,
            r"Sin atribución \(directo/desconocido\):\s+0\s+\(0\.0 %\)",
        )
        self.assertNotIn("youtube", output)

    def test_days_excludes_old_professionals(self):
        self.create_professional(
            1,
            attribution_source="x",
            attribution_content="d_reciente",
        )
        self.create_professional(
            2,
            date_joined=timezone.now() - timedelta(days=31),
            attribution_source="x",
            attribution_content="d_antiguo",
        )

        output = self.run_command(dias=30)

        self.assertRegex(output, r"Total de registros profesionales:\s+1")
        self.assertIn("d_reciente", output)
        self.assertNotIn("d_antiguo", output)

    def test_detail_never_prints_personal_identifiers(self):
        user = self.create_professional(
            1,
            attribution_campaign="ergoreach",
            attribution_source="x",
            attribution_medium="reply",
            attribution_content="d_privacidad",
        )

        output = self.run_command(dias=30, detalle=True)

        self.assertIn("DETALLE DE REGISTROS ATRIBUIDOS", output)
        self.assertIn(user.profession, output)
        self.assertIn("d_privacidad", output)
        self.assertNotIn("@", output)
        self.assertNotIn(user.email, output)
        self.assertNotIn(user.dni, output)
        self.assertNotIn(user.username, output)
        self.assertNotIn(user.first_name, output)
        self.assertNotIn(user.last_name, output)
        self.assertNotRegex(output, re.compile(r"\b\d{7,11}\b"))

    def test_trainees_are_never_counted(self):
        User.objects.create_trainee(
            cuil="20123456789",
            email="trainee-command@example.test",
            full_name="Trainee Privado",
            attribution_campaign="ergoreach",
            attribution_source="x",
            attribution_content="d_trainee",
        )

        output = self.run_command(dias=30)

        self.assertRegex(output, r"Total de registros profesionales:\s+0")
        self.assertNotIn("ergoreach", output)
        self.assertNotIn("d_trainee", output)
