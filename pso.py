from random import shuffle
import random
import copy

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


def energy_func(schedule):
    journal_allocation, journal_allocation_score, _, _ = allocate(schedule[0])
    case_allocation, case_allocation_score, _, _ = allocate(schedule[1])

    distribution_score = 0
    for p in picks:
        distribution_score += dist_lut(journal_allocation.index(p['n']) - case_allocation.index(p['n']))

    return -(journal_allocation_score + case_allocation_score + distribution_score)



# PSO parameters
num_particles = 30
num_iterations = 500
inertia_weight = 0.7
c1 = 2.0  # cognitive component
c2 = 2.0  # social component

def pso_schedule(schedule_data, energy_func, num_particles, num_iterations, inertia_weight, c1, c2):
    def random_particle(schedule_data):
        particle = [rand_rank(journal_dates, journal_prealloc), rand_rank(case_dates, case_prealloc)]
        for group in particle:
            for person in group:
                person['velocity'] = [random.uniform(-1, 1) for _ in range(len(person['d']))]
        return particle
    def update_velocity(particle, pbest, gbest, inertia_weight, c1, c2):
        for group_idx, group in enumerate(particle):
            for i, person in enumerate(group):
                for j in range(len(person['d'])):
                    inertia = inertia_weight * particle[group_idx][i]['velocity'][j]
                    cognitive = c1 * random.random() * (pbest[group_idx][i]['d'][j] - person['d'][j]) if pbest[group_idx][i]['d'][j] is not None and person['d'][j] is not None else 0
                    social = c2 * random.random() * (gbest[group_idx][i]['d'][j] - person['d'][j]) if gbest[group_idx][i]['d'][j] is not None and person['d'][j] is not None else 0
                    particle[group_idx][i]['velocity'][j] = inertia + cognitive + social

    def update_position(particle, schedule_data):
        for group_idx, group in enumerate(particle):
            for i, person in enumerate(group):
                for j in range(len(person['d'])):
                    if person['d'][j] is not None:
                        new_pos = person['d'][j] + person['velocity'][j]
                        if new_pos < 0:
                            new_pos = 0
                        elif new_pos >= len(schedule_data[group_idx]):
                            new_pos = len(schedule_data[group_idx]) - 1
                        person['d'][j] = schedule_data[group_idx][int(new_pos)]['d'][j]


    # Initialize particles
    particles = [random_particle(schedule_data) for _ in range(num_particles)]
    pbest_positions = copy.deepcopy(particles)
    pbest_fitnesses = [energy_func(p) for p in particles]
    gbest_position = min(pbest_positions, key=lambda x: energy_func(x))
    gbest_fitness = energy_func(gbest_position)

    for _ in range(num_iterations):
        for i, particle in enumerate(particles):
            update_velocity(particle, pbest_positions[i], gbest_position, inertia_weight, c1, c2)
            update_position(particle, schedule_data)

            # Update personal best
            fitness = energy_func(particle)
            if fitness < pbest_fitnesses[i]:
                pbest_positions[i] = copy.deepcopy(particle)
                pbest_fitnesses[i] = fitness

                # Update global best
                if fitness < gbest_fitness:
                    gbest_position = copy.deepcopy(particle)
                    gbest_fitness = fitness

    return gbest_position, gbest_fitness

best_schedule, best_energy = pso_schedule(
    [journal_dates, case_dates],
    energy_func,
    num_particles,
    num_iterations,
    inertia_weight,
    c1,
    c2
)

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
