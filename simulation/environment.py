import mesa
import mesa.time
import mesa.model
from simulation import space
import numpy as np
import itertools
import sys

from simulation.boids import SheepAgent, WolfAgent, Grass


def create_sheep(sheep, space):
    return (SheepAgent(s, space) for s in sheep)

def create_wolves(wolves, space):
    return (WolfAgent(w, space) for w in wolves)

def create_grass(count):
    return (Grass() for _ in range(count))

def create_population(sheep, wolves, space):
    return itertools.chain(create_sheep(sheep, space),
                           create_wolves(wolves, space),
                           create_grass(count=200))


def update_species(species, population):
    sheep, wolves = species

    for i, s_agent in enumerate(population[:len(sheep)]):
        sheep[i][:] = s_agent.extract_genes()
        sheep[i].fitness.values = s_agent.eaten, s_agent.energy

    for i, w_agent in enumerate(population[len(sheep):len(sheep)+len(wolves)]):
        wolves[i][:] = w_agent.extract_genes()
        wolves[i].fitness.values = w_agent.eaten, w_agent.energy

    return sheep, wolves

class Environment:
    def __init__(self, steps=500):
        self.steps = steps

    def run_simulation(self, species, seed):
        model = self.prepare_model(species, seed)
        model.run_model()
        population = model.get_results()
        return update_species(species, population),

    def prepare_model(self, species, seed):
        model = Model(seed, self.steps)
        population = create_population(*species, model.space)
        model.add_population(population)
        return model

class Model(mesa.model.Model):
    def __init__(self, seed, steps):
        super(Model, self).__init__(seed)
        self.iter = 0
        self.steps = steps

        self.schedule = mesa.time.SimultaneousActivation(self)
        self.space = space.CachedSpace()

    def add_population(self, population):
        self.population = list(population)
        for agent in self.population:
            self.space.place_agent(agent, pos=np.random.rand(2))
            if agent.energy > 0:
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
        self.running = self.iter <= self.steps

    def get_results(self):
        return self.population
