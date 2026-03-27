from django.urls import reverse_lazy
from django.views.generic import FormView

from users.forms import SignUpForm


class SignUpView(FormView):
    template_name = 'registration/register.html'
    form_class = SignUpForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        return super().form_valid(form)
