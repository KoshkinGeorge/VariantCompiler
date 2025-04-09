from src.python.task_combiner import TaskCombiner
from src.python.variant_compiler import VariantCompiler
import pytest

Task = VariantCompiler.Task

tasks = [
    Task("task10", 1, []), # №00
    Task("task11", 1, []), # №01
    Task("task20", 2, []), # №02
    Task("task21", 2, []), # №03
    Task("task30", 3, []), # №04
    Task("task31", 3, []), # №05
    Task("task32", 3, []), # №06
    Task("task33", 3, []), # №07
    Task("task34", 3, []), # №08
    Task("task35", 3, []), # №09
    Task("task40", 4, []), # №10
    Task("task41", 4, []), # №11
    Task("task42", 4, []), # №12
    Task("task50", 5, []), # №13
    Task("task60", 6, []), # №14
    Task("task61", 6, []), # №15
]

class TestTaskCombiner:
    @pytest.fixture
    def full_combiner(self):
        combiner = TaskCombiner()
        initial_tasks = {
            1:  [0, 1, 4, 7],
            2:  [1, 3, 4, 5],
            3:  [8],
            4:  [5, 6],
            5:  [12, 14, 15],
            6:  [14, 15],
            7:  [15],
            8:  [],
            9:  [13, 14],
            10: [14]
        }
        for pos in initial_tasks:
            initial_tasks[pos] = [tasks[index] for index in initial_tasks[pos]]

        combiner.add_tasks(initial_tasks)
        combiner.update_comb()
        return combiner


    def test_add_tasks(self):
        # Arrange
        expected = {1: [tasks[0], tasks[2], tasks[4]],
                    2: [tasks[6], tasks[10], tasks[13]],
                    3: [tasks[14], tasks[15]]}
        combiner = TaskCombiner()

        # Act
        combiner.add_tasks(expected)

        # Assert
        assert combiner.tasks.items() == expected.items()

    def test_clear_tasks(self, full_combiner):
        # Arrange
        combiner = full_combiner
        combiner.tasks = {1: tasks[1]}

        # Act
        combiner.clear_tasks()

        # Assert
        assert combiner.tasks.items() == {}.items()
        assert combiner.atd == []
        assert combiner.comb == []

    @pytest.mark.manual
    def test_variant_dist(self, full_combiner):
        full_combiner.variant_dist(pos_count = 7)

    @pytest.mark.parametrize("min_diff, max_diff, pos_count, expected", [
        (10, 25, 7, 6),
        (0, 40, 6, 96),
        (0, 40, None, 0),
        (-690, -2346527, 7, 0),
        (26, 26, 7, 10),
        (26, 25, 7, 0),
        (10, 10, 6, 0)
    ])
    def test_variant_count(self, min_diff, max_diff, pos_count, expected, full_combiner):
        # Act
        ans = full_combiner.variant_count(min_diff, max_diff, pos_count)

        # Assert
        assert ans == expected
