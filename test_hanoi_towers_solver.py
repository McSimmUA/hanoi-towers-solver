from unittest import TestCase
from typing import Tuple, List
from hanoi_towers_solver import *


class Test(TestCase):

    test_cases: Tuple[Tuple[int, int, Tuple[int, int]], ...] = (
        (1, 3, (-1, 0)),
        (2, 1, (1, 1)),
        (3, 1, (1, 1)), (3, 2, (3, 1)), (3, 8, (255, 7)),
        (4, 2, (3, 1)), (4, 4, (9, 1)), (4, 5, (13, 2)), (4, 8, (33, 4)),
        (5, 5, (11, 1)), (5, 8, (23, 2)), (5, 12, (47, 4)),
        (7, 14, (43, 1)),
        (10, 25, (81, 1)),
        (12, 12, (25, 1)),
        (13, 25, (75, 1)),
        (19, 19, (39, 1))
    )

    # @unittest.skip("Temporarily disabled because various approaches may give different splits")
    # Testing both min_steps and split to ensure that the optimal solution is found
    def test_get_min_steps_and_split(self):
        for rods, disks, expected in self.test_cases:
            optimal_result = get_min_steps_and_split(rods, disks)
            self.assertEqual((optimal_result.min_steps, optimal_result.split), expected, msg=f'{(rods, disks)=}')

    #testing only min_steps to allow any split that gives the optimal solution
    def test_get_min_steps_ignoring_split(self):
        for rods, disks, (min_steps, _) in self.test_cases:
            optimal_result = get_min_steps_and_split(rods, disks)
            self.assertEqual(optimal_result.min_steps, min_steps, msg=f'{rods, disks=}')

    def test_get_solution(self):
        for rods, disks, (min_steps, _) in self.test_cases:
            if min_steps < 0:
                with self.assertRaises(Exception, msg=f'not solvable for {rods} rods and {disks} disks'):
                    get_solution(rods, disks)
            else:
                solution: list[SolutionStep] = get_solution(rods, disks)
                self.assertEqual(len(solution), min_steps,
                                 msg=f'Incorrect number of steps {len(solution)} for {rods=}, {disks=}')
                test_rods: List[List[int]] = [list() for _ in range(rods)]
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
        print('Cache usage:', get_min_steps_and_split.cache_info())
