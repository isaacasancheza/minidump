#!/usr/bin/env python3
from re import sub
from json import loads, dumps
from argparse import ArgumentParser, FileType
from subprocess import run
from tempfile import NamedTemporaryFile


def pascal_to_snake(name):
    name = sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return sub('([a-z0-9])([A-Z])', r'\1_\2', name).upper()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('function_name', type=str)

    parser.add_argument('-s', '--stack_name', dest='stack_name', type=str)
    parser.add_argument('--output-file', dest='output_file', type=FileType(), default='./outputs.json')
    parser.add_argument('--template-file', dest='template_file', type=FileType(), default='./cdk.out/Stack.template.json')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--include', nargs='+')
    group.add_argument('--exclude', nargs='+')

    args = parser.parse_args()
    include = args.include
    exclude = args.exclude
    stack_name = args.stack_name
    output_file = args.output_file
    function_name = args.function_name
    template_file = args.template_file

    outputs = loads(output_file.read())
    if not isinstance(outputs, dict):
        parser.error('outputs file must contain a json object')
    if not outputs:
        parser.error('outputs file cannot be an empty json object')

    if stack_name and stack_name not in outputs:
        parser.error(f"stack name '{stack_name}' doesn't exist on outputs")
    else:
        # guess stack name from outputs
        if len(outputs) > 1:
            parser.error('too many keys on outputs')
        stack_name = list(outputs.keys())[0]

    if include:
        env_vars = {
            'Parameters': {pascal_to_snake(key): value for key, value in outputs.get(stack_name).items() if key in include}
        }
    elif exclude:
        env_vars = {
            'Parameters': {pascal_to_snake(key): value for key, value in outputs.get(stack_name).items() if key not in exclude}
        }
    else:
        env_vars = {
            'Parameters': {pascal_to_snake(key): value for key, value in outputs.get(stack_name).items()}
        }

    with NamedTemporaryFile('w') as env_file:
        env_file.write(dumps(env_vars))
        env_file.flush()

        command = [
            'sam',
            'local',
            'invoke',
            '-t',
            template_file.name,
            '-n',
            env_file.name,
            function_name,
        ]
        run(command)
