# models.py
from django.contrib.auth.models import User
from django.db import models


class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='achievements/', blank=True, null=True)
    """
    {"type": "xp_total", "value": 1000}
    {"type": "lessons_completed", "value": 5}
    {"type": "code_tasks_solved", "value": 10}
    {"type": "fragment_type", "fragment_type": "quiz", "count": 3}
    {"type": "module_completed", "module_id": 1}
    """
    criteria = models.JSONField()
    xp_reward = models.PositiveIntegerField(default=0)


class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)


class UserLessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
