from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.utils import timezone


User = get_user_model()

ATTRIBUTION_FILTER = (
    Q(attribution_campaign__gt="")
    | Q(attribution_content__gt="")
    | Q(attribution_source__gt="")
)


def _percentage(value, total):
    return (value * 100 / total) if total else 0.0


def _display_value(value, empty_label):
    return value or empty_label


class Command(BaseCommand):
    help = "Resume la atribución first-touch de registros profesionales"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dias",
            type=int,
            default=30,
            help="Ventana sobre date_joined en días (default: 30).",
        )
        parser.add_argument(
            "--campana",
            type=str,
            default=None,
            help=(
                "Acota todo el universo a attribution_campaign; por eso "
                "'sin atribución' normalmente será 0 en este modo."
            ),
        )
        parser.add_argument(
            "--detalle",
            action="store_true",
            help="Lista fecha, profesión y utm_content sin datos personales.",
        )

    def handle(self, *args, **options):
        dias = options["dias"]
        campana = options["campana"]
        desde = timezone.now() - timedelta(days=dias)

        profesionales = User.objects.filter(
            user_type="professional",
            date_joined__gte=desde,
        )
        if campana is not None:
            profesionales = profesionales.filter(attribution_campaign=campana)

        atribuidos = profesionales.filter(ATTRIBUTION_FILTER)
        total = profesionales.count()
        con_atribucion = atribuidos.count()
        sin_atribucion = total - con_atribucion

        self._write_summary(
            dias=dias,
            total=total,
            con_atribucion=con_atribucion,
            sin_atribucion=sin_atribucion,
        )
        self._write_campaigns(atribuidos)
        self._write_sources(atribuidos)
        self._write_contents(atribuidos)

        if options["detalle"]:
            self._write_details(atribuidos)

    def _write_summary(self, *, dias, total, con_atribucion, sin_atribucion):
        title = f"ATRIBUCIÓN DE REGISTROS PROFESIONALES — últimos {dias} días"
        self.stdout.write(title)
        self.stdout.write("═" * len(title))
        self.stdout.write("")
        self.stdout.write(f"{'Total de registros profesionales:':<39}{total:>6}")
        self.stdout.write(
            f"{'Con atribución:':<39}{con_atribucion:>6}  "
            f"({_percentage(con_atribucion, total):.1f} %)"
        )
        self.stdout.write(
            f"{'Sin atribución (directo/desconocido):':<39}{sin_atribucion:>6}  "
            f"({_percentage(sin_atribucion, total):.1f} %)"
        )

    def _write_campaigns(self, atribuidos):
        rows = list(
            atribuidos.exclude(attribution_campaign="")
            .values("attribution_campaign")
            .annotate(registros=Count("id"))
            .order_by("-registros", "attribution_campaign")
        )
        labels = [row["attribution_campaign"] for row in rows]
        width = max([len("campaña"), *(len(label) for label in labels)])

        self.stdout.write("\nPOR CAMPAÑA")
        self.stdout.write(f"  {'campaña':<{width}}  registros")
        self.stdout.write(f"  {'─' * width}  {'─' * len('registros')}")
        for row in rows:
            self.stdout.write(
                f"  {row['attribution_campaign']:<{width}}  {row['registros']:>9}"
            )

    def _write_sources(self, atribuidos):
        rows = list(
            atribuidos.values("attribution_source", "attribution_medium")
            .annotate(registros=Count("id"))
            .order_by("-registros", "attribution_source", "attribution_medium")
        )
        display_rows = [
            (
                _display_value(row["attribution_source"], "(sin origen)"),
                _display_value(row["attribution_medium"], "(sin medio)"),
                row["registros"],
            )
            for row in rows
        ]
        source_width = max(
            [len("origen"), *(len(source) for source, _, _ in display_rows)]
        )
        medium_width = max(
            [len("medio"), *(len(medium) for _, medium, _ in display_rows)]
        )

        self.stdout.write("\nPOR ORIGEN Y MEDIO")
        self.stdout.write(
            f"  {'origen':<{source_width}}  {'medio':<{medium_width}}  registros"
        )
        self.stdout.write(
            f"  {'─' * source_width}  {'─' * medium_width}  {'─' * len('registros')}"
        )
        for source, medium, count in display_rows:
            self.stdout.write(
                f"  {source:<{source_width}}  {medium:<{medium_width}}  {count:>9}"
            )

    def _write_contents(self, atribuidos):
        rows = list(
            atribuidos.exclude(attribution_content="")
            .values("attribution_content")
            .annotate(registros=Count("id"))
            .order_by("-registros", "attribution_content")
        )
        labels = [row["attribution_content"] for row in rows]
        width = max([len("borrador"), *(len(label) for label in labels)])

        self.stdout.write("\nTOP BORRADORES  (utm_content)")
        self.stdout.write(f"  {'borrador':<{width}}  registros")
        self.stdout.write(f"  {'─' * width}  {'─' * len('registros')}")
        for row in rows:
            self.stdout.write(
                f"  {row['attribution_content']:<{width}}  {row['registros']:>9}"
            )

    def _write_details(self, atribuidos):
        rows = list(
            atribuidos.order_by("-date_joined").values(
                "date_joined",
                "profession",
                "attribution_content",
            )
        )
        display_rows = [
            (
                timezone.localtime(row["date_joined"]).strftime("%Y-%m-%d"),
                _display_value(row["profession"], "(sin profesión)"),
                _display_value(row["attribution_content"], "(sin contenido)"),
            )
            for row in rows
        ]
        date_width = max(
            [len("fecha"), *(len(joined) for joined, _, _ in display_rows)]
        )
        profession_width = max(
            [len("profesión"), *(len(profession) for _, profession, _ in display_rows)]
        )
        content_width = max(
            [len("borrador"), *(len(content) for _, _, content in display_rows)]
        )

        self.stdout.write("\nDETALLE DE REGISTROS ATRIBUIDOS")
        self.stdout.write(
            f"  {'fecha':<{date_width}}  {'profesión':<{profession_width}}  "
            f"{'borrador':<{content_width}}"
        )
        self.stdout.write(
            f"  {'─' * date_width}  {'─' * profession_width}  {'─' * content_width}"
        )
        for joined, profession, content in display_rows:
            self.stdout.write(
                f"  {joined:<{date_width}}  {profession:<{profession_width}}  "
                f"{content:<{content_width}}"
            )
