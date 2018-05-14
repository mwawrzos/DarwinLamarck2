from simulation.environment import Environment
from gen.logging import Stats

class Experiment:
    def __init__(self, toolbox, epochs=50, checkpoint=None):
        self.environment = Environment()
        self.setup_toolbox(toolbox)
        self.epochs = epochs

        if checkpoint:
            self.load_state(checkpoint)
        else:
            self.init_state()

    def setup_toolbox(self, toolbox):
        self.toolbox = toolbox
        self.stats = Stats()
        self.toolbox.register('run_simulation', self.environment.run_simulation)
        self.toolbox.decorate('run_simulation', self.stats.log_decorator)

    def init_state(self):
        self.iteration = 0

        population, = self.toolbox.population()
        self.population, = self.toolbox.run_simulation(population, self.random_seed())

    def load_state(self, checkpoint):
        pass

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
