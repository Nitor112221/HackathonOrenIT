from courses.models import TaskAttempt, UserFragmentProgress, Module
from gamification.models import UserLessonProgress, UserAchievement, Achievement


def evaluate_achievement(achievement: Achievement, user):
    criteria = achievement.criteria
    ctype = criteria.get('type')
    if ctype == 'xp_total':
        return user.profile.total_xp >= criteria['value']
    elif ctype == 'lessons_completed':
        count = UserLessonProgress.objects.filter(user=user, completed=True).count()
        return count >= criteria['value']
    elif ctype == 'code_tasks_solved':
        count = TaskAttempt.objects.filter(user=user, fragment__type='code', is_correct=True).count()
        return count >= criteria['value']
    elif ctype == 'fragment_type':
        # количество пройденных фрагментов определённого типа
        count = UserFragmentProgress.objects.filter(
            user=user,
            completed=True,
            fragment__type=criteria['fragment_type'],
        ).count()
        return count >= criteria['count']
    elif ctype == 'module_completed':
        # проверяем, что все уроки модуля пройдены
        module = Module.objects.get(id=criteria['module_id'])
        lessons = module.lessons.all()
        completed_lessons = UserLessonProgress.objects.filter(user=user, lesson__in=lessons, completed=True).count()
        return completed_lessons == lessons.count()

    return False


def check_achievements(user):
    earned_ids = UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True)
    pending = Achievement.objects.exclude(id__in=earned_ids)
    new_achievements = []
    for achievement in pending:
        if evaluate_achievement(achievement, user):
            UserAchievement.objects.create(user=user, achievement=achievement)
            if achievement.xp_reward:
                user.profile.total_xp += achievement.xp_reward
                user.profile.save()

            new_achievements.append(achievement)

    return new_achievements