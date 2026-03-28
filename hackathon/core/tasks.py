import json
import os
import shutil
import subprocess
import tempfile
import traceback

from django.contrib.auth import get_user_model
from django.utils import timezone

import courses.models
from gamification.achievement_service import check_achievements
from gamification.models import UserLessonProgress
from hackathon.celery_config import app


@app.task
def run_user_code_in_docker(
    user_code,
    author_code,
    checker,
    tests,
    time_limit,
    memory_limit,
    pk,
    user_id,
    fragment_id,
):
    """
    Запускает пользовательский код в Docker-контейнере.

    Аргументы:
        user_code (str): Исходный код пользователя.
        tests (list of dict): Список тестов, каждый содержит:
            - 'number' (int)
            - 'input_data' (str)
            - 'output_data' (str)
        time_limit (int): Максимальное время выполнения одного теста (сек).
        memory_limit (int): Ограничение памяти (МБ).

    Возвращает:
        dict: {'status': 'AC', 'test_error': None, 'message': None} или
              {'status': 'WA'/'TL'/'RE'/'Fail', 'test_error': int, 'message': str}
    """
    user = get_user_model().objects.get(id=user_id)
    fragment = courses.models.Fragment.objects.get(id=fragment_id)

    attempt: courses.models.TaskAttempt = courses.models.TaskAttempt.objects.get(id=pk)
    attempt.status = 'running'
    attempt.save()
    temp_dir = tempfile.mkdtemp()
    try:
        runner_path = os.path.join(temp_dir, 'code_runner.py')
        shutil.copy('core/code_runner.py', runner_path)
        if not os.path.exists(runner_path):
            raise FileNotFoundError(f"code_runner.py not found 2")

        # Подготавливаем тесты для передачи через окружение
        tests_json = json.dumps(tests)

        cmd = [
            'docker',
            'run',
            '--rm',
            '-v',
            f'{temp_dir}:/mnt/',
            '--memory',
            f'{memory_limit}m',  # ограничение памяти
            '-e',
            f'TESTS={tests_json}',
            '-e',
            f'TIME_LIMIT={time_limit}',
            '-e',
            f'MEMORY_LIMIT={memory_limit}',
            '-e',
            f'USER_CODE={user_code}',
            '-e',
            f'AUTHOR_CODE={author_code}',
            '-e',
            f'CHECKER={checker}',
            'python:3',
            'python',
            '/mnt/code_runner.py',

        ]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=time_limit * len(tests) * 3 + 5,
        )
        try:
            output = proc.stdout.strip()
            result = json.loads(output)
        except json.JSONDecodeError:
            result = {
                'status': 'Fail',
                'test_error': 1,
                'message': f'Некорректный вывод чекера: {proc}',
            }
        if result['status'] == 'AC':
            attempt.status = 'success'
            attempt.is_correct = True
        else:
            attempt.status = 'failure'
            attempt.is_correct = False
            attempt.output = (
                f'Ошибка на тесте{result["test_error"]}.'
                f'\nСообщение: {result["message"]}'
            )

        attempt.completed_at = timezone.now()
        attempt.save()

        if attempt.is_correct:
            progress, created = (
                courses.models.UserFragmentProgress.objects.get_or_create(
                    user=user,
                    fragment=fragment,
                )
            )
            if not progress.completed:
                progress.completed = True
                progress.completed_at = timezone.now()
                progress.save()
                user.profile.total_xp += fragment.xp_reward
                user.profile.update_streak()
                user.profile.save()

                lesson = fragment.lesson
                total_fragments = lesson.fragments.count()
                completed_fragments = courses.models.UserFragmentProgress.objects.filter(user=user, fragment__lesson=lesson,
                                                                                  completed=True).count()
                if total_fragments == completed_fragments:
                    lesson_progress, _ = UserLessonProgress.objects.get_or_create(user=user, lesson=lesson)
                    if not lesson_progress.completed:
                        lesson_progress.completed = True
                        lesson_progress.completed_at = timezone.now()
                        lesson_progress.save()

                check_achievements(user)

    except subprocess.TimeoutExpired as e:
        # Общий таймаут выполнения всех тестов
        attempt.status = 'failure'
        attempt.is_correct = False
        attempt.output = f'Превышено общее время выполнения (таймаут {e.timeout} сек).'
        attempt.completed_at = timezone.now()
        attempt.save()
    except Exception as e:
        # Любая другая ошибка (docker не установлен, ошибка копирования, и т.п.)
        attempt.status = 'failure'
        attempt.is_correct = False
        attempt.output = (
            f'Внутренняя ошибка при проверке: {str(e)}\n{traceback.format_exc()}'
        )
        attempt.completed_at = timezone.now()
        attempt.save()
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
