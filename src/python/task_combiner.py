import matplotlib.pyplot as plt
from variant_compiler import VariantCompiler
import random

class TaskCombiner(VariantCompiler.ITaskCombiner):
    def __init__(self):
        self.tasks = dict()
        # self.comb - table used for all possible combinations calculation
        # Row indices = amount of positions we can use for variant compiling
        # Column indices = accumulative difficulty of the whole variant
        # self.comb[N][M] - list of all possible task
        # combinations, which use only N first positions and have M difficulty
        # in total
        self.comb = []
        self.comb_updated = True
        self.max_difficulty = 0
        self.max_pos = 0

    def add_tasks(self, new_tasks):
        for pos in new_tasks:
            if pos not in self.tasks:
                self.tasks[pos] = []
            self.tasks[pos] += new_tasks[pos]
            self.tasks[pos].sort(key=lambda task: task.difficulty)
        if new_tasks.items() != dict().items():
            self.comb_updated = False

    def clear_tasks(self):
        self.tasks = dict()
        self.comb = []
        self.comb_updated = True
        self.max_difficulty = 0
        self.max_pos = 0

    def update_comb(self):
        self.max_pos = max(self.tasks)
        self.max_difficulty = 0
        for possible_tasks in self.tasks.values():
            if possible_tasks != []:
                self.max_difficulty += possible_tasks[-1].difficulty
        self.comb = [[[] for diff_level in range(self.max_difficulty + 1)]
                for pos in range(self.max_pos + 1)]

        # for each difficulty level DL except 0, comb_matrix[0][DL] = []
        # for each number of positions NOP except 0, comb_matrix[NOP][0] = []
        self.comb[0][0].append([]) # only possible combination - the empty one

        # then let`s calculate further dynamic programming layers recursively
        # comb_matrix[i][j] = (comb_matrix[i-1][j - TD] for each task in self
        # tasks[i], where TD - Task Difficulty)
        for i in range(1, self.max_pos + 1): # i - availaible_positions
            for j in range(1, self.max_difficulty + 1): # j - total_difficulty
                if i not in self.tasks:
                    continue
                for candidate in self.tasks[i]:
                    for comb in self.comb[i-1][j - candidate.difficulty]:
                        if candidate not in comb:
                            self.comb[i][j].append(comb + [candidate])

        with open('output/out.txt', 'w', encoding='utf-8') as out:
            for pos in self.comb:
                print(f'{[len(a) for a in pos]}\n\n', file=out)

        self.comb_updated = True

    def variant_hist(self, pos_count=None):
        if not self.comb_updated:
            self.update_comb()
        if pos_count is None:
            pos_count = self.max_pos

        dist = []
        if self.comb:
            dist = [len(self.comb[pos_count][d]) for d in range(self.max_difficulty + 1)]
        dist.append(0)

        start = end = None
        for i in range(self.max_difficulty + 1):
            if dist[i] != 0 and start is None:
                start = i
            if dist[-1-i] != 0 and end is None:
                end = self.max_difficulty + 1 - i
        if start is None:
            start = 0
        if end is None:
            end = self.max_difficulty

        plt.bar(range(start - 1, end + 1), dist[start - 1:end + 1])
        plt.show()

    def variant_count(self, min_diff, max_diff, pos_count=None):
        if not self.comb_updated:
            self.update_comb()
        if min_diff is None:
            min_diff = 0
        if max_diff is None:
            max_diff = self.max_difficulty
        if pos_count is None:
            pos_count = self.max_pos
        return sum([len(self.comb[pos_count][d]) for d in 
                    range(min_diff, max_diff + 1)])

    def generate_random(self, n, min_diff, max_diff, pos_count=None):
        if not self.comb_updated:
            self.update_comb()
        if pos_count is None:
            pos_count = self.max_pos
        if min_diff is None:
            min_diff = 0
        if max_diff is None:
            max_diff = self.max_difficulty
        

        possible_diff = []
        for d in range(min_diff, max_diff + 1):
            if self.comb[pos_count][d] != []:
                possible_diff.append(d)

        if not possible_diff:
            raise super().NoPossibleCombination('Your rules are so strict,'
            ' that no combination satisfies them')       

        generated = []
        for i in range(n):
            diff = random.choice(possible_diff)
            picked = random.choice(self.comb[pos_count][diff])
            generated.append(picked)

        return generated
