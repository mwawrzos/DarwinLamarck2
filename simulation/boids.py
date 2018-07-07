import numpy as np
import random

EPSILON = 1e-16

MAX_ENERGY   = 200
VIEW_RANGE   = 1e-1
BASE_SPEED   = 3e-3
SHEEP_RADIUS = 1e-2
GRASS_RADIUS = 6e-3
WOLF_RADIUS  = 1.4e-2
SHEEP_EAT_ENERGY = 10
WOLF_EAT_ENERGY  = 400
INERTIA = 0.3

def unit_vector(v):
    return v / (np.linalg.norm(v) + EPSILON)

def limit(val, low=0, high=1000):
    return max(low, min(high, val))

def score_agent_hunger(agent):
    return limit((agent.MAX_ENERGY - agent.energy) * agent.hunger_a + agent.hunger_b)

def filter_by_type(population, agentType):
    return (agent for agent in population if type(agent) is agentType)

def first_pos(agent, population):
    try:
        return next(iter(population)).pos
    except StopIteration:
        return agent.pos + [agent.VIEW_RANGE, 0]

def avoidance_score(agent, neighbours):
    closest = first_pos(agent, neighbours)
    distance_to_closest = agent.space.get_distance(agent.pos, closest)
    return 1 - (distance_to_closest / agent.VIEW_RANGE)

def avoid(neighbour_heading, radius):
    length = np.linalg.norm(neighbour_heading)
    return -neighbour_heading * (radius - length) / (length + EPSILON)

def escape(agent, neighbours):
    return sum((avoid(agent.space.get_heading(agent.pos, neighbour.pos),
                      agent.VIEW_RANGE)
                for neighbour in neighbours),
               np.array([0, 0]))

def cohere(agent, neighbours):
    return unit_vector(sum((agent.space.get_heading(agent.pos, neighbour.pos)
                           for neighbour in neighbours)))

def align(agent, neighbours):
    mass_centre = np.mean(np.array([neighbour.heading
                                    for neighbour in neighbours]), axis=0)
    return unit_vector(mass_centre)

def angle(V1, V2):
    cosang = np.dot(V1, V2)
    sinang = np.linalg.norm(np.cross(V1, V2))
    return np.arctan2(sinang, cosang)

def couple(agent, population):
    population = list(visible
                      for visible in population
                      if  angle(agent.space.get_heading(agent.pos, visible.pos),
                                agent.heading)
                          < np.pi/2)
    if not population:
        return np.array([0, 0])

    cohersion  = cohere(agent, population)
    alignment  = align(agent, population)
    separation = escape(agent, (neighbour
                                for neighbour in population
                                if agent.space.get_distance(agent.pos, neighbour.pos) <= agent.VIEW_RANGE / 2))
    return cohersion + separation + alignment

class Grass:
    RADIUS = GRASS_RADIUS
    COLOR = 'green'
    energy = 0

    def step(self):
        pass
    
    def advance(self):
        pass

class Decision:
    def __init__(self, pos, extra_speed=0):
        self._pos  = pos
        self.cost = 1 + 2 * extra_speed
        self.speed = BASE_SPEED * (1 + extra_speed)
        
    def apply(self, agent):
        self._pos = agent.space.torus_adj(self._pos)
        heading = agent.space.get_heading(agent.pos, self._pos)
        
        agent.heading = agent.heading + INERTIA * unit_vector(heading)
        agent.heading = unit_vector(agent.heading)
        agent.new_pos = agent.space.torus_adj(agent.pos + agent.heading * self.speed)

