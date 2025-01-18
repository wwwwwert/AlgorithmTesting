import argparse
import importlib
import subprocess
import tempfile
from pathlib import Path
from typing import List

from tqdm import tqdm

STD = 'c++17'


def compile(task_path: Path, skip_compiler_checks: bool=False):
    print('Compiling...')
    cpp_path = task_path / 'main.cpp'
    bin_path = task_path / 'main'
    if skip_compiler_checks:
        exit_code = subprocess.run(
            [f"g++ {str(cpp_path)} -g -std={STD} -O2 -o {str(bin_path)}"],
            shell=True
        ).returncode
    else:
        exit_code = subprocess.run(
            [f"g++ {str(cpp_path)} -fsanitize=address,undefined -g -fno-sanitize-recover=all -std={STD} -O2 -Wall -Werror -Wsign-compare -o {str(bin_path)}"],
            shell=True
        ).returncode

    if exit_code != 0:
        print(f'Compilation error. Exit code {exit_code}')
        return False

    if not bin_path.exists():
        print('Compiling failed')
        return False
    
    return True


def get_tests(task_path: Path):
    tests_dir = task_path / 'tests'
    tests = []
    if not tests_dir.exists():
        print("Directory 'tests' was not found.")
        return tests
    
    for test in tests_dir.iterdir():
        if 'test' in test.name:
            tests.append(test)
    tests.sort(key=lambda x: int(str(x).split('_')[1]))
    return tests


def get_checker(task_path: Path):
    custom_checker_path = task_path / 'checker.py'
    if not custom_checker_path.exists():
        return lambda out_lines, true_out_lines: '\n'.join(out_lines) == '\n'.join(true_out_lines)
    else:
        print('Using custom checker:', custom_checker_path)
    
        module_name = "custom_checker"
        module = importlib.machinery.SourceFileLoader(module_name, str(custom_checker_path.absolute())).load_module()

        # Импорт функции checker
        checker = getattr(module, "checker")
        return checker


def test_case(
    test_path: Path,
    verbose: bool,
    input_file: str,
    output_file: str,
    true_output_file: str,
    checker
):
    bin_path = test_path.parent.parent / 'main'

    if verbose:
        print('\n', 'Running ', test_path.stem, sep='')
        print('Input:')
        with open(input_file, 'r') as fp:
            print(
                '\n'.join([
                    line.strip() for line in fp.readlines() if line.strip() != ''
                ]), '\n'
            )

    exit_code = subprocess.run(
        [f"./{bin_path} <{input_file} >{output_file}"],
        shell=True
    ).returncode

    if exit_code != 0:
        if verbose:
            print(f'Runtime error. Exit code {exit_code}')
        return 'RE'

    with open(output_file, 'r') as out, open(true_output_file, 'r') as true_out:
        out_lines = [line.strip() for line in out if line.strip() != '']
        true_out_lines = [line.strip() for line in true_out if line.strip() != '']

        if not checker(out_lines, true_out_lines):
            print(f'Error in {test_path.stem} occurred')
            print('Your answer:')
            print('\n'.join(out_lines), '\n')
            if exit_code == 0:
                print('Real answer')
                print('\n'.join(true_out_lines), '\n')
                print('-' * 20)
            return 'WA'
        
        if verbose:
            print('Output:')
            print('\n'.join(true_out_lines))
            print('-' * 20)
        return 'OK'


def run_tests(
    tests: List[Path],
    checker,
    verbose: bool=False, 
    dry_run: bool=False,
):
    passed_count = 0
    with tempfile.TemporaryDirectory() as dir:
        for test in tqdm(tests, desc='Running tests'):
            output_file = str(Path(dir) / 'output.txt')
            input_file = str(test / 'input.txt')
            true_output_file = str(test / 'output.txt')

            test_result = test_case(
                test,
                verbose,
                input_file,
                output_file,
                true_output_file,
                checker,
            )

            if test_result == 'OK':
                passed_count += 1
            elif test_result == 'WA':
                print(f'WA on test {test.name}')
                if not dry_run:
                    break
            elif test_result == 'RE':
                print(f'RE on test {test.name}')
                if not dry_run:
                    break

    if passed_count == len(tests):
        print('All tests passed')
    else:
        print(passed_count, '/', len(tests), 'tests passed')


def main(task_path: str, verbose: bool=False, skip_compiler_checks: bool=False, dry_run: bool=False):
    task_path = Path(task_path)

    if not compile(task_path, skip_compiler_checks):
        return

    tests = get_tests(task_path)
    if not tests:
        print('No tests found!')
        return
    
    checker = get_checker(task_path)

    run_tests(
        tests,
        checker,
        verbose, 
        dry_run,
    )


if __name__ == "__main__":
    args = argparse.ArgumentParser(description="Run tests for task")
    args.add_argument(
        "task",
        type=str,
        help="Task directory path",
    )
    args.add_argument(
        '-v',
        '--verbose', 
        action=argparse.BooleanOptionalAction,
        help="Verbose outputs",
    )
    args.add_argument(
        '-s',
        '--skip-compiler-checks', 
        action=argparse.BooleanOptionalAction,
        help="Compile program without necessary checks and sanitizers",
    )
    args.add_argument(
        '-d',
        '--dry-run', 
        action=argparse.BooleanOptionalAction,
        help="Skip output check. Testing would not stop if WA occures",
    )

    args = args.parse_args()

    # slant
    print("""    ___    __          ______          __      
   /   |  / /___ _____/_  __/__  _____/ /______
  / /| | / / __ `/ __ \/ / / _ \/ ___/ __/ ___/
 / ___ |/ / /_/ / /_/ / / /  __(__  ) /_(__  ) 
/_/  |_/_/\__, /\____/_/  \___/____/\__/____/  
         /____/                                """, end='\n\n')
    
    main(args.task, args.verbose, args.skip_compiler_checks, args.dry_run)