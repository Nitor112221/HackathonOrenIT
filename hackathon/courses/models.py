from django.db import models
from django.contrib.auth.models import User


class Module(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, unique=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    xp_reward = models.PositiveIntegerField(default=50)

    class Meta:
        ordering = ['order']
        unique_together = ['module', 'order']

    def __str__(self):
        return f"{self.module.title} - {self.title}"


class Fragment(models.Model):
    TYPE_CHOICES = (
        ('video', 'Видео'),
        ('text', 'Текст'),
        ('code', 'Код'),
        ('quiz', 'Викторина'),
        ('short_answer', 'Краткий ответ'),
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='fragments')
    order = models.PositiveIntegerField(default=0)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    data = models.JSONField(default=dict)  # структура зависит от type
    xp_reward = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ['lesson', 'order']

    def __str__(self):
        return f"{self.lesson.title} - {self.get_type_display()} ({self.order})"


class UserFragmentProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fragment_progress')
    fragment = models.ForeignKey(Fragment, on_delete=models.CASCADE, related_name='user_progress')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'fragment']
