
import random
from random import shuffle
import math

# Same data as before
picks = [
    {"n": "NAME 0", "j": [4, 4, 4], "c": [4, 4, 4]},
    {"n": "NAME 1", "j": [None, None, None], "c": [7, 6, 8]},
    {"n": "NAME 2", "j": [3, 6, 8], "c": [3, 6, 7]},
    {"n": "NAME 3", "j": [1, 2, 3], "c": [5, 6, 7]},
    {"n": "NAME 4", "j": [9, 6, 3], "c": [5, 6, 9]},
    {"n": "NAME 5", "j": [6, 5, 7], "c": [None, None, None]},
    {"n": "NAME 6", "j": [5, 3, 2], "c": [8, 9, 7]},
    {"n": "NAME 7", "j": [1, 3, 5], "c": [3, 5, 6]},
    {"n": "NAME 8", "j": [None, None, None], "c": [None, None, None]},
    {"n": "LD Conference", "j": [3, 3, 3], "c": [3, 3, 3]}
]

journal_dates = [{'n': e['n'], 'd': [d - 1 if d != None else None for d in e['j']]} for e in picks]
case_dates = [{'n': e['n'], 'd': [d - 1 if d!= None else None for d in e['c']]} for e in picks]
journal_prealloc = ['LD Conference']
case_prealloc = ['LD Conference']

PICKED_DATE_WEIGHT = 10
RANDOM_DATE_PENALTY = 10
MAX_PICKS = 3
MIN_SCORE = -1000
SPACING_WEIGHT = 1
RUNS = 100000
NUM_PEOPLE = len(picks)
NUM_DATES = 12

def rand_rank(group, pa):
    """
    Randomly shuffle the group, but preserve ``pa`` leading entries.

    Splits the group and shuffles only the tail.

    Patameters
    ----------
    group : [{'n': string, 'd': [int]}]
    pa : int

    Returns
    -------
    group : [{'n': string, 'd': [int]}]
    """
    pre_alloc = []
    alloc = []
    for person in group:
        if person['n'] in pa:
            pre_alloc.append(person)
        else:
            alloc.append(person)
    shuffle(alloc)
    return pre_alloc + alloc

def dist_lut(d):
    """
    A look up table for scoring the distribution

    Parameters
    ----------
    d : int

    Returns
    -------
    d : int
    """
    d = abs(d)
    if d == 0:
        return -10
    if d == 1:
        return -5
    if d == 2:
        return -3
    if (d >= 3) & (d < 6):
        return d
    return 6

def allocate(group):
    """
    Allocate people their chosen dates or a random one if not possible.

    Parameters
    ----------
    group : [{'n': string, 'd': [int]}]
    """
    randoms = 0
    picks = [0] * MAX_PICKS
    allocation = [None] * NUM_DATES
    allocation_score = 0
    random_allocations = []
    for p in group:
        allocated = False
        #print(p)
        for index, d in enumerate(p['d']):
            if d == None:
                break
            if allocation[d] == None:
                allocation[d] = p['n']
                allocated = True
                allocation_score += PICKED_DATE_WEIGHT * (len(p['d']) - index)
                picks[index] += 1
                break
        if allocated == False:
            random_allocations.append(p['n'])
            allocation_score -= RANDOM_DATE_PENALTY
            randoms += 1
    for name in random_allocations:
        free_slot = allocation.index(None)
        allocation[free_slot] = name
    return (allocation, allocation_score, picks, randoms)


def hill_climbing(init_state, energy_func, get_neighbor_func, iterations):
    state = init_state
    state_energy = energy_func(state)

    for _ in range(iterations):
        neighbor = get_neighbor_func(state)
        neighbor_energy = energy_func(neighbor)

        delta_energy = neighbor_energy - state_energy

        if delta_energy < 0:
            state, state_energy = neighbor, neighbor_energy

    return state, state_energy


def energy_func(schedule):
    journal_allocation, journal_allocation_score, _, _ = allocate(schedule[0])
    case_allocation, case_allocation_score, _, _ = allocate(schedule[1])

    distribution_score = 0
    for p in picks:
        distribution_score += dist_lut(journal_allocation.index(p['n']) - case_allocation.index(p['n']))

    return -(journal_allocation_score + case_allocation_score + distribution_score)


def get_neighbor_func(schedule):
    neighbor = [rand_rank(s, journal_prealloc) if i == 0 else rand_rank(s, case_prealloc) for i, s in enumerate(schedule)]
    return neighbor

init_state = [rand_rank(journal_dates, journal_prealloc), rand_rank(case_dates, case_prealloc)]

iterations = 100000

best_schedule, best_energy = hill_climbing(init_state, energy_func, get_neighbor_func, iterations)

journal_allocation, _, journal_picks, journal_randoms = allocate(best_schedule[0])
case_allocation, _, case_picks, case_randoms = allocate(best_schedule[1])

print(f"Best Energy: {best_energy}")
print("Journal Club Order")
for n in journal_allocation:
    print(n)
print("Case Presentation Order")
for n in case_allocation:
    print(n)
