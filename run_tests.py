import argparse
import subprocess
import tempfile
from pathlib import Path
from typing import List

from tqdm import tqdm


def compile(task_path: Path):
    print('Compiling...')
    cpp_path = task_path / 'main.cpp'
    bin_path = task_path / 'main'
    exit_code = subprocess.run(
        [f"g++ {str(cpp_path)} -fsanitize=address,undefined -fno-sanitize-recover=all -std=c++17 -O2 -Wall -Werror -Wsign-compare -o {str(bin_path)}"],
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


def test_case(
    test_path: Path,
    verbose: bool,
    output_file: str,
    input_file: str,
    true_output_file: str
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

        if '\n'.join(out_lines) != '\n'.join(true_out_lines):
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
    verbose: bool=False, 
    dry_run: bool=False
):
    wa_count = 0
    with tempfile.TemporaryDirectory() as dir:
        for test in tqdm(tests, desc='Running tests'):
            output_file = str(Path(dir) / 'output.txt')
            input_file = str(test / 'input.txt')
            true_output_file = str(test / 'output.txt')

            test_result = test_case(
                test,
                verbose,
                output_file,
                input_file,
                true_output_file
            )

            if test_result == 'OK':
                pass
            elif test_result == 'WA':
                wa_count += 1
                if not dry_run:
                    break
            elif test_result == 'RE':
                wa_count += 1
                if not dry_run:
                    break

    if wa_count == 0:
        print('All tests passed')
    else:
        print(len(tests) - wa_count, '/', len(tests), 'tests passed')


def main(task_path: str, verbose: bool=False, dry_run: bool=False):
    task_path = Path(task_path)

    if not compile(task_path):
        return

    tests = get_tests(task_path)
    if not tests:
        print('No tests found!')
        return

    run_tests(
        tests, 
        verbose, 
        dry_run
    )


if __name__ == "__main__":
    args = argparse.ArgumentParser(description="Run tests for task")
    args.add_argument(
        "-t",
        "--task",
        default=None,
        type=str,
        help="task directory path",
    )
    args.add_argument(
        '-v',
        '--verbose', 
        action=argparse.BooleanOptionalAction,
        help="Verbose outputs",
    )
    args.add_argument(
        '-d',
        '--dry_run', 
        action=argparse.BooleanOptionalAction,
        help="Skip output check. Testing would not stop if WA occures.",
    )

    args = args.parse_args()
    main(args.task, args.verbose, args.dry_run)