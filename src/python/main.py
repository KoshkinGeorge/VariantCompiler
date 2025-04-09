from variant_compiler import VariantCompiler
from nb_generator import NbGenerator
from nb_parser import NbParser
from task_combiner import TaskCombiner
import os
import datetime

class UnknownCommand(Exception):
    pass

if __name__ == '__main__':
    compiler = VariantCompiler(
        generator = NbGenerator(),
        parser = NbParser(),
        combiner = TaskCombiner()
    )

    while (command := input(">>> ").split()) != ['quit']:
        args = {'unkeyed': []}
        for arg in command[1:]:
            if '=' not in arg:
                args['unkeyed'].append(arg)
                continue
            key, value = arg.split('=')
            args[key] = value


        match command[0]:
            case 'add':
                version = args['--version'] if '--version' in args else 4
                path = [args['--path']] if '--path' in args else args['unkeyed']
                compiler.add_tasks(*path, version=version)
            
            case 'clear':
                compiler.clear_tasks()

            case 'hist':
                variant_size = int(args['--positions']) if '--positions' in args else None 
                compiler.hist(variant_size)

            case 'generate':
                amount = int(args['--amount']) if '--amount' in args else 1
                min_diff = int(args['--min_diff']) if '--min_diff' in args else None
                max_diff = int(args['--max_diff']) if '--max_diff' in args else None
                positions = int(args['--positions']) if '--positions' in args else None
                name = args['--name'] if '--name' in args else 'hometask'
                common = args['--common'] if '--common' in args else None
                if '--path' not in args:
                    now = datetime.datetime.now()
                    dirname = f'{now.date()}---{now.hour}-{now.minute}-{now.second}'
                    os.mkdir(dirname)
                    path = dirname
                else:
                    path = args['--path']
                compiler.generate(amount, min_diff, max_diff, positions, path, name, common)

            case _:
                raise UnknownCommand(f"No such command: {' '.join(command)}")
