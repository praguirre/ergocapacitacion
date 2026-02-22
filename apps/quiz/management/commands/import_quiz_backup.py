import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.quiz.models import Choice, Question
from apps.training.models import TrainingModule


class Command(BaseCommand):
    help = "Importa backup canónico de quiz para un módulo, con opción de replace total."

    def add_arguments(self, parser):
        parser.add_argument(
            "--module",
            default="ergonomia",
            help="Slug del módulo de destino (default: ergonomia)",
        )
        parser.add_argument(
            "--path",
            default="apps/quiz/fixtures/backup_quiz_questions.json",
            help="Ruta del backup JSON (default: apps/quiz/fixtures/backup_quiz_questions.json)",
        )
        parser.add_argument(
            "--replace",
            action="store_true",
            help="Borra preguntas/opciones actuales del módulo e importa todo el backup.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        module_slug = options["module"]
        backup_path = Path(options["path"])
        replace = options["replace"]

        module = TrainingModule.objects.filter(slug=module_slug).first()
        if not module:
            raise CommandError(f"No existe TrainingModule con slug='{module_slug}'.")

        if not backup_path.exists():
            raise CommandError(f"No existe el backup JSON: {backup_path}")

        try:
            payload = json.loads(backup_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CommandError(f"JSON inválido en {backup_path}: {exc}") from exc

        questions_data = [row for row in payload if row.get("model") == "quiz.question"]
        choices_data = [row for row in payload if row.get("model") == "quiz.choice"]

        if not questions_data or not choices_data:
            raise CommandError("El backup no contiene quiz.question y quiz.choice válidos.")

        deleted_choices = 0
        deleted_questions = 0

        if replace:
            deleted_choices, _ = Choice.objects.filter(question__module=module).delete()
            deleted_questions, _ = Question.objects.filter(module=module).delete()

        questions_data.sort(key=lambda row: row.get("fields", {}).get("order", 0))

        question_pk_map = {}
        created_questions = 0
        updated_questions = 0

        for item in questions_data:
            fields = item.get("fields", {})
            old_question_pk = item.get("pk")

            order = fields.get("order")
            text = fields.get("text", "")
            explanation_correct = fields.get("explanation_correct", "")

            if order is None:
                raise CommandError("Se encontró una pregunta sin 'order' en el backup.")

            if replace:
                question = Question.objects.create(
                    module=module,
                    order=order,
                    text=text,
                    explanation_correct=explanation_correct,
                )
                created_questions += 1
            else:
                question, created = Question.objects.update_or_create(
                    module=module,
                    order=order,
                    defaults={
                        "text": text,
                        "explanation_correct": explanation_correct,
                    },
                )
                if created:
                    created_questions += 1
                else:
                    updated_questions += 1

            question_pk_map[old_question_pk] = question

        created_choices = 0
        updated_choices = 0
        skipped_choices = 0

        for item in choices_data:
            fields = item.get("fields", {})
            old_question_pk = fields.get("question")
            question = question_pk_map.get(old_question_pk)

            if not question:
                skipped_choices += 1
                continue

            label = fields.get("label", "")
            if not label:
                skipped_choices += 1
                continue

            defaults = {
                "text": fields.get("text", ""),
                "is_correct": fields.get("is_correct", False),
                "explanation_if_chosen": fields.get("explanation_if_chosen", ""),
            }

            if replace:
                Choice.objects.create(
                    question=question,
                    label=label,
                    **defaults,
                )
                created_choices += 1
            else:
                _, created = Choice.objects.update_or_create(
                    question=question,
                    label=label,
                    defaults=defaults,
                )
                if created:
                    created_choices += 1
                else:
                    updated_choices += 1

        q_count = Question.objects.filter(module=module).count()
        c_count = Choice.objects.filter(question__module=module).count()

        self.stdout.write(self.style.SUCCESS(f"Módulo: {module.slug}"))
        self.stdout.write(self.style.SUCCESS(f"replace: {'sí' if replace else 'no'}"))
        if replace:
            self.stdout.write(self.style.WARNING(f"eliminadas choices: {deleted_choices}"))
            self.stdout.write(self.style.WARNING(f"eliminadas questions: {deleted_questions}"))

        self.stdout.write(self.style.SUCCESS(f"questions creadas: {created_questions}"))
        self.stdout.write(self.style.SUCCESS(f"questions actualizadas: {updated_questions}"))
        self.stdout.write(self.style.SUCCESS(f"choices creadas: {created_choices}"))
        self.stdout.write(self.style.SUCCESS(f"choices actualizadas: {updated_choices}"))
        self.stdout.write(self.style.WARNING(f"choices omitidas: {skipped_choices}"))

        self.stdout.write(self.style.SUCCESS(f"Q_COUNT={q_count}"))
        self.stdout.write(self.style.SUCCESS(f"C_COUNT={c_count}"))

        preview_questions = list(
            Question.objects.filter(module=module)
            .order_by("order")
            .values_list("order", "text")[:3]
        )
        self.stdout.write("Primeras 3 preguntas:")
        for order, text in preview_questions:
            short_text = (text[:90] + "...") if len(text) > 90 else text
            self.stdout.write(f"  {order}. {short_text}")
