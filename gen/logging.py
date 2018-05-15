from deap import tools
import numpy as np
import sys

def stats(specie_idx):
    def wrapper(pop):
        return [ind.fitness.values for ind in pop[specie_idx]]

    return wrapper

def alive(pop):
    return sum(ind[1] > 0 for ind in pop[0])

def debug(foo):
    def wrapper(*args, **kwargs):
        return foo(*args, **kwargs)
    return wrapper

class Stats:
    def __init__(self):
        s_stats = tools.Statistics(stats(0))
        w_stats = tools.Statistics(stats(1))
        self.stats = tools.MultiStatistics(sheep=s_stats, wolves=w_stats)
        self.stats.register('avg',    np.average)
        self.stats.register('min',    np.min)
        self.stats.register('median', np.median)
        self.stats.register('max',    np.max)
        self.stats.register('alive',  alive)
        self.stats.register('std',    np.std)

        self.logbook = tools.Logbook()
        self.logbook.header = 'gen', 'sheep', 'wolves'
        self.logbook.chapters['sheep'].header = 'std', 'min', 'median', 'avg', 'max', 'alive'
        self.logbook.chapters['wolves'].header = 'std', 'min', 'median', 'avg', 'max', 'alive'
        self.logbook.columns_len = [4, 33, 33]

        self.iteration = 0

    def log_decorator(self, foo):
        def wrapper(population, *args):
            population, = foo(population, *args)

            self.logbook.record(gen=self.iteration, **self.stats.compile([population]))
            self.iteration += 1
            sys.stdout.write("\r%s\n" % self.logbook.stream,)

            return population,

        return wrapper
