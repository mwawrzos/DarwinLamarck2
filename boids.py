import numpy as np
import mesa
import random


def limit(val, low=0, high=1000):
    return max(low, min(high, val))

def score_agent_hunger(agent):
    return limit((agent.MAX_ENERGY - agent.energy) * agent.hunger_a + agent.hunger_b)

def filter_by_type(population, agentType):
    return (agent for agent in population if type(agent) is agentType)

def distance_to_closest(agent, poulation):
    return min((agent.space.get_distance(agent.pos, s.pos) for s in poulation),
               default=agent.VIEW_RANGE)

def avoidance_score(agent, neighbours):
    closest = distance_to_closest(agent, neighbours)
    return 1 - (closest / agent.VIEW_RANGE)

class Agent:
    VIEW_RANGE = 0.1
    MAX_ENERGY = 200
    RADIUS = None

    def __init__(self, space : mesa.space.ContinuousSpace):
        self.space = space
        self.pos = random.random(), random.random()
        self.energy = self.MAX_ENERGY
        
    def step(self):
        neighbours = self.space.get_neighbors(self.pos, self.VIEW_RANGE, include_center=False)
        self.decision = self.make_deicision(neighbours)
    
    def advance(self):
        if self.valid_decision():
            self.v = self.decision.v
            self.pos = self.decision.pos
        self.energy = self.decision.cost
        if self.energy < self.MAX_ENERGY:
            self.find_food()
        self.penalty()
    
    def valid_decision(self):
        return not self.space.get_neighbors(self.decision.pos, self.RADIUS)

    def make_deicision(self, neighbours):
        decisions, weights = self.get_weighted_decisions(neighbours)
        return random.choices(decisions, weights)[0](neighbours)
    
    def find_food(self):
        pass

    def penalty(self):
        pass

    def get_weighted_decisions(self, neighbours):
        pass

class SheepAgent(Agent):
    def __init__(self, genes, space):
        super(SheepAgent, self).__init__(space)
        self.apply_genes(genes)

    def apply_genes(self, genes):
        (  self.hunger_a,   self.hunger_b,
             self.fear_a,     self.fear_b, self.fear_speed,
         self.coupling_a, self.coupling_b                 ) = genes

    def hunger(self, neighbours):
        pass

    def coupling(self, neighbours):
        pass

    def fear(self, neighbours):
        pass

    def score_hunger(self):
        return score_agent_hunger(self)

    def score_coupling(self, neighbours):
        sheep = filter_by_type(neighbours, SheepAgent)
        return avoidance_score(self, sheep)

    def score_fear(self, neighbours):
        wolves = filter_by_type(neighbours, WolfAgent)
        return avoidance_score(self, wolves)

    def get_weighted_decisions(self, ns):
        return ([self.hunger,         self.coupling,           self.fear],
                [self.score_hunger(), self.score_coupling(ns), self.score_fear(ns)])

class WolfAgent(Agent):
    def __init__(self, genes, space):
        super(WolfAgent, self).__init__(space)
        self.apply_genes(genes)

    def apply_genes(self, genes):
        (  self.hunger_a,   self.hunger_b, self.hunger_speed,
         self.coupling_a, self.coupling_b                   ) = genes

    def hunger(self, neighbours):
        pass

    def coupling(self, neighbours):
        pass

    def score_hunger(self):
        return score_agent_hunger(self)

    def score_coupling(self, neighbours):
        wolves = filter_by_type(neighbours, WolfAgent)
        return avoidance_score(self, wolves)

    def get_weighted_decisions(self, ns):
        return ([self.hunger,         self.coupling],
                [self.score_hunger(), self.score_coupling(ns)])
