import sys

import django.contrib.auth.models
from django.contrib.auth.models import User as AuthUser
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

if 'makemigrations' not in sys.argv and 'migrate' not in sys.argv:
    AuthUser._meta.get_field('email')._unique = True


class User(django.contrib.auth.models.User):
    class Meta:
        proxy = True


class Profile(django.db.models.Model):
    user = django.db.models.OneToOneField(
        django.contrib.auth.models.User,
        on_delete=django.db.models.CASCADE,
        related_name='profile',
    )

    total_xp = django.db.models.IntegerField(default=0, verbose_name='всего опыта')

    last_activity_date = django.db.models.DateField(null=True, blank=True)
    current_streak = django.db.models.IntegerField(default=0)

    def update_streak(self):
        """Обновляет серию активных дней"""
        today = timezone.now().date()
        if self.last_activity_date == today:
            # Уже обновлено сегодня, ничего не меняем
            return

        if self.last_activity_date == today - timezone.timedelta(days=1):
            # Продолжаем серию
            self.current_streak += 1
        else:
            self.current_streak = 1

        self.last_activity_date = today
        self.save()

    def get_level(self):
        return self.total_xp // 100 + 1

    def get_next_level_xp(self):
        # XP для следующего уровня
        return 100 - self.total_xp % 100


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
