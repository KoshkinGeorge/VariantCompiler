from src.python.nb_generator import NbGenerator
from src.python.variant_compiler import VariantCompiler
import nbformat

import pytest
from contextlib import nullcontext as does_not_raise


class TestNbGenerator:
    def test_clear_context(self):
        # Arrange
        generator = NbGenerator()
        generator.context = {'name': 123}

        #Act
        generator.clear_context()

        #Assert
        assert generator.context == dict()

    @pytest.mark.parametrize('init_blocks, expected_context', [
        (['a=5'], {'a': 5}),
        (['b=10', 'a=15'], {'a': 15, 'b': 10}),
        (['a=5', 'b=10', 'a=15'], {'a': 15, 'b': 10})
    ])
    def test_add_context(self, init_blocks, expected_context):
        # Arrange
        generator = NbGenerator()

        # Act
        generator.add_context(init_blocks)

        # Assert
        for var in expected_context:
            assert expected_context[var] == generator.context[var]

    @pytest.fixture(scope='session')
    def prepare_tasks(self):
        generator = NbGenerator()
        tasks = [None] * 5  
        tasks[0] = VariantCompiler.Task(
            desc = 'Выведите матрицу размера N * M, заполненную нулями',
            difficulty = 2,
            gens = ['generated = f"**N = {a // 2}**"', 'generated = f"**M = {b - 5}**"'], 
        )
        tasks[1] = VariantCompiler.Task(
            desc = 'Выведите матрицу размера N * M, у которой на главной диагонали стоят единицы',
            difficulty = 2,
            gens = ['generated = f\'**N = {c}**\\n\'', 'generated = f"**M = {c - b}**"']
        )
        tasks[2] = VariantCompiler.Task(
            desc = 'Выведите диагональную матрицу размера N * N, у которой на диагонали расставлены числа от 1 до N в возрастающем порядке',
            difficulty = 3,
            gens = ['generated = f"**N = {a}**\\n"']
        )
        tasks[3] = VariantCompiler.Task(
            desc = 'Some task',
            difficulty = 'Some difficulty',
            gens = ['Oh no, this is invalid python code']
        )
        tasks[4] = VariantCompiler.Task(
            desc = 'Some task',
            difficulty = 'Some difficulty',
            gens = ['# And here is a valid python code, but the \'generated\' var is not found\noutput = a + b + c']
        )
        return generator, tasks

    @pytest.mark.parametrize('context, combination, expected_nb, exception', [
        (dict(), [], 'test_generate1.ipynb', does_not_raise()),
        ({'a': 5, 'b': 10, 'c': 15}, [0, 1, 2], 'test_generate2.ipynb', does_not_raise()),
        (dict(), [0], 'test_generate1.ipynb', pytest.raises(Exception)),
        ({'a': 5, 'b': 10, 'c': 15}, [3], 'test_generate1.ipynb', pytest.raises(Exception)),
        ({'a': 5, 'b': 10, 'c': 15}, [4], 'test_generate1.ipynb', pytest.raises(Exception))
    ])
    def test_generate(self, prepare_tasks, context, combination, expected_nb, exception):
        # Arrange
        prepare_tasks[0].context = context
        expected_nb = nbformat.read(f'test/notebooks/{expected_nb}', as_version=4)

        # Act
        with exception:
            nb = prepare_tasks[0].generate([prepare_tasks[1][i] for i in    combination])

            # Assert
            assert len(nb.cells) == len(expected_nb.cells)
            for i in range(len(nb.cells)):
                assert nb.cells[i].cell_type == expected_nb.cells[i].cell_type
                assert nb.cells[i].source == expected_nb.cells[i].source