from variant_compiler import VariantCompiler
import re
import nbformat

class NbParser(VariantCompiler.IParser):
    def validate_cell(self, cell, expected_type="markdown", expected_pattern=None):
        if cell.cell_type != expected_type:
            raise super().ParseError(f"Expected cell type: {expected_type}\n"
                                f"Got: {cell.cell_type}")       
        if expected_pattern is not None:
            if not re.fullmatch(expected_pattern, cell.source):
                raise super().ParseError(f"The data in cell\n\n{cell.source}\n\n can`t be parsed, because it doesn`t match the predefined pattern") 
        return True

    def parse(self, *args, version=4):
        """
        Parses Task objects from the given Jupyter Notebook.

        Parameters
        ----------
        path : string or file-like object with read method
            notebook to parse

        version : int
            version of the notebook

        number_of_positions : int
            how many task there is going to be in one variant

        Returns
        -------
        dict
            the dictionary with lists of possible tasks, keyed by position

        See Also
        --------
        Task
        """
        
        initialization_blocks = []
        tasks = dict()
        for path in args:
            nb = nbformat.read(path, as_version=version)

            # parsing initialization blocks
            i = 0
            while i < len(nb.cells) and nb.cells[i].cell_type == 'code':
                initialization_blocks.append(nb.cells[i].source)
                i += 1

            # parsing tasks
            while i < len(nb.cells):
                #parsing description
                self.validate_cell(nb.cells[i], "markdown", r'([^:]*:)?([\s\S]*)')
                extracted = nb.cells[i].source
                if ':' in extracted:
                    extracted = ':'.join(nb.cells[i].source.split(':')[1:])
                desc = extracted.lstrip()
                i += 1

                # parsing task difficulty
                self.validate_cell(nb.cells[i], "markdown", r"([^:]*:)?\s*\d+\s*")
                extracted = nb.cells[i].source
                if ':' in extracted:
                    extracted = nb.cells[i].source.split(':')[-1]
                difficulty = int(extracted)
                i += 1

                # parsing task possible positions
                self.validate_cell(nb.cells[i], "markdown", 
                                   r"([^:]*:)?\s*\d+(,\s*\d+)*")
                extracted = nb.cells[i].source
                if ':' in extracted:
                    extracted = nb.cells[i].source.split(':')[-1]
                positions = [int(pos) for pos in extracted.split(',')]
                i += 1

                gens = []
                while i < len(nb.cells) and nb.cells[i].cell_type == "code":
                    gens.append(nb.cells[i].source)
                    i += 1

                if not gens:
                    raise super().ParseError(f'No solution generation code block found in task\n\n{desc}\n\n')
                
                solution = gens[-1]
                gens.pop()

                current = VariantCompiler.Task(desc, difficulty, gens, solution)
                for pos in positions:
                    if pos not in tasks:
                        tasks[pos] = list()
                    tasks[pos].append(current)
                    
        # for each position, the list of possible tasks (tasks[pos]) should
        # be sorted ascendingly by difficulty
        for pos in tasks:
            tasks[pos].sort(key=lambda task: task.difficulty)

        return (initialization_blocks, tasks)
