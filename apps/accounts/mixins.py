# apps/accounts/mixins.py
# ============================================================================
# COMMIT 10: Mixins para vistas basadas en clase
# ============================================================================

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse


class ProfessionalRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin para vistas basadas en clase que requieren un profesional.

    Uso:
        class MyView(ProfessionalRequiredMixin, TemplateView):
            template_name = 'my_template.html'
    """
    login_url = None  # Se define en get_login_url()

    def get_login_url(self):
        return reverse('professional_login')

    def test_func(self):
        # Defensa extra: el usuario debe estar activo además de ser profesional
        return self.request.user.is_active and self.request.user.is_professional

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            # Usuario logueado pero no es profesional
            return redirect('dashboard')  # Ajustar según tu UX/URLs reales
        return super().handle_no_permission()


class TraineeRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin para vistas que requieren un trabajador (trainee).

    Uso:
        class TrainingView(TraineeRequiredMixin, TemplateView):
            template_name = 'training.html'
    """
    login_url = None

    def get_login_url(self):
        return reverse('landing')

    def test_func(self):
        # Defensa extra: el usuario debe estar activo además de ser trainee
        return self.request.user.is_active and self.request.user.is_trainee


class SubscriptionRequiredMixin(ProfessionalRequiredMixin):
    """
    Mixin que requiere suscripción activa (para futuro).

    Uso:
        class PremiumView(SubscriptionRequiredMixin, TemplateView):
            required_tier = 'premium'
            template_name = 'premium_feature.html'
    """
    required_tier = 'basic'

    def test_func(self):
        if not super().test_func():
            return False

        tier_levels = {'free': 0, 'basic': 1, 'premium': 2}
        required_level = tier_levels.get(self.required_tier, 0)
        user_level = tier_levels.get(self.request.user.subscription_tier, 0)

        return (
            self.request.user.has_active_subscription
            and user_level >= required_level
        )
