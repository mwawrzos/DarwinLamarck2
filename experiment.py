import os

from simulation.environment import Environment
from gen.logging import Stats
from gen.checkpoints import CheckpointManager


def summary_decorator(checkpoint, logger):
    def summary(foo):
        def wrapper(*args, **kwargs):
            ret = foo(*args, **kwargs)
            with open(os.path.join(checkpoint.checkpoint_dir, 'summary.txt'), 'w') as f:
                f.write(str(logger))

            return ret

        return wrapper
    return summary

class Experiment:
    def __init__(self, toolbox, epochs=50, checkpoint=None):
        self.environment = Environment()
        self.checkpoints = CheckpointManager(checkpoint)
        self.setup_toolbox(toolbox)
        self.epochs = epochs

        if self.checkpoints.last_epoch >= 0:
            self.load_state()
        else:
            self.init_state()

    def setup_toolbox(self, toolbox):
        self.toolbox = toolbox
        self.stats = Stats()
        self.toolbox.register('run_simulation', self.environment.run_simulation)
        self.toolbox.decorate('run_simulation', self.stats.log_decorator,
                                                self.checkpoints.save_decorator,
                                                summary_decorator(self.checkpoints, self.stats.logbook))

    def init_state(self):
        self.iteration = 0

        population, = self.toolbox.population()
        self.population, = self.toolbox.run_simulation(population, self.random_seed())

    def load_state(self):
        self.iteration   = self.checkpoints.last_epoch
        population, seed = self.checkpoints.load_epoch(self.iteration)

        self.population, = self.toolbox.run_simulation(population, seed)

    def run(self):
        while not self.finished():
            population, = self.toolbox.select(self.population)
            population, = self.toolbox.new_population(population)
            population, = self.toolbox.run_simulation(population, self.random_seed())

            self.update_results(population)

    def finished(self):
        return self.iteration >= self.epochs

    def update_results(self, population):
        self.iteration += 1
        self.population = population

    def random_seed(self):
        import datetime
        now = datetime.datetime.now()
        return now.microsecond
