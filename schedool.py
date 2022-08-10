#!/usr/bin/python3

import random

people = [{"n": "Ali", "j": [0, 1, 2], "c": [2, 1, 0]},
          {"n": "Claire", "j": [1, 1, 7], "c": [6, 1, 2]},
          {"n": "Dale", "j": [2, 3, 6], "c": [3, 1, 2]},
          {"n": "Eric", "j": [5, 3, 6], "c": [7, 1, 2]},
          {"n": "Fred", "j": [4, 1, 4], "c": [4, 1, 2]},
          {"n": "George", "j": [5, 6, 3], "c": [7, 4, 1]},
          {"n": "Hollie", "j": [4, 5, 6], "c": [7, 3, 2]},
          {"n": "India", "j": [1, 6, 7], "c": [4, 7, 1]},
          {"n": "Jack", "j": [7, 2, 5], "c": [3, 7, 4]}]

PICKED_DATE_WEIGHT = 2
RANDOM_DATE_PENALTY = 2
SPACING_WEIGHT = 1
RUNS = 100000

num_people = len(people)

def allocate(group, k):
    randoms = 0
    picks = [0, 0, 0] # ASSUMPTION!!!
    allocation = [None] * len(group)
    allocation_score = 0
    random.shuffle(group)
    for p in group:
        allocated = False
        for index, d in enumerate(p[k]):
            if allocation[d] == None:
                allocation[d] = p['n']
                allocated = True
                allocation_score += PICKED_DATE_WEIGHT * (len(p[k]) - index)
                picks[index] += 1
                break
        if allocated == False:
            free_slot = allocation.index(None)
            allocation[free_slot] = p['n']
            allocation_score -= RANDOM_DATE_PENALTY
            randoms += 1
    return (allocation, allocation_score, picks, randoms)


best_allocation = [None] * num_people
best_allocation_score = 0

allocation = {'score': 0}
score = 0
for _ in range(RUNS):
    journal_allocation, journal_allocation_score, journal_picks, journal_randoms = allocate(people, 'j')
    if journal_allocation_score > best_allocation_score:
        best_allocation, best_allocation_score, best_picks, best_randoms = journal_allocation, journal_allocation_score, journal_picks, journal_randoms
    journal_allocation, journal_allocation_score, journal_picks, journal_randoms = best_allocation, best_allocation_score, best_picks, best_randoms

    best_allocation = [None] * num_people
    best_allocation_score = 0
    case_allocation, case_allocation_score, case_picks, case_randoms = allocate(people, 'c')
    if case_allocation_score > best_allocation_score:
        best_allocation, best_allocation_score, best_picks, best_randoms = case_allocation, case_allocation_score, case_picks, case_randoms
    case_allocation, case_allocation_score, case_picks, case_randoms = best_allocation, best_allocation_score, best_picks, best_randoms
    
    distribution_score = 0
    for p in people:
        distribution_score = SPACING_WEIGHT * (num_people/2 - abs((num_people/2) - abs(journal_allocation.index(p['n']) - case_allocation.index(p['n']))))

    score = journal_allocation_score + case_allocation_score + distribution_score
    if score > allocation['score']:
        allocation['c'] = case_allocation
        allocation['j'] = journal_allocation
        allocation['c_randoms'] = case_randoms
        allocation['c_picks'] = case_picks
        allocation['j_randoms'] = journal_randoms
        allocation['j_picks'] = journal_picks
        allocation['score'] = score
print(f"After {RUNS} runs best was {allocation}.")
