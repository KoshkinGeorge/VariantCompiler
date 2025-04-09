class VariantCompiler:
    class Task:
        """
        Programm realization for abstract linear algebra task.
        """
        def __init__(self, desc: str, difficulty: int, gens, solution: str):
            self.desc = desc
            self.difficulty = difficulty
            self.gens = gens
            self.solution = solution

        def __eq__(self, other):
            return (self.desc == other.desc) and \
                   (self.difficulty == other.difficulty) and \
                   (self.gens == other.gens)

        def __repr__(self):
            return f'''\nDescription: {self.desc}\nDifficulty: {self.difficulty}\nGenerators:\n''' + '\n\n'.join(self.gens)

    class IParser:
        class ParseError(Exception):
            pass
        
        def parse(self, *args):
            pass

    class IGenerator:
        class GenerationError(Exception):
            pass

        class ContextError(GenerationError):
            pass

        def generate(self, combinations, path, name, common):
            pass

        def clear_context(self):
            pass

        def add_context(self, init_blocks):
            pass
    
    class ITaskCombiner:
        class NoPossibleCombination(Exception):
            pass

        def add_tasks(self, new_tasks):
            pass

        def clear_tasks(self):
            pass

        def variant_dist(self, pos_count):
            pass

        def variant_count(self, min_diff, max_diff, pos_count):
            pass

        def generate_random(self, n, min_diff, max_diff, pos_count):
            pass

    def __init__(self, parser, generator, combiner):
        self.parser = parser
        self.generator = generator
        self.combiner = combiner
        self.init_blocks = []
        self.start_codeblock = ''
        self.start_textblock = ''

    def add_tasks(self, *files, version=4):
        self.init_blocks, tasks = self.parser.parse(*files, version=version)
        self.combiner.add_tasks(tasks)

    def clear_tasks(self):
        self.init_blocks = []
        self.combiner.clear_tasks()

    def hist(self, pos_count=None):
        self.combiner.variant_hist(pos_count)

    def generate(self, n, min_diff, max_diff, pos_count, path, name, common):
        expected_outcome = self.combiner.variant_count(min_diff, max_diff, pos_count)
        ans = input(f'Min difficulty: {min_diff}\n'
                    f'Max difficulty: {max_diff}\n'
                    f'Number of positions: {pos_count}\n'
                    f'Number of possible variants: {expected_outcome}\n'
                    f'Requiered number: {n}\n'
                    f'Folder for generated variants: {path}\n'
                    f'Name for generated notebooks: {name}\n'
                    f'Are you sure you want to continue(Y/N)?\n').lower()
        if ans != 'y':
            return
        
        picked = self.combiner.generate_random(n, min_diff, max_diff, pos_count)
        self.generator.clear_context()
        self.generator.add_context(self.init_blocks)
        self.generator.generate(picked, path, name, common)
        print("Everything generated successfully!\n")
