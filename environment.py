import mesa
import mesa.time
import mesa.space
import mesa.model
import numpy as np
import itertools

from boids import SheepAgent, WolfAgent


def create_sheep(sheep, space):
    return (SheepAgent(s, space) for s in sheep)


def create_wolves(wolves, space):
    return (WolfAgent(w, space) for w in wolves)


def create_populaiton(sheep, wolves, space):
    return itertools.chain(create_sheep(sheep, space),
                           create_wolves(wolves, space))


def extract_genes(population):
    return (population[:100], population[100:])

class Environment:
    def __init__(self, max_iter=500):
        self.max_iter = max_iter

    def run_simulation(self, species, seed):
        model = self.prepare_model(species, seed)
        model.run_model()
        population = model.get_results()
        return extract_genes(population)

    def prepare_model(self, species, seed):
        model = Model(self.max_iter, seed)
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
        for agent in population:
            self.space.place_agent(agent, agent.pos)
            self.schedule.add(agent)

    def step(self):
        self.schedule.step()
        self.update_results()

    def update_results(self):
        self.iter += 1
        self.running = self.iter <= self.max_iter

    def get_results(self):
        return self.schedule.agents
