from django.contrib import admin

import courses.models


class ModuleAdmin(admin.ModelAdmin):
    pass


class LessonAdmin(admin.ModelAdmin):
    pass


class FragmentAdmin(admin.ModelAdmin):
    pass


admin.site.register(courses.models.Module, ModuleAdmin)
admin.site.register(courses.models.Lesson, LessonAdmin)
admin.site.register(courses.models.Fragment, FragmentAdmin)
