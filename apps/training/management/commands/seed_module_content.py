from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.training.models import TrainingModule


CONTENT_FILES = {
    "intro_md": "intro.md",
    "material_md": "material.md",
    "transcript_md": "transcript.txt",
}


class Command(BaseCommand):
    help = "Carga contenido canónico (intro/material/transcript) en un TrainingModule."

    def add_arguments(self, parser):
        parser.add_argument(
            "--module",
            default="ergonomia",
            help="Slug del módulo a actualizar (default: ergonomia)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Si está presente, pisa contenido existente.",
        )

    def handle(self, *args, **options):
        module_slug = options["module"]
        force = options["force"]

        module = TrainingModule.objects.filter(slug=module_slug).first()
        if not module:
            raise CommandError(f"No existe TrainingModule con slug='{module_slug}'.")

        training_dir = Path(__file__).resolve().parents[2]
        content_dir = training_dir / "content" / module_slug

        canonical_values = {}
        for field_name, file_name in CONTENT_FILES.items():
            path = content_dir / file_name
            if not path.exists():
                raise CommandError(f"No existe archivo canónico requerido: {path}")
            canonical_values[field_name] = path.read_text(encoding="utf-8")

        updated_fields = []
        omitted_fields = []

        for field_name, canonical_text in canonical_values.items():
            current_value = getattr(module, field_name, "") or ""

            if force:
                if current_value != canonical_text:
                    setattr(module, field_name, canonical_text)
                    updated_fields.append(field_name)
                else:
                    omitted_fields.append(field_name)
                continue

            if current_value.strip():
                omitted_fields.append(field_name)
                continue

            setattr(module, field_name, canonical_text)
            updated_fields.append(field_name)

        if updated_fields:
            module.save(update_fields=updated_fields + ["updated_at"])

        self.stdout.write(self.style.SUCCESS(f"Módulo: {module.slug}"))
        self.stdout.write(self.style.SUCCESS(f"Actualizados: {len(updated_fields)} ({', '.join(updated_fields) if updated_fields else 'ninguno'})"))
        self.stdout.write(self.style.WARNING(f"Omitidos: {len(omitted_fields)} ({', '.join(omitted_fields) if omitted_fields else 'ninguno'})"))

        self.stdout.write("Longitudes (caracteres):")
        for field_name in CONTENT_FILES:
            value = getattr(module, field_name, "") or ""
            self.stdout.write(f"  - {field_name}: {len(value)}")
