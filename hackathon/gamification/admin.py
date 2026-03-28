from django.contrib import admin

import gamification.models


class AchievementAdmin(admin.ModelAdmin):
    pass


class UserAchievementAdmin(admin.ModelAdmin):
    pass


class UserLessonProgressAdmin(admin.ModelAdmin):
    pass


admin.site.register(gamification.models.Achievement, AchievementAdmin)
admin.site.register(gamification.models.UserAchievement, UserAchievementAdmin)
admin.site.register(gamification.models.UserLessonProgress, UserLessonProgressAdmin)
