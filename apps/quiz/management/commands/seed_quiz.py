# apps/quiz/management/commands/seed_quiz.py

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.training.models import TrainingModule
from apps.quiz.models import Question, Choice


DEFAULT_QUESTIONS = [
    {
        "order": 1,
        "text": "Según el video, ¿cuál es la idea central de la ergonomía?",
        "correct": "B",
        "explanation_correct": "La ergonomía busca que el trabajo se adapte a la persona y no al revés, para prevenir daños que se acumulan con el tiempo.",
        "choices": {
            "A": ("Comprar una silla cómoda para estar mejor.", "La ergonomía no se limita a la silla; se trata de adaptar el trabajo a la persona."),
            "B": ("Que el trabajo se adapte a la persona y no al revés.", ""),
            "C": ("Evitar accidentes visibles como resbalones y caídas únicamente.", "Los accidentes visibles son una parte; el foco del video está en daños acumulativos."),
            "D": ("Trabajar con más fuerza para terminar más rápido.", "Trabajar con más fuerza no previene lesiones; puede aumentarlas."),
        },
    },
    {
        "order": 2,
        "text": "¿Qué diferencia principal marca el video entre un accidente y una enfermedad profesional?",
        "correct": "C",
        "explanation_correct": "El accidente es súbito e inesperado; la enfermedad profesional se gesta con el tiempo por exposición repetida a riesgos.",
        "choices": {
            "A": ("La enfermedad profesional ocurre por una caída y el accidente por postura.", "Está invertido: la caída es accidente; la postura sostenida contribuye a enfermedad profesional."),
            "B": ("La enfermedad profesional siempre aparece de un día para otro.", "En el video se explica que es un daño silencioso y progresivo."),
            "C": ("El accidente es súbito; la enfermedad profesional se desarrolla con el tiempo.", ""),
            "D": ("No hay diferencias, son lo mismo.", "Legal y clínicamente se diferencian por su forma de aparición y criterios."),
        },
    },
    {
        "order": 3,
        "text": "Para que una dolencia sea reconocida legalmente como enfermedad profesional, ¿qué condiciones deben cumplirse?",
        "correct": "A",
        "explanation_correct": "Debe existir un agente de riesgo laboral, un diagnóstico médico claro y una relación directa entre el riesgo y la enfermedad.",
        "choices": {
            "A": ("Agente de riesgo + diagnóstico médico + relación directa con el trabajo.", ""),
            "B": ("Solo tener dolor y haber trabajado muchos años.", "El video remarca que se requieren criterios específicos, no solo antigüedad o dolor."),
            "C": ("Que el jefe lo confirme y el trabajador lo firme.", "No es un criterio médico-legal válido."),
            "D": ("Que sea una lesión visible como un golpe.", "Las enfermedades profesionales pueden no ser visibles al inicio."),
        },
    },
    {
        "order": 4,
        "text": "El video menciona siete factores de riesgo ergonómico. ¿Cuál de los siguientes NO es uno de ellos?",
        "correct": "D",
        "explanation_correct": "Los 7 factores mencionados son: manejo de cargas, posturas forzadas, movimientos repetitivos, estar de pie por mucho tiempo, vibraciones, frío/calor excesivo y presión constante (estrés por contacto).",
        "choices": {
            "A": ("Movimientos repetitivos.", ""),
            "B": ("Vibraciones de herramientas.", ""),
            "C": ("Manejo manual de cargas.", ""),
            "D": ("Exposición a radiación ionizante.", "Ese factor no aparece en la lista de 7 riesgos ergonómicos del video."),
        },
    },
    {
        "order": 5,
        "text": "¿Por qué es especialmente riesgoso manipular una carga pesada e inestable con mal agarre?",
        "correct": "B",
        "explanation_correct": "Cuando el agarre es malo y el peso se mueve, aumenta mucho el riesgo de lesión, especialmente en la zona lumbar.",
        "choices": {
            "A": ("Porque solo se lastiman las manos.", "El video destaca el riesgo de espalda/lumbar, no solo manos."),
            "B": ("Porque aumenta mucho el riesgo de lesión lumbar por inestabilidad y mal agarre.", ""),
            "C": ("Porque el cuerpo se vuelve más fuerte y resistente.", "No: incrementa la probabilidad de lesión."),
            "D": ("Porque es seguro si la carga es un saco y no una caja.", "El tipo de objeto no elimina el riesgo; lo clave es peso, agarre y postura."),
        },
    },
    {
        "order": 6,
        "text": "Según el video, levantar cargas por encima de los hombros es muy peligroso principalmente porque…",
        "correct": "C",
        "explanation_correct": "Al levantar por encima de los hombros, el cuerpo pierde ventaja mecánica y la tensión en hombros y cuello aumenta mucho.",
        "choices": {
            "A": ("Porque se ve mal ante los compañeros.", "No es un motivo ergonómico."),
            "B": ("Porque mejora la postura automáticamente.", "No: aumenta la carga sobre cuello/hombros."),
            "C": ("Porque se pierde ventaja mecánica y sube la tensión en hombros y cuello.", ""),
            "D": ("Porque la carga pesa menos en esa posición.", "No: la exigencia biomecánica aumenta."),
        },
    },
    {
        "order": 7,
        "text": "El video compara la presión en la espalda al levantar una caja de 25 kg 'bien' vs 'mal'. ¿Qué valores menciona?",
        "correct": "A",
        "explanation_correct": "Menciona aproximadamente 75 kg de presión si se levanta bien vs 375 kg si se levanta mal (cinco veces más).",
        "choices": {
            "A": ("75 kg vs 375 kg.", ""),
            "B": ("25 kg vs 50 kg.", "El video habla de presión resultante mucho mayor que el peso real."),
            "C": ("100 kg vs 200 kg.", "Los valores citados en el video son 75 y 375."),
            "D": ("375 kg vs 75 kg.", "Está invertido: la mala técnica aumenta la presión."),
        },
    },
    {
        "order": 8,
        "text": "¿Cuáles son las 'cuatro reglas de oro' para levantar cargas que se mencionan en el video?",
        "correct": "D",
        "explanation_correct": "1) Base estable y buen agarre con toda la mano. 2) Fuerza desde las piernas con espalda recta. 3) Carga pegada al cuerpo. 4) No girar la cintura; girar moviendo los pies.",
        "choices": {
            "A": ("Espalda redonda, piernas estiradas, girar cintura, carga lejos.", "Son exactamente los errores que aumentan el riesgo."),
            "B": ("Apoyar la carga en el cuello, levantar rápido, girar tronco, mirar hacia abajo.", "No corresponde a las reglas del video."),
            "C": ("Separar los pies, pero levantar con la espalda y girar con la cintura.", "La regla clave es usar piernas y NO girar cintura con carga."),
            "D": ("Base estable y buen agarre + fuerza desde piernas con espalda recta + carga cerca + girar con los pies, no con la cintura.", ""),
        },
    },
    {
        "order": 9,
        "text": "Según el video, ¿cuál es el peso máximo recomendado para levantar de forma rutinaria?",
        "correct": "B",
        "explanation_correct": "El video menciona 25 kg como límite recomendado para levantamiento rutinario. Si pesa más, se requiere ayuda mecánica o de otra persona.",
        "choices": {
            "A": ("15 kg.", "El valor mencionado en el video es 25 kg."),
            "B": ("25 kg.", ""),
            "C": ("35 kg.", "El video marca 25 kg como límite recomendado."),
            "D": ("No existe un límite recomendado.", "Sí: el video indica un límite claro."),
        },
    },
    {
        "order": 10,
        "text": "Si aparece dolor o un síntoma, ¿qué indica el protocolo del video y cuál es la herramienta preventiva más efectiva?",
        "correct": "A",
        "explanation_correct": "Protocolo: avisar inmediatamente, gestionar atención médica por la aseguradora y no volver a la tarea hasta el alta. Prevención: la pausa activa.",
        "choices": {
            "A": ("Avisar, gestionar atención médica por aseguradora y no volver sin alta; la herramienta preventiva es la pausa activa.", ""),
            "B": ("Aguantar el dolor, automedicarse y seguir trabajando; la prevención es trabajar más rápido.", "El video dice lo contrario: no ocultar dolor y no volver sin alta."),
            "C": ("Cambiar solo la silla; la prevención es evitar hablar del tema.", "La silla no es la solución única y ocultar síntomas es un error."),
            "D": ("Esperar una semana y ver si se pasa; la prevención es no moverse durante la jornada.", "El video remarca que el cuerpo está hecho para moverse y que no hay que ocultar síntomas."),
        },
    },
]


