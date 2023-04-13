# schedool

Optimizer for schedulling. Designed for a group of people to pick 3 dates each for two activities aiming for those dates to be about 6 months apart.

Reports order of schedule for each task, as well as how many got their first, second or third choice for each task and how many got random selection.

Can weight various aspects of the rating system.

## Versions
* Simulated annealing - Fastest in general, probably what you want.
* Random - Randomly shuffle brute force approach, single threaded.
* Hill climbing - meh.
* PSO - Particle Swarm Optimization - Not great.
* Genetic - Terrible.