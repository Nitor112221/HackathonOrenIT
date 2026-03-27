from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.generic import DetailView, ListView

from courses.models import Fragment, Lesson, Module, TaskAttempt, UserFragmentProgress


class ModuleListView(LoginRequiredMixin, ListView):
    model = Module
    template_name = 'courses/module_list.html'
    context_object_name = 'modules'


class LessonListView(LoginRequiredMixin, DetailView):
    model = Module
    template_name = 'courses/lesson_list.html'
    context_object_name = 'module'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lessons = self.object.lessons.all()
        for lesson in lessons:
            total = lesson.fragments.count()
            completed = UserFragmentProgress.objects.filter(
                user=self.request.user,
                fragment__lesson=lesson,
                completed=True,
            ).count()
            lesson.is_completed = total > 0 and total == completed

        context['lessons'] = lessons
        return context


class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Lesson
    template_name = 'courses/lesson_detail.html'
    context_object_name = 'lesson'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fragments = self.object.fragments.all()
        completed_ids = UserFragmentProgress.objects.filter(
            user=self.request.user,
            fragment__in=fragments,
            completed=True,
        ).values_list('fragment_id', flat=True)

        # Определяем текущий фрагмент
        current = None
        for frag in fragments:
            if frag.id not in completed_ids:
                current = frag
                break

        if current is None and fragments.exists():
            current = fragments.first()

        context['fragments'] = fragments
        context['completed_ids'] = list(completed_ids)
        context['current_fragment'] = current
        return context


@login_required
def fragment_detail(request, fragment_id):
    fragment = get_object_or_404(Fragment, id=fragment_id)
    context = {
        'fragment': fragment,
        'completed': UserFragmentProgress.objects.filter(
            user=request.user,
            fragment=fragment,
            completed=True,
        ).exists(),
    }
    return render(request, 'courses/fragments/fragment_base.html', context)


@login_required
def complete_fragment(request, fragment_id):
    fragment = get_object_or_404(Fragment, id=fragment_id)
    progress, created = UserFragmentProgress.objects.get_or_create(
        user=request.user,
        fragment=fragment,
    )
    if not progress.completed:
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()
        request.user.profile.total_xp += fragment.xp_reward
        request.user.profile.save()

    return render(
        request,
        'courses/fragments/fragment_base.html',
        {'fragment': fragment },
    )


@login_required
def submit_task(request, fragment_id):
    fragment = get_object_or_404(Fragment, id=fragment_id)
    user = request.user
    answer = request.POST.get('answer')

    is_correct = False
    if fragment.type == 'code':
        # TODO добавить обработку посылок
        # Отправляем задачу в Celery
        # Здесь нужно отправить задачу в Celery, а пока вернём сообщение
        return HttpResponse(
            '<div class="alert alert-info">Код отправлен на проверку. '
            'Результат появится позже.</div>',
        )
    elif fragment.type == 'quiz':
        correct_options = fragment.data.get('correct', [])
        selected = request.POST.getlist('options')
        selected = list(map(int, selected))
        answer = str(selected)
        is_correct = set(selected) == set(correct_options)
    elif fragment.type == 'short_answer':
        correct_answers = fragment.data.get('correct_answers', [])
        is_correct = answer.strip() in correct_answers

    if is_correct:
        TaskAttempt.objects.create(
            user=user,
            fragment=fragment,
            answer=answer,
            status='success',
            is_correct=True,
            completed_at=timezone.now(),
        )
        progress, _ = UserFragmentProgress.objects.get_or_create(
            user=user,
            fragment=fragment,
        )
        if not progress.completed:
            progress.completed = True
            progress.completed_at = timezone.now()
            progress.save()
            user.profile.total_xp += fragment.xp_reward
            user.profile.save()

        return render(
            request,
            'courses/fragments/fragment_base.html',
            {
                'fragment': fragment,
                'completed': True,
             },
        )
    else:
        context = {
            'fragment': fragment,
            'error': 'Ответ неверный, попробуйте ещё раз',
            'completed': False,
        }
        return render(
            request,
            'courses/fragments/fragment_base.html',
            context,
        )