class Command(BaseCommand):
    help = "Crea 10 preguntas + opciones para un módulo (por defecto: el módulo activo más reciente)."

    def add_arguments(self, parser):
        parser.add_argument("--slug", type=str, help="Slug del módulo a seedear (opcional).")

    @transaction.atomic
    def handle(self, *args, **opts):
        slug = opts.get("slug")
        if slug:
            module = TrainingModule.objects.filter(slug=slug).first()
        else:
            module = TrainingModule.objects.filter(is_active=True).order_by("-updated_at").first()

        if not module:
            raise CommandError("No hay módulo activo (o slug inválido). Creá/activá un TrainingModule en el admin.")

        if Question.objects.filter(module=module).exists():
            self.stdout.write(self.style.WARNING(f"Ya existen preguntas para {module.slug}. No hago nada."))
            return

        for qd in DEFAULT_QUESTIONS:
            q = Question.objects.create(
                module=module,
                order=qd["order"],
                text=qd["text"],
                explanation_correct=qd["explanation_correct"],
            )
            for label, (txt, expl) in qd["choices"].items():
                Choice.objects.create(
                    question=q,
                    label=label,
                    text=txt,
                    is_correct=(label == qd["correct"]),
                    explanation_if_chosen=expl,
                )

        self.stdout.write(self.style.SUCCESS(f"Seed OK: {module.slug} (10 preguntas)"))