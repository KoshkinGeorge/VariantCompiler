from variant_compiler import VariantCompiler
import nbformat
import json
import os

class NbGenerator(VariantCompiler.IGenerator):
    def __init__(self, init_blocks=None):
        self.context = {}
        self.add_context(init_blocks)

    def clear_context(self):
        self.context = dict()

    def add_context(self, init_blocks):
        if init_blocks is None:
            return
        for init_block in init_blocks:
            exec(init_block, self.context)

    def run_code(self, code: str, result_var: str):
        self.context[result_var] = None
        try:
            exec(code, self.context)
        except NameError as ne:
            raise super().ContextError(f'Error code: \n\n{code}\n\n'
            'No such name in generator`s context\n' + str(ne))
        if self.context[result_var] is None:
            raise super().GenerationError(f'No \'{result_var}\' variable found in code:\n\n{code}\n\n')

    def generate(self, combinations, path, name, common):
        if common is not None:
            common = nbformat.read(common, as_version=4).cells

        counter = 1
        old_path = os.getcwd()
        if os.path.exists(path) and os.path.isdir(path):
            os.chdir(path)
        else:
            raise super().GenerationError("No such directory found: "
                        f"{path}")
        
        os.mkdir('./tasks')
        os.mkdir('./solutions')

        for combination in combinations:
            os.mkdir(f'./tasks/{counter}')
            os.mkdir(f'./solutions/{counter}')
            os.chdir(f'./tasks/{counter}')
            student_nb = nbformat.v4.new_notebook()
            teacher_nb = nbformat.v4.new_notebook()

            # inserting common part
            if common is not None:
                for cell in common:
                    student_nb.cells.append(cell)

            for i, task in enumerate(combination, 1):
                text = f'##Задание {i}\n'
                text += task.desc
                
                # generating unique parts for this task
                for gen in task.gens:
                    self.run_code(gen, 'generated')
                    
                    if hasattr(self.context['generated'], 'load'):
                        self.context['generated'].load()
                    else:
                        text += f'\n\n{self.context['generated']}'

                student_nb.cells.append(nbformat.v4.new_markdown_cell(source=text))
                student_nb.cells.append(nbformat.v4.new_code_cell(source=""))

                # generating solution
                self.run_code(task.solution, 'solution')
                text = f'##Задание {i}\n\n{self.context['solution']}'
                teacher_nb.cells.append(nbformat.v4.new_markdown_cell(source=text))
            
            with open(f'{name}.ipynb', 'w', encoding='utf-8') as outfile:
                json.dump(student_nb, outfile)
            os.chdir(f'../../solutions/{counter}')
            with open(f'{name}_solution.ipynb', 'w', encoding='utf-8') as outfile:
                json.dump(teacher_nb, outfile)
            os.chdir('../../')
            counter += 1
        os.chdir(old_path)

        