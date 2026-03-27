from django import forms
import django.contrib.auth.forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={'class': 'form-control'},
        ),
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует.')

        return email

    class Meta(django.contrib.auth.forms.UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            if not isinstance(field.field.widget, django.forms.CheckboxInput):
                field.field.widget.attrs['class'] = 'form-control'
            else:
                field.field.widget.attrs['class'] = 'form-check-input'
