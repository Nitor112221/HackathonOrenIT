import json
import os
import subprocess
from pathlib import Path
from typing import Tuple


def run_code(code, folder, tests, time_limit, memory_limit):
    file = Path('code.py')
    file.touch()
    code = code.replace('\\n', '\n')
    code = code.replace("'\\''", "'")
    code = code.replace("\\'", "")
    file.write_text(code)

    folder = Path(folder)
    folder.mkdir(exist_ok=True)

    result = {
        'status': 'AC',
        'test_error': None,
        'message': None,
    }

    for i, test in enumerate(tests):
        input_data = test.replace('\\n', '\n')
        try:
            process = subprocess.run(
                ['python', 'code.py'],
                input=input_data,
                check=True,
                text=True,
                capture_output=True,
                timeout=time_limit,
            )

            program_output = process.stdout.strip()
            file_output = folder / Path(f'{i}.txt')
            file_output.touch()
            file_output.write_text(program_output)

        except subprocess.TimeoutExpired:
            result['status'] = 'TL'
            result['test_error'] = i
            result['message'] = f'Time limit exceeded on test {i}'
            break

        except Exception as e:
            result['status'] = 'RE'
            result['test_error'] = i
            result['message'] = str(e) + ' ' + e.__class__.__name__ + ' ' + e.__str__()
            break

    return result


def run_checker(code_checker, test_count, folder_user="user", folder_author="author") -> Tuple[str, int] | None:
    file = Path('checker.py')
    file.touch()
    code_checker = code_checker.replace('\\n', '\n')
    code_checker = code_checker.replace("'\\''", "'")
    code_checker = code_checker.replace("\\'", "")
    file.write_text(code_checker)

    folder_user = Path(folder_user)
    folder_author = Path(folder_author)
    for i in range(test_count):
        try:
            process = subprocess.run(
                ['python', 'checker.py', folder_user / f'{i}.txt', folder_author / f'{i}.txt'],
                check=True,
                text=True,
                capture_output=True,
                timeout=time_limit
            )
            if 'OK' not in process.stdout:
                return 'WA', i
        except Exception as e:
            return "Fail", i



if __name__ == '__main__':
    tests = os.getenv('TESTS')
    tests_parsed = json.loads(tests)
    user_code = os.getenv('USER_CODE')
    author_code = os.getenv('AUTHOR_CODE')
    checker = os.getenv('CHECKER')
    time_limit = int(os.getenv('TIME_LIMIT'))
    memory_limit = int(os.getenv('MEMORY_LIMIT'))

    result = run_code(user_code, 'user', tests_parsed, time_limit, memory_limit)
    if result['status'] != 'AC':
        print(json.dumps(result))
        exit()

    result_auth = run_code(author_code, 'author', tests_parsed, time_limit, memory_limit)
    if result_auth['status'] != 'AC':
        result['status'] = 'Fail'
        result['message'] = 'Testing error, problem on our side'
        result['test_error'] = result_auth['test_error'] + 1
        print(json.dumps(result))
        exit()
    res = run_checker(checker, len(tests_parsed))
    if res is None:
        print(json.dumps(result))
        exit()
    result['status'] = res[0]
    result['test_error'] = res[1] + 1

    if res[0] == 'Fail':
        result['message'] = 'Ошибка проверяющей системы'
    elif res[0] == 'WA':
        result['message'] = f'Неправильный ответ'

    print(json.dumps(result))
