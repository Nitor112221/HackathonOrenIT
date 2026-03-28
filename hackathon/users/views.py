from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from gamification.models import Achievement, UserAchievement

from users.forms import SignUpForm


class SignUpView(FormView):
    template_name = 'registration/register.html'
    form_class = SignUpForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, DetailView):
    model = get_user_model()
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        # Если передан username, показываем профиль этого пользователя, иначе текущего
        username = self.kwargs.get('username')
        if username:
            return get_object_or_404(User, username=username)
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        profile = user.profile
        context['profile'] = profile
        context['level'] = profile.get_level()
        context['next_level_xp'] = profile.get_next_level_xp()
        context['xp_percent'] = (profile.total_xp % 100)

        all_achievements = Achievement.objects.all()
        earned_ids = UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True)
        earned_achievements = Achievement.objects.filter(id__in=earned_ids)
        context['all_achievements'] = all_achievements
        context['earned_achievements'] = earned_achievements

        return context
