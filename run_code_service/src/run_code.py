import json
import os
import shutil
import subprocess
import tempfile
import traceback
import logging
import uuid

logger = logging.getLogger("run_code_service")

SHARED_TEMP_BASE  = "/tmp/code_runner_data"

def run_user_code_in_docker(
    user_code,
    author_code,
    checker,
    tests,
    time_limit,
    memory_limit,
):
    """
    Запускает пользовательский код в Docker-контейнере.

    Аргументы:
        user_code (str): Исходный код пользователя.
        tests (list of str): Список тестов, каждый содержит:
            - 'input_data' (str)
        time_limit (int): Максимальное время выполнения одного теста (сек).
        memory_limit (int): Ограничение памяти (МБ).

    Возвращает:
        dict: {'status': 'AC', 'test_error': None, 'message': None} или
              {'status': 'WA'/'TL'/'RE'/'Fail', 'test_error': int, 'message': str}
    """
    if os.path.exists(SHARED_TEMP_BASE):
        run_id = str(uuid.uuid4())
        temp_dir = os.path.join(SHARED_TEMP_BASE, run_id)
        os.makedirs(temp_dir, exist_ok=True)
        use_shared = True
    else:
        temp_dir = tempfile.mkdtemp()
        use_shared = False
        logger.warning(f"Shared temp dir {SHARED_TEMP_BASE} not found, using {temp_dir}")
    try:
        runner_path = os.path.join(temp_dir, 'code_runner.py')
        code_runner_path = os.path.join(os.path.curdir, 'scripts/code_runner.py')

        if not os.path.exists(code_runner_path):
            raise FileNotFoundError('code_runner.py not found in scripts/')

        shutil.copy(code_runner_path, runner_path)
        if not os.path.exists(runner_path):
            raise FileNotFoundError('code_runner.py not copied')

        # Подготавливаем тесты для передачи через окружение
        tests_json = json.dumps(tests)

        cmd = [
            'docker',
            'run',
            '--rm',
            '-v',
            f'{temp_dir}:/scripts/',
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
            '/scripts/code_runner.py',
            # 'ls'
        ]
        print(str(cmd))
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=time_limit * len(tests) * 3 + 5,
        )
        try:
            output = proc.stdout.strip()
            return json.loads(output)
        except json.JSONDecodeError:
            return {
                'status': 'Fail',
                'test_error': 1,
                'message': f'Некорректный вывод чекера: {proc}',
            }

    except subprocess.TimeoutExpired as e:
        # Общий таймаут выполнения всех тестов
        return {
            'status': 'TL',
            'test_error': None,
            'message': f'Превышено ограничение по времени',
        }
    except Exception as e:
        logger.error(f'Внутренняя ошибка при проверке: {str(e)}\n{traceback.format_exc()}')
        return {
            'status': 'Fail',
            'test_error': None,
            'message': f'Ошибка тестирования',
        }
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        pass
