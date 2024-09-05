from functools import cache
from typing import TypedDict, NamedTuple

Disk = TypedDict('Disk', {'size': int, 'rode': int})

SolutionStep = NamedTuple('SolutionStep', [('disk_size', int), ('from_rode', int), ('to_rode', int)])

SplitResult = NamedTuple('SplitResult', [('min_steps', int), ('split', int)])


def hanoi_get_solution(rods: int | list[int], disks: int | list[Disk]) -> list[SolutionStep]:
    """
    returns list of steps to solve particular board (rods, disks)
    """
    rods_list: list[int]
    disks_list: list[Disk]
    solution: list[SolutionStep]

    def move_disk_to(disk: Disk, to_: int) -> None:
        """
        Changes position of the disk and add solution step to the solution
        """
        # solution.append({'disk_size': disk['size'], 'from_rode': disk['rode'], 'to_rode': to_})
        solution.append(SolutionStep(disk_size=disk['size'], from_rode=disk['rode'], to_rode=to_))
        disk['rode'] = to_

    def get_smallest_disk(rode: int) -> Disk | None:
        rode_disks = filter(lambda a: a['rode'] == rode, disks_list)
        return min(rode_disks, default=None, key=lambda a: a['size'])

    def trivial_solve_recursively(disks_count: int, from_: int, to_: int, using_: list[int]) -> None:
        """
        This recursion solves trivial cases :
        - when there are more rods than disks, so no stacking is needed
        - when only three rodes are involved, so no disk grouping is needed
        """
        if len(using_) == 0 and disks_count > 1:
            raise Exception('Not solvable, list of intermediate rods is empty')
        if disks_count <= len(using_) + 1:
            tmp_disks: list[Disk] = []
            for i in range(disks_count - 1):
                d: Disk = get_smallest_disk(from_)
                move_disk_to(d, using_[i])
                tmp_disks.append(d)
            move_disk_to(get_smallest_disk(from_), to_)
            while len(tmp_disks) > 0:
                move_disk_to(tmp_disks.pop(), to_)
        else:
            trivial_solve_recursively(disks_count - 1, from_, using_[0], [to_, ])
            move_disk_to(get_smallest_disk(from_), to_)
            trivial_solve_recursively(disks_count - 1, using_[0], to_, [from_, ])

    def find_intermediate_rods(for_disk: Disk, exclude_last: bool = False) -> list[int]:
        """
        returns list of rods that could be used as intermediate
        """
        intermediate_rods: list[int] = []
        for r in rods_list:
            d = get_smallest_disk(r)
            if d is None or d['size'] > for_disk['size']:
                intermediate_rods.append(r)
        if exclude_last:
            del intermediate_rods[-1]
        return intermediate_rods

    if type(rods) is int:
        rods_list = list(range(rods))
    elif type(rods) is list:
        rods_list = rods
    else:
        raise ValueError(f'type int or list[int] is expected for the parameter {rods=}, got {type(rods)} instead')

    if type(disks) is int:
        disks_list = [{'rode': rods_list[0], 'size': i} for i in range(disks)]
    elif type(disks) is list:
        disks_list = disks
    else:
        raise ValueError(f'type int or list[Disk] is expected for the parameter {disks=}, got {type(disks)} instead')

    solution = []
    from_rode: int = rods_list[0]
    to_rode: int = rods_list[-1]
    using_rodes: list[int] = rods_list[1:-1]

    optimal_result = calc_min_steps_and_split(rods=len(rods_list), disks=len(disks_list))
    if optimal_result.min_steps < 0:
        raise Exception(f'not solvable for {len(rods_list)} rods and {len(disks_list)} disks')
    if optimal_result.split == 0:
        trivial_solve_recursively(len(disks_list), from_rode, to_rode, using_rodes)
    else:
        d1: list[Disk] = disks_list[:optimal_result.split]
        d2: list[Disk] = disks_list[optimal_result.split:]

        rods: list[int] = [from_rode, to_rode] + find_intermediate_rods(d1[-1], True)
        first_target_rode: int = rods[-1]
        solution.extend(hanoi_get_solution(rods, d1))

        rods = [from_rode] + find_intermediate_rods(d2[-1])
        solution.extend(hanoi_get_solution(rods, d2))

        rods = [first_target_rode] + find_intermediate_rods(d1[-1])
        solution.extend(hanoi_get_solution(rods, d1))

    return solution


@cache
def calc_min_steps_and_split(rods: int, disks: int) -> SplitResult:
    """
    the function results are cached as it significantly helps in this case
    returns (min_steps, split) or (-1, 0) if there is no solution
    """
    # not possible to solve for incorrect input
    if disks < 1 or rods < 2:
        return SplitResult(min_steps=-1, split=0)  # {'min_steps': -1, 'split': 0}

    # always possible to solve one disk case in one step
    if disks == 1:
        return SplitResult(min_steps=1, split=0)

    # not possible to solve when disks_count > 1 with only two rods
    if rods == 2:
        return SplitResult(min_steps=-1, split=0)  # {'min_steps': -1, 'split': 0}

    # when disks less than rods, the solution is trivial, no need to split
    if disks < rods:
        return SplitResult(min_steps=2 * disks - 1, split=0)  # {'min_steps': 2 * disks - 1, 'split': 0}

    # for 3-rods case the solution is classic
    if rods == 3:
        return SplitResult(min_steps=2 ** disks - 1, split=0)  # {'min_steps': 2 ** disks - 1, 'split': 0}

    # more generals case requires recursive search
    split: int = 0
    min_steps: int = -1
    for d in range(2, disks):
        candidate_result_1 = calc_min_steps_and_split(rods=rods, disks=d)
        candidate_result_2 = calc_min_steps_and_split(rods=rods - 1, disks=disks - d)
        if candidate_result_1.min_steps < 1 or candidate_result_2.min_steps < 1:
            # no solution for this split
            continue
        # total amount of steps for this split would be
        steps_required: int = 2 * candidate_result_1.min_steps + candidate_result_2.min_steps
        if steps_required < min_steps or min_steps == -1:
            min_steps = steps_required
            split = d
            # this solution actually works. the order of processing groups is important,
            # so maximum 2 parts should be used in each iteration.
            # an example when the solution depends on the groups order:
            # (r=4, d=8): [[(2,), (2,)],(4,)] != [(2,), [(2,)],(4,)]
            # now split returns number of top disks in first part, or 0 if no splitting is necessary
            # (in previous solutions I tried to keep the list of splits and it didn't work

    return SplitResult(min_steps=min_steps, split=split)


def main():
    ...


if __name__ == "__main__":
    main()
