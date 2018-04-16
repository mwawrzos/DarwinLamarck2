from environment import Environment

class Experiment:
    def __init__(self, toolbox, max_iter=500, checkpoint=None):
        self.toolbox = toolbox
        self.max_iter = max_iter

        if checkpoint:
            self.load_state(checkpoint)
        else:
            self.init_state()

    def init_state(self):
        self.iteration = 0
        self.environment = Environment()
        
        population = self.toolbox.population()
        self.population = self.environment.run_simulation(population, self.random_seed())

    def load_state(self, checkpoint):
        pass

    def run(self):
        while not self.finished():
            population = self.toolbox.select(self.population)
            population = self.toolbox.new_population(population)
            population = self.environment.run_simulation(population, self.random_seed())

            self.update_results(population)

    def finished(self):
        return self.iteration >= self.max_iter
            
    def update_results(self, population):
        self.iteration += 1
        self.population = population

    def random_seed(self):
        import datetime
        now = datetime.datetime.now()
        return now.microsecond
