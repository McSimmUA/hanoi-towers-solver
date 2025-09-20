from functools import cache
from typing import NamedTuple, Set, List
from collections import deque

SolutionStep = NamedTuple('SolutionStep', [('disk_size', int), ('from_rod', int), ('to_rod', int)])

SplitResult = NamedTuple('SplitResult', [('min_steps', int), ('split', int)])


"""
    Solves initially arranged board (all disks are in the first rod)
    Parameters:
    - rods_num: int - number of rods
    - disks_num: int - number of disks
    Returns: list of solution steps to move the disks from the first rod to the last rod
    Each step is represented as a dict with keys:
    - disk_size: int - size of the disk being moved (0 is the smallest)
    - from_rod: int - index of the rod from which the disk is moved
    - to_rod: int - index of the rod to which the disk is moved
"""
def get_solution(rods_num: int, disks_num: int) -> List[SolutionStep]:

    # validate input
    if disks_num < 1:
        raise ValueError(f'disks_num must be at least 1, got {disks_num}')
    if rods_num < 2:
        raise ValueError(f'rods_num must be at least 2, got {rods_num}')
    
    # initial state
    rods_list: list[deque[int]] = [deque() for _ in range(0, rods_num)]
    # all disks are in the first rod, largest at the bottom, smallest at the top, which is the right side [-1] of the deque.
    rods_list[0] = deque([i for i in range(disks_num - 1, -1, -1)])
    # disks_locations: list[int] = disks_num * [0]
    solution: list[SolutionStep] = []
    

    """
        Helper: Moves disk from one rod to another, updating the rods_list, disks_locations and adding the step to the solution
    """
    def _move_disk(from_: int, to_: int) -> None:
        d: int = rods_list[from_].pop()
        solution.append(SolutionStep(disk_size=d, from_rod=from_, to_rod=to_))
        rods_list[to_].append(d)

    """
        Recursive function to solve the puzzle
        from_: int - index of the rod from which to move disks
        to_: int - index of the rod to which to move disks
        using_: Set[int] - set of indices of rods that could be used as intermediate
        disks_count: int - number of disks to move
    """
    def _solve_recursively(from_rod: int, to_rod: int, using: Set[int], disks_count: int) -> None:
        if disks_count == 0:
            return
        if len(using) == 0 and disks_count > 1:
            raise Exception(f'({rods_num=};{disks_num=}) - Not solvable, list of intermediate rods is empty')
        
        # trivial case: move one disk
        if disks_count == 1:
            _move_disk(from_rod, to_rod)
            return
        

        optimal_split: SplitResult = get_min_steps_and_split(rods=2 + len(using), disks=disks_count)
        if optimal_split.min_steps < 0:
            raise Exception(f'not solvable for {rods_num} rods and {disks_num} disks')

        intermediate_rod: int = using.pop()
        _solve_recursively(from_rod=from_rod, to_rod=intermediate_rod, using=using | {to_rod}, disks_count=optimal_split.split)
        _solve_recursively(from_rod=from_rod, to_rod=to_rod, using=using.copy(), disks_count=disks_count - optimal_split.split)
        _solve_recursively(from_rod=intermediate_rod, to_rod=to_rod, using=using | {from_rod}, disks_count=optimal_split.split)


    # set of indices of rods that could be used as intermediate
    using_rods: Set[int] = set(range(1, rods_num - 1))
    _solve_recursively(from_rod=0, to_rod=rods_num-1, using=using_rods, disks_count=disks_num)
    return solution


"""
    for given number of rods and disks calculates minimum number of steps required to solve the puzzle
    and the optimal split of disks into two groups (top and bottom)
    returns SplitResult(min_steps, split) or SplitResult(-1, 0) if there is no solution
"""
@cache
def get_min_steps_and_split(rods: int, disks: int) -> SplitResult:
    """
    the function results are cached as it significantly helps in this case
    returns (min_steps, split) or (-1, 0) if there is no solution
    """
    # not possible to solve for incorrect input
    if disks < 1 or rods < 2:
        return SplitResult(min_steps=-1, split=0)  # {'min_steps': -1, 'split': 0}

    # always possible to solve one disk case in one step
    if disks == 1:
        return SplitResult(min_steps=1, split=1)

    # not possible to solve when disks_count > 1 with only two rods
    if rods == 2:
        return SplitResult(min_steps=-1, split=0)  # {'min_steps': -1, 'split': 0}

    # when disks less than rods, the solution is trivial, no need to split
    if disks < rods:
        return SplitResult(min_steps=2 * disks - 1, split=1)  # {'min_steps': 2 * disks - 1, 'split': 0}

    # for 3-rods case the solution is classic
    if rods == 3:
        return SplitResult(min_steps=2 ** disks - 1, split=disks-1)  # {'min_steps': 2 ** disks - 1, 'split': 0}

    # more generals case requires recursive search
    split: int = 0
    min_steps: int = -1

    """
    For practical layouts this loop could start from 2 as it allows to skip search for zero splits. 
    I compared the cases up to 300 rods and 5*rods disks, and up to 200 rods and 10*rods disks:
    There is no case when 0 is the only optimal split, except trivial cases when disks < rods or rods == 3, which are handled separately
    However, I leave the classic loop starting from 1 for clarity, as the performance increase is small (~14%)
    """
    for d in range(1, disks):
        candidate_result_1 = get_min_steps_and_split(rods=rods, disks=d)
        candidate_result_2 = get_min_steps_and_split(rods=rods - 1, disks=disks - d)
        if candidate_result_1.min_steps < 1 or candidate_result_2.min_steps < 1:
            # no solution for this split
            continue
        # total amount of steps for this split would be
        steps_required: int = 2 * candidate_result_1.min_steps + candidate_result_2.min_steps
        if steps_required < min_steps or min_steps == -1:
            min_steps = steps_required
            split = d
            # finaly, this solution actually works. the order of processing groups is important,
            # so maximum 2 parts should be used in each iteration.
            # an example when the solution depends on the groups order:
            # (r=4, d=8): [[(2,), (2,)],(4,)] != [(2,), [(2,)],(4,)]
            # now split returns number of top disks in first part, or 0 if no splitting is necessary
            # (in previous solutions I tried to keep the list of splits and it didn't work

    return SplitResult(min_steps=min_steps, split=split)


def main():
    solution: List[SolutionStep] = get_solution(4, 8)
    print(f'Solution with {len(solution)} steps:')
    for step in solution:
        print(step)


if __name__ == "__main__":
    main()
