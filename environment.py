import mesa
import mesa.time
import mesa.space
import mesa.model
import numpy as np
import itertools
import sys

from boids import SheepAgent, WolfAgent, Grass


def create_sheep(sheep, space):
    return (SheepAgent(s, space) for s in sheep)

def create_wolves(wolves, space):
    return (WolfAgent(w, space) for w in wolves)

def create_grass(count):
    return (Grass() for _ in range(count))

def create_populaiton(sheep, wolves, space):
    return itertools.chain(create_sheep(sheep, space),
                           create_wolves(wolves, space),
                           create_grass(count=200))


def extract_genes(population):
    return ([sheep.extract_genes() for sheep in population if type(sheep) == SheepAgent],
            [wolf.extract_genes()  for wolf  in population if type(wolf)  == WolfAgent])

class Environment:
    def __init__(self, max_iter=500):
        self.max_iter = max_iter

    def run_simulation(self, species, seed):
        model = self.prepare_model(species, seed)
        model.run_model()
        population = model.get_results()
        return extract_genes(population)

    def prepare_model(self, species, seed):
        model = Model(seed, self.max_iter)
        population = create_populaiton(*species, model.space)
        model.add_population(population)
        return model

class Model(mesa.model.Model):
    def __init__(self, seed, max_iter):
        super(Model, self).__init__(seed)
        self.iter = 0
        self.max_iter = max_iter

        self.schedule = mesa.time.SimultaneousActivation(self)
        self.space = mesa.space.ContinuousSpace(x_max=1, y_max=1, torus=True)

    def add_population(self, population):
        self.population = list(population)
        for agent in self.population:
            self.space.place_agent(agent, pos=np.random.rand(2))
            self.schedule.add(agent)

    def step(self):
        self.schedule.step()
        self.clean_up()
        self.update_results()
    
    def clean_up(self):
        agents_to_remove = [agent
                            for agent in self.schedule.agents
                            if  agent.energy <= 0]
        for agent in agents_to_remove:
            self.schedule.remove(agent)

    def update_results(self):
        self.iter += 1
        sys.stdout.write("\r%d" % self.iter,)
        sys.stdout.flush()
        self.running = self.iter <= self.max_iter

    def get_results(self):
        return self.population
