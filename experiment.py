from environment import Environment

class Experiment:
    def __init__(self, toolbox, epochs=500, checkpoint=None):
        self.environment = Environment()
        self.epochs = epochs

        if checkpoint:
            self.load_state(checkpoint)
        else:
            self.init_state()

    def init_state(self):
        self.iteration = 0
        
        population, = self.toolbox.population()
        self.population, = self.environment.run_simulation(population, self.random_seed())

    def load_state(self, checkpoint):
        pass

    def run(self):
        while not self.finished():
            population, = self.toolbox.select(self.population)
            population, = self.toolbox.new_population(population)
            population, = self.environment.run_simulation(population, self.random_seed())

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
