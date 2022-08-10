#!/usr/bin/python3

import random

people = [{"n": "Ali", "j": [0, 1, 2], "c": [2, 1, 0]},
          {"n": "Claire", "j": [2, 1, 7], "c": [6, 1, 2]},
          {"n": "Dale", "j": [2, 4, 6], "c": [3, 1, 2]},
          {"n": "Eric", "j": [3, 5, 6], "c": [7, 1, 2]},
          {"n": "Fred", "j": [2, 1, 4], "c": [4, 1, 2]},
          {"n": "George", "j": [4, 6, 3], "c": [7, 4, 1]},
          {"n": "Hollie", "j": [2, 4, 1], "c": [7, 3, 2]},
          {"n": "India", "j": [7, 1, 4], "c": [4, 7, 1]},
          {"n": "Jack", "j": [5, 1, 2], "c": [3, 7, 4]}
]

PICKED_DATE_WEIGHT = 2
RANDOM_DATE_PENALTY = 0
SPACING_WEIGHT = 1
RUNS = 100000

num_people = len(people)

def allocate(group, k):
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
                break
        if allocated == False:
            free_slot = allocation.index(None)
            allocation[free_slot] = p['n']
            allocation_score -= RANDOM_DATE_PENALTY
    return (allocation, allocation_score)


best_allocation = [None] * num_people
best_allocation_score = 0

allocation = {'c': [], 'd': []}
allocation_score = 0

for _ in range(RUNS):
    journal_allocation, journal_allocation_score = allocate(people, 'j')
    if journal_allocation_score > best_allocation_score:
        best_allocation = journal_allocation
        best_allocation_score = journal_allocation_score
journal_allocation = best_allocation
journal_allocation_score = best_allocation_score

best_allocation = [None] * num_people
best_allocation_score = 0
for _ in range(RUNS):
    case_allocation, case_allocation_score = allocate(people, 'c')
    if case_allocation_score > best_allocation_score:
        best_allocation = case_allocation
        best_allocation_score = case_allocation_score
case_allocation = best_allocation
case_allocation_score = best_allocation_score

distribution_score = 0
for p in people:
    distribution_score = SPACING_WEIGHT * (num_people/2 - abs((num_people/2) - abs(journal_allocation.index(p['n']) - case_allocation.index(p['n']))))

print(f"Allocation of journal club presentations complete with score {journal_allocation_score}, order is {journal_allocation}.")

print(f"Allocation of case presentations complete with score {case_allocation_score}, order is {case_allocation}.")

print(f"Total allocation score {case_allocation_score + journal_allocation_score + distribution_score}")