class Agent:
    VIEW_RANGE = VIEW_RANGE
    MAX_ENERGY = MAX_ENERGY
    RADIUS = None

    def __init__(self, space):
        self.space = space
        self.energy = self.MAX_ENERGY
        self.pos = None
        self.heading = np.zeros(2)
        self.new_pos = np.zeros(2)
        
    def step(self):
        neighbours = list(self.space.get_neighbors(self, self.VIEW_RANGE, include_center=False))
        self.decision = self.make_deicision(neighbours)
    
    def advance(self):
        self.decision.apply(self)
        coliding = self._get_coliding()

        if self.valid_decision(coliding):
            self.move()
        self.energy -= self.decision.cost
        if self.energy < self.MAX_ENERGY:
            self.find_food(coliding)
        self.penalty(coliding)
        if self.energy <= 0:
            self.space._remove_agent(self.pos, self)

    def _get_coliding(self):
        movement = self.space.get_distance(self.new_pos, self.pos)
        neighbours = self.space.get_neighbors(self, self.RADIUS + movement, include_center=False)
        # neighbours = list(neighbours)
        # print(len(neighbours), movement, self.heading)
        return [neighbour 
                for neighbour in neighbours
                if self.space.get_distance(self.new_pos, neighbour.pos) <= self.RADIUS]

    def move(self):
        self.space.move_agent(self, self.new_pos)
    
    def valid_decision(self, coliding):
        try:
            next(filter_by_type(coliding, type(self)))
            return False
        except:
            return True

    def make_deicision(self, neighbours):
        decisions, weights = self.get_weighted_decisions(neighbours)
        decision = random.choices(decisions, np.array(weights).round(8) + EPSILON)[0](neighbours)
        return decision
    
    def find_food(self, coliding):
        pass

    def penalty(self, coliding):
        pass

    def get_weighted_decisions(self, neighbours):
        pass

class SheepAgent(Agent):
    RADIUS = SHEEP_RADIUS
    COLOR = 'blue'

    def __init__(self, genes, space):
        super(SheepAgent, self).__init__(space)
        self.apply_genes(genes)
        self.eaten = 0

    def apply_genes(self, genes):
        (  self.hunger_a,   self.hunger_b,
             self.fear_a,     self.fear_b, self.fear_speed,
         self.coupling_a, self.coupling_b                 ) = genes

    def extract_genes(self):
        return (  self.hunger_a,   self.hunger_b,
                    self.fear_a,     self.fear_b, self.fear_speed,
                self.coupling_a, self.coupling_b                 )

    def hunger(self, neighbours):
        food = filter_by_type(neighbours, Grass)
        closest = first_pos(self, food)
        return Decision(self.space.get_heading(self.pos, closest))

    def coupling(self, neighbours):
        sheep = filter_by_type(neighbours, SheepAgent)
        return Decision(couple(self, sheep))

    def fear(self, neighbours):
        return Decision(escape(self, neighbours), self.fear_speed)

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

    def find_food(self, coliding):
        if filter_by_type(coliding, Grass):
            self.energy += SHEEP_EAT_ENERGY
            self.eaten  += 1

class WolfAgent(Agent):
    RADIUS = WOLF_RADIUS
    COLOR = 'red'

    def __init__(self, genes, space):
        super(WolfAgent, self).__init__(space)
        self.apply_genes(genes)
        self.eaten = 0

    def apply_genes(self, genes):
        (  self.hunger_a,   self.hunger_b, self.hunger_speed,
         self.coupling_a, self.coupling_b                   ) = genes

    def extract_genes(self):
        return (  self.hunger_a,   self.hunger_b, self.hunger_speed,
                self.coupling_a, self.coupling_b                   )

    def hunger(self, neighbours):
        food = filter_by_type(neighbours, SheepAgent)
        closest = first_pos(self, food)
        return Decision(self.space.get_heading(self.pos, closest), self.hunger_speed)

    def coupling(self, neighbours):
        wolves = filter_by_type(neighbours, WolfAgent)
        return Decision(couple(self, wolves))

    def score_hunger(self):
        return score_agent_hunger(self)

    def score_coupling(self, neighbours):
        wolves = filter_by_type(neighbours, WolfAgent)
        return avoidance_score(self, wolves)

    def get_weighted_decisions(self, ns):
        return ([self.hunger,         self.coupling],
                [self.score_hunger(), self.score_coupling(ns)])

    def find_food(self, coliding):
        for sheep in filter_by_type(coliding, SheepAgent):
            self.energy, sheep.energy = self.energy + WOLF_EAT_ENERGY, 0
            self.eaten  += 1
            self.space._remove_agent(sheep.pos, sheep)
