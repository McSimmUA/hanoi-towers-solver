from unittest import TestCase
from hanoi_towers_solver import *


class Test(TestCase):
    test_cases = (
        (1, 3, (-1, 0)),
        (2, 1, (1, 0)),
        (3, 1, (1, 0)), (3, 2, (3, 0)), (3, 8, (255, 0)),
        (4, 2, (3, 0)), (4, 4, (9, 2)), (4, 5, (13, 2)), (4, 8, (33, 4)),
        (5, 5, (11, 2)), (5, 8, (23, 2)), (5, 12, (47, 4)),
        (7, 14, (43, 2)),
        (10, 25, (81, 2)),
        (12, 12, (25, 2)),
        (13, 25, (75, 2)),
        (19, 19, (39, 2))
    )

    def test_calc_min_steps_and_split(self):
        for rods, disks, expected in self.test_cases:
            optimal_result = calc_min_steps_and_split(rods, disks)
            self.assertEqual((optimal_result.min_steps, optimal_result.split), expected, msg=f'{rods, disks=}')

    def test_hanoi_get_solution(self):
        for rods, disks, (min_steps, _) in self.test_cases:
            if min_steps < 0:
                with self.assertRaises(Exception, msg=f'not solvable for {rods} rods and {disks} disks'):
                    hanoi_get_solution(rods, disks)
            else:
                solution: list[SolutionStep] = hanoi_get_solution(rods, disks)
                self.assertEqual(len(solution), min_steps,
                                 msg=f'Incorrect number of steps {len(solution)} for {rods=}, {disks=}')
                test_rods = [[] for _ in range(rods)]
                test_rods[0] = list(range(disks))
                for disk, from_, to_ in solution:
                    # disk, from_, to_ = solution_step.disk_size, solution_step.from_rode, solution_step.to_rode
                    self.assertIn(disk, test_rods[from_],
                                  msg=f'[{rods=},{disks=}]: moving absent disk {disk} from the rode {from_}')
                    self.assertGreater(min(test_rods[to_] + [disk + 1]), disk,
                                       msg=f'[{rods=},{disks=}]: moving {disk=} on a smaller disk on the rode {to_}')
                    test_rods[from_].remove(disk)
                    test_rods[to_].append(disk)
                self.assertEqual(len(test_rods[-1]), disks,
                                 msg=f'[{rods=},{disks=}]: move is not completed, last rode is{test_rods[-1]}')

    @classmethod
    def tearDownClass(cls) -> None:
        print('Cache usage:', calc_min_steps_and_split.cache_info())
