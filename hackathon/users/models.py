import sys

import django.contrib.auth.models
from django.contrib.auth.models import User as AuthUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

if 'makemigrations' not in sys.argv and 'migrate' not in sys.argv:
    AuthUser._meta.get_field('email')._unique = True


class User(django.contrib.auth.models.User):
    class Meta:
        proxy = True


class Profile(django.db.models.Model):
    user = django.db.models.OneToOneField(
        django.contrib.auth.models.User,
        on_delete=django.db.models.CASCADE,
        related_name="profile",
    )

    total_xp = django.db.models.IntegerField(default=0, verbose_name='всего опыта')


@receiver(post_save, sender=AuthUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=AuthUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(pre_save, sender=AuthUser)
def validate_unique_email(sender, instance, **kwargs):
    if AuthUser.objects.filter(email=instance.email).exclude(pk=instance.pk).exists():
        raise ValidationError('Пользователь с таким email уже существует.')
