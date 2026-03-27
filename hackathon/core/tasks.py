import json
import tempfile
import subprocess
import shutil

from hackathon.celery import app

@app.task
def run_user_code_in_docker(user_code, author_code, checker, tests, time_limit, memory_limit, pk):
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
    temp_dir = tempfile.mkdtemp()
    try:
        shutil.copy("hackathon/core/code_runner.py", temp_dir)

        # Подготавливаем тесты для передачи через окружение
        tests_json = json.dumps(tests)

        cmd = [
            'docker', 'run', '--rm',
            '-v', f'{temp_dir}:/mnt',
            '--memory', f'{memory_limit}m',                     # ограничение памяти
            '--ulimit', f'cpu={time_limit * 3 * len(tests)}',   # ограничение CPU
            '--cap-add=SYS_RESOURCE',                           # для resource.setrlimit
            '-e', f'TESTS={tests_json}',
            '-e', f'TIME_LIMIT={time_limit}',
            '-e', f'MEMORY_LIMIT={memory_limit}',
            '-e', f'USER_CODE={user_code}',
            '-e', f'AUTHOR_CODE={author_code}',
            '-e', f'CHECKER={checker}',
            'python:3', 'python', '/mnt/runner.py'
        ]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=time_limit * len(tests) * 3 + 5
        )

        try:
            output = proc.stdout.strip()
            result = json.loads(output)
        except json.JSONDecodeError:
            result = {
                'status': 'Fail',
                'test_error': None,
                'message': f'Invalid output from runner: {output}'
            }

        # TODO: добавить в базу данные

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)