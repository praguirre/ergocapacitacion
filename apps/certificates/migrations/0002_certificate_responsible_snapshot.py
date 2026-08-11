"""Agrega responsable trazable y snapshot inmutable a nuevas emisiones."""

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("certificates", "0001_initial"),
        ("quiz", "0002_quizattempt_capacitacion_link"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="certificate",
            name="responsible_license_number",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AddField(
            model_name="certificate",
            name="responsible_name",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AddField(
            model_name="certificate",
            name="responsible_profession",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="certificate",
            name="responsible_professional",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="issued_training_certificates",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Profesional responsable",
            ),
        ),
    ]
