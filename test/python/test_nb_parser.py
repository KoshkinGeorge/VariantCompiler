from src.python.nb_parser import NbParser
from src.python.variant_compiler import VariantCompiler
import nbformat

import pytest
from contextlib import nullcontext as does_not_raise


class TestNbParser:
    
    @pytest.mark.parametrize('index, type, pattern, verdict',
        [
            (0, 'markdown', r'.*', does_not_raise()),
            (0, 'code', r'.*', pytest.raises(Exception)),
            (0, 'markdown', r'\d\d:\d\d:\d\d', pytest.raises(Exception)),
            (1, 'code', None, does_not_raise()),
            (1, 'code', r'\d\d:\d\d:\d\d', pytest.raises(Exception)),
            (3, 'markdown', r'\d\d:\d\d:\d\d', does_not_raise())
        ])
    def test_validate_cell(self, index, type, pattern, verdict):
        # Arrange
        parser = NbParser()
        cells = nbformat.read(
            'test/notebooks/test_validate_cells.ipynb',
            as_version=4).cells
        
        # Assert
        with verdict:
            assert parser.validate_cell(cells[index], type, pattern)

    def test_parse_empty(self):
        # Arrange
        parser = NbParser()
        expected_init_blocks = []
        expected_tasks = dict()
        
        # Act
        init_blocks, tasks = parser.parse('test/notebooks/empty.ipynb')
        
        # Assert
        assert init_blocks == expected_init_blocks
        assert expected_tasks.items() == tasks.items()

    def test_parse_simple(self):
        # Arrange
        parser = NbParser()
        expected_init_blocks = []
        task1 = VariantCompiler.Task(
            desc='Just a simple **test notebook**',
            difficulty=7,
            gens = [
                'generated = 5',
                'generated = [[randint(1, 100) for i in range(3)] for j in range(4)]'
            ])
        task2 = VariantCompiler.Task(
            desc='The second task is to admit that you are a fool', 
            difficulty=100,
            gens = [
                'generated = [[randint(1, 100) for i in range(4)] for j in range(3)]',
                'generated = [[randint(1, 100) for i in range(4)] for j in range(4)]'
            ])
        expected_tasks = {
            1: [task1],
            2: [task2],
            3: [task2],
            4: [task2],
            5: [task1, task2], # expected to get this order, because the tasks are sorted in ascending order by difficulty
            6: [task1, task2],
            7: [task1],
            # 8 key is skipped since there is no task for 9 position in simple.ipynb
            9: [task2],
        }
        
        # Act
        init_blocks, tasks = parser.parse('test/notebooks/simple.ipynb')
        
        # Assert
        assert init_blocks == expected_init_blocks
        assert expected_tasks.items() == tasks.items()

    def test_parse_middle(self):
        # Arrange
        parser = NbParser()
        expected_init_blocks = [
            "print('That`s my first init block')",
            "print('Second init block')",
            "import random"
        ]
        task1 = VariantCompiler.Task(
            desc='Выведите матрицу размера N * M, заполненную нулями',
            difficulty=2,
            gens = [
                '# код, который генерирует N\nN = random.randint(1, 5)\ngenerated = f\'**N = {N}**\\n\'',
                '# код, который генерирует M\nM = random.randint(1, 5)\ngenerated = f\'**M = {M}**\\n\''
            ])
        task2 = VariantCompiler.Task(
            desc='Выведите матрицу размера N * M, у которой на главной диагонали стоят единицы',
            difficulty=2,
            gens = [
                '# код, который генерирует N\nN = random.randint(1, 5)\ngenerated = f\'**N = {N}**\\n\'',
                '# код, который генерирует M\nM = random.randint(1, 5)\ngenerated = f\'**M = {M}**\\n\''
            ])
        task3 = VariantCompiler.Task(
            desc='Выведите **диагональную матрицу** размера N * N, у которой на диагонали расставлены числа от 1 до N в возрастающем порядке',
            difficulty=3,
            gens = [
                '# код, который генерирует N\nN = random.randint(1, 5)\ngenerated = f\'**N = {N}**\\n\''
            ])
        expected_tasks = {
            1: [task1, task2, task3],
        }
        
        # Act
        init_blocks, tasks = parser.parse('test/notebooks/middle.ipynb')
        
        # Assert
        assert init_blocks == expected_init_blocks
        assert expected_tasks.items() == tasks.items()

    def test_multiple(self):
        # Arrange
        parser = NbParser()
        task1 = VariantCompiler.Task(
            desc='Just a simple **test notebook**',
            difficulty=7,
            gens = [
                'generated = 5',
                'generated = [[randint(1, 100) for i in range(3)] for j in range(4)]'
            ])
        task2 = VariantCompiler.Task(
            desc='The second task is to admit that you are a fool', 
            difficulty=100,
            gens = [
                'generated = [[randint(1, 100) for i in range(4)] for j in range(3)]',
                'generated = [[randint(1, 100) for i in range(4)] for j in range(4)]'
            ])
        task3 = VariantCompiler.Task(
            desc='Выведите матрицу размера N * M, заполненную нулями',
            difficulty=2,
            gens = [
                '# код, который генерирует N\nN = random.randint(1, 5)\ngenerated = f\'**N = {N}**\\n\'',
                '# код, который генерирует M\nM = random.randint(1, 5)\ngenerated = f\'**M = {M}**\\n\''
            ])
        task4 = VariantCompiler.Task(
            desc='Выведите матрицу размера N * M, у которой на главной диагонали стоят единицы',
            difficulty=2,
            gens = [
                '# код, который генерирует N\nN = random.randint(1, 5)\ngenerated = f\'**N = {N}**\\n\'',
                '# код, который генерирует M\nM = random.randint(1, 5)\ngenerated = f\'**M = {M}**\\n\''
            ])
        task5 = VariantCompiler.Task(
            desc='Выведите **диагональную матрицу** размера N * N, у которой на диагонали расставлены числа от 1 до N в возрастающем порядке',
            difficulty=3,
            gens = [
                '# код, который генерирует N\nN = random.randint(1, 5)\ngenerated = f\'**N = {N}**\\n\''
            ])
        expected_tasks = {
            1: [task3, task4, task5, task1],
            2: [task2],
            3: [task2],
            4: [task2],
            5: [task1, task2], # expected to get this order, because the tasks are sorted in ascending order by difficulty
            6: [task1, task2],
            7: [task1],
            # 8 key is skipped since there is no task for 9 position in simple.ipynb
            9: [task2],
        }
        expected_init_blocks = [
            "print('That`s my first init block')",
            "print('Second init block')",
            "import random"
        ]
        
        # Act
        init_blocks, tasks = parser.parse(
            'test/notebooks/simple.ipynb', 
            'test/notebooks/middle.ipynb',
            version=4)

        # Assert
        assert expected_init_blocks == init_blocks
        assert expected_tasks.items() == tasks.items()
