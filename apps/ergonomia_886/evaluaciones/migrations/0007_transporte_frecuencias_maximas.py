from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("evaluaciones", "0006_vibracionce_eval_calc_details_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="transporte_eval",
            name="frecuencia_max_hora",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Máximo de traslados observado en cualquier hora",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="transporte_eval",
            name="frecuencia_max_minuto",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Máximo de traslados observado en cualquier minuto",
                null=True,
            ),
        ),
    ]
