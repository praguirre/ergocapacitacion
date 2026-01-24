# apps/quiz/admin.py

from django.contrib import admin
from .models import Question, Choice, QuizAttempt, QuizState

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0  # No mostrar filas vacías extra

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("module", "order", "text_preview")
    list_filter = ("module",)
    search_fields = ("text",)
    inlines = [ChoiceInline]  # Esto permite editar respuestas dentro de la pregunta

    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = "Texto"

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "module", "score", "passed", "started_at", "submitted_at")
    list_filter = ("module", "passed", "started_at")
    search_fields = ("user__email", "user__cuil")

@admin.register(QuizState)
class QuizStateAdmin(admin.ModelAdmin):
    list_display = ("user", "module", "attempts_used", "lockout_until")
    search_fields = ("user__email",)