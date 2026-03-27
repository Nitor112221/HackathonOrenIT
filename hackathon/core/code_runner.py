import json
import os
import resource
import subprocess
from pathlib import Path


def set_memory_limit(max_memory_mb):
    max_memory_bytes = max_memory_mb * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (max_memory_bytes, max_memory_bytes))


def run_code(code, folder, tests, time_limit, memory_limit):
    file = Path('code.py')
    file.touch()
    file.write_text(code)

    set_memory_limit(memory_limit)

    result = {
        'status': 'AC',
        'test_error': None,
        'message': None,
    }

    for i, test in enumerate(tests):
        input_data = test['input_data']
        try:
            process = subprocess.run(
                ['python', 'user_code.py'],
                input=input_data,
                check=True,
                text=True,
                capture_output=True,
                timeout=time_limit,
            )

            program_output = process.stdout.strip()
            file_output = Path(folder) / Path(f'{i}.txt')
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
            result['message'] = str(e) + ' ' + e.__class__.__name__
            break

    return result


def run_checker(code_checker, test_count, folder_user="folder/user", folder_author="folder/author") -> None | (str, int):
    file = Path('checker.py')
    file.touch()
    file.write_text(code_checker)

    folder_user = Path(folder_user)
    folder_author = Path(folder_author)
    for i in range(test_count):
        try:
            process = subprocess.run(
                ['python', 'user_code.py', folder_user / f'{i}.txt', folder_author / f'{i}.txt'],
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
    user_code = os.getenv('USER_CODE')
    author_code = os.getenv('AUTHOR_CODE')
    checker = os.getenv('CHECKER')
    time_limit = os.getenv('TIME_LIMIT')
    memory_limit = os.getenv('MEMORY_LIMIT')

    result = run_code(user_code, 'user', tests, time_limit, memory_limit)
    if result['status'] != 'AC':
        print(json.dumps(result))
        exit()

    result_auth = run_code(author_code, 'author', tests, time_limit, memory_limit)
    if result_auth != 'AC':
        result['status'] = 'Fail'
        result['message'] = 'Testing error, problem on our side'
        result['error'] = result_auth['test_error']
        print(json.dumps(result))
        exit()

    res = run_checker(checker, len(tests))
    if res is None:
        print(json.dumps(result))
        exit()

    result['status'] = res[0]
    result['error'] = res[1]

    print(json.dumps(result))
