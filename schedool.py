#!/usr/bin/python3

from random import shuffle
from functools import reduce

picks = [
    {"n": "NAME 0","j":[11,10,12],"c":[3,3,3]},
    {"n": "NAME 1", "j": [4,4,4], "c": [4,4,4]},
    {"n": "NAME 2", "j": [None ,None,None], "c": [7,6,8]},
    {"n": "NAME 3","j":[3,6,8],"c":[3,6,7]},
    {"n": "NAME 4","j":[1,2,3],"c":[5,6,7]},
    {"n": "NAME 5", "j":[9,6,3],"c":[5,6,9]},
    {"n": "NAME 6","j":[6,5,7],"c":[None,None,None]},
    {"n": "NAME 7","j":[5,3,2],"c":[8,9,7]},
    {"n": "NAME 8","j":[1,3,5],"c":[3,5,6]},
    {"n": "NAME 9","j":[None,None,None],"c":[None,None,None]}
]

journal_dates = [{'n': e['n'], 'd': [d - 1 if d != None else None for d in e['j']]} for e in picks]
case_dates = [{'n': e['n'], 'd': [d - 1 if d!= None else None for d in e['c']]} for e in picks]
journal_prealloc = ['LD Conference']
case_prealloc = ['LD Conference', 'Amina Rawat']

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
    shuffle(group)
    return group
#    print(group)
    new_rank = group[:]
    randoms = new_rank[pa:]
    shuffle(randoms)
    prealloc = new_rank[:pa]
    return prealloc.append(randoms)

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
    if group == None:
        group = []
    random_allocations = []
    for p in group:
        allocated = False
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
#            free_slot = allocation.index(None)
#            allocation[free_slot] = p['n']
            random_allocations.append(p['n'])
            allocation_score -= RANDOM_DATE_PENALTY
            randoms += 1
    for name in random_allocations:
        free_slot = allocation.index(None)
        allocation[free_slot] = name
    return (allocation, allocation_score, picks, randoms)

best_allocation = [None] * NUM_DATES
best_allocation_score = MIN_SCORE

allocation = {'score': MIN_SCORE, 'pre-allocated': journal_prealloc + case_prealloc}
score = MIN_SCORE
for _ in range(RUNS):
    journal_ranking = rand_rank(journal_dates, journal_prealloc)
    journal_allocation, journal_allocation_score, journal_picks, journal_randoms = allocate(journal_ranking)
#    print(journal_ranking, journal_allocation)
    if journal_allocation_score > best_allocation_score:
        best_allocation, best_allocation_score, best_picks, best_randoms = journal_allocation, journal_allocation_score, journal_picks, journal_randoms
    journal_allocation, journal_allocation_score, journal_picks, journal_randoms = best_allocation, best_allocation_score, best_picks, best_randoms
    
    case_ranking = rand_rank(case_dates, case_prealloc)
    best_allocation_score = MIN_SCORE
    case_allocation, case_allocation_score, case_picks, case_randoms = allocate(case_ranking)
    if case_allocation_score > best_allocation_score:
        best_allocation, best_allocation_score, best_picks, best_randoms = case_allocation, case_allocation_score, case_picks, case_randoms
    case_allocation, case_allocation_score, case_picks, case_randoms = best_allocation, best_allocation_score, best_picks, best_randoms
    
    distribution_score = MIN_SCORE
    for p in picks:
        distribution_score = dist_lut(journal_allocation.index(p['n']) - case_allocation.index(p['n']))
#        distribution_score = SPACING_WEIGHT * (num_people/2 - abs((num_people/2) - abs(journal_allocation.index(p['n']) - case_allocation.index(p['n']))))
    score = journal_allocation_score + case_allocation_score + distribution_score
    if score > allocation['score']:
        allocation['j'] = journal_allocation
        allocation['j_randoms'] = journal_randoms
        allocation['j_picks'] = journal_picks
        allocation['c'] = case_allocation
        allocation['c_randoms'] = case_randoms
        allocation['c_picks'] = case_picks
        allocation['score'] = score
print(f"After {RUNS} runs best was {allocation}.")
print("Journal Club Order")
for n in allocation['j']:
    print(n)
print("Case Presentation Order")
for n in allocation['c']:
    print(n)
