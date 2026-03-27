from django.urls import path

import courses.views

urlpatterns = [
    path('modules/', courses.views.ModuleListView.as_view(), name='module_list'),
    path(
        'modules/<int:pk>/lessons/',
        courses.views.LessonListView.as_view(),
        name='lesson_list',
    ),
    path(
        'lessons/<int:pk>/',
        courses.views.LessonDetailView.as_view(),
        name='lesson_detail',
    ),
    path(
        'fragment/<int:fragment_id>/',
        courses.views.fragment_detail,
        name='fragment_detail',
    ),
    path(
        'fragment/<int:fragment_id>/complete/',
        courses.views.complete_fragment,
        name='complete_fragment',
    ),
    path(
        'fragment/<int:fragment_id>/submit/',
        courses.views.submit_task,
        name='submit_task',
    ),
    path(
        'fragment/<int:fragment_id>/status/',
        courses.views.fragment_status,
        name='fragment_status',
    ),
]
