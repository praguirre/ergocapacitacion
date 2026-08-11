"""Vincula cada intento online con el link que determinó su responsable."""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("quiz", "0001_initial"),
        ("training", "0004_add_link_share_log"),
    ]

    operations = [
        migrations.AddField(
            model_name="quizattempt",
            name="capacitacion_link",
            field=models.ForeignKey(
                blank=True,
                help_text="Link validado al iniciar el intento online.",
                null=True,
                on_delete=models.SET_NULL,
                related_name="quiz_attempts",
                to="training.capacitacionlink",
                verbose_name="Link de origen",
            ),
        ),
    ]
