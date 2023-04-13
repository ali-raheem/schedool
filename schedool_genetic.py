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
POPULATION_SIZE = 100
NUM_GENERATIONS = 1000
NUM_PEOPLE = len(picks)
NUM_DATES = 12
MUTATION_RATE = 0.1
TOURNAMENT_SIZE = 5

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

def energy_func(schedule):
    journal_allocation, journal_allocation_score, _, _ = allocate(schedule[0])
    case_allocation, case_allocation_score, _, _ = allocate(schedule[1])

    distribution_score = 0
    for p in picks:
        distribution_score += dist_lut(journal_allocation.index(p['n']) - case_allocation.index(p['n']))

    return -(journal_allocation_score + case_allocation_score + distribution_score)

def mutate(schedule, mutation_rate):
    for s in schedule:
        if random.random() < mutation_rate:
            idx1, idx2 = random.sample(range(len(s)), 2)
            s[idx1], s[idx2] = s[idx2], s[idx1]
    return schedule

def crossover(parent1, parent2):
    index1 = random.randint(0, len(parent1) - 1)
    index2 = random.randint(index1, len(parent1))
    child1 = parent1[:index1] + parent2[index1:index2] + parent1[index2:]
    child2 = parent2[:index1] + parent1[index1:index2] + parent2[index2:]
    return child1, child2

def tournament_selection(population, tournament_size):
    selected = random.sample(population, tournament_size)
    selected.sort(key=lambda x: energy_func(x), reverse=True)
    return selected[0]

def genetic_algorithm(init_population, energy_func, mutation_rate, num_generations, tournament_size):
    population = init_population

    for _ in range(num_generations):
        new_population = []

        for _ in range(len(population) // 2):
            parent1 = tournament_selection(population, tournament_size)
            parent2 = tournament_selection(population, tournament_size)
            child1, child2 = crossover(parent1, parent2)

            child1 = mutate(child1, mutation_rate)
            child2 = mutate(child2, mutation_rate)

            new_population.append(child1)
            new_population.append(child2)

        population = new_population

    best_individual = min(population, key=energy_func)
    return best_individual, energy_func(best_individual)

# Create the initial population
init_population = [[rand_rank(journal_dates, journal_prealloc), rand_rank(case_dates, case_prealloc)] for _ in range(POPULATION_SIZE)]

# Run the Genetic Algorithm
best_schedule, best_energy = genetic_algorithm(init_population, energy_func, MUTATION_RATE, NUM_GENERATIONS, TOURNAMENT_SIZE)

# Output the results
journal_allocation, _, journal_picks, journal_randoms = allocate(best_schedule[0])
case_allocation, _, case_picks, case_randoms = allocate(best_schedule[1])

print(best_energy)
print("Journal Club Order")
for n in journal_allocation:
    print(n)
print("Case Presentation Order")
for n in case_allocation:
    print(n)
