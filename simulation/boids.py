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
    res = sum((avoid(agent.space.get_heading(agent.pos, neighbour.pos),
                      agent.VIEW_RANGE)
                for neighbour in neighbours),
               np.array([0, 0]))
    return res

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
    if not population:
        return np.array([0, 0])

    cohersion  = cohere(agent, population)
    alignment  = align(agent, population)
    separation = escape(agent, (neighbour
                                for neighbour in population
                                if agent.space.get_distance(agent.pos, neighbour.pos) <= agent.VIEW_RANGE / 2))
    coupling = cohersion + separation * 5 / agent.VIEW_RANGE + alignment
    return unit_vector(coupling)

def hunt(agent, neighbours):
        closest = first_pos(agent, neighbours)
        food_vector = agent.space.get_heading(agent.pos, closest)
        return unit_vector(food_vector)

class Grass:
    RADIUS = GRASS_RADIUS
    COLOR = 'green'
    energy = 0

    def make_deicision(self):
        pass
    
    def move(self):
        pass

    def update_space(self):
        pass

    def resolve_collision(self):
        pass
    
    def take_action(self):
        pass

class Decision:
    def __init__(self, heading, extra_speed=0):
        self._heading  = heading
        self.cost = 1 + 2 * extra_speed
        self.speed = BASE_SPEED * (1 + extra_speed)
        
    def apply(self, agent):
        agent.heading = agent.heading + INERTIA * (self._heading / (np.linalg.norm(self._heading) + EPSILON))
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
        self.old_pos = None
        self.heading = np.zeros(2)
        self.new_pos = np.zeros(2)
        self.decision = Decision((-1,-1))
        
    def make_decision(self):
        neighbours = list(self.space.get_neighbors(self, self.VIEW_RANGE, include_center=False))
        self.decision = self._make_deicision(neighbours)

    def move(self):
        self.decision.apply(self)
        self.space.move_agent(self, self.new_pos, on_hold=True)

    def update_space(self):
        self.space.move_hold()

    def resolve_collision(self):
        try:
            coliding = self._get_coliding()
            next(filter_by_type(coliding, type(self)))              # if not empty
            self.space.move_agent(self, self.old_pos, on_hold=True) # then move back
        except StopIteration:                                       # otherwise
            pass                                                    # do nothing
    
    def take_action(self):
        self.space.move_hold()
        coliding = list(self._get_coliding())
        self.energy -= self.decision.cost
        if self.energy < self.MAX_ENERGY:
            self.find_food(coliding)
        self.penalty(coliding)
        if self.energy <= 0:
            self.space._remove_agent(self.pos, self)

    def _get_coliding(self):
        return self.space.get_neighbors(self, self.RADIUS*2, include_center=False) 
    
    def valid_decision(self, coliding):
        try:
            next(filter_by_type(coliding, type(self)))
            return False
        except:
            return True

    def _make_deicision(self, neighbours):
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
        return Decision(hunt(self, food))

    def coupling(self, neighbours):
        sheep = list(filter_by_type(neighbours, SheepAgent))
        s1 = sheep

        # population = list(population)
        # print([angle(p.pos - agent.pos, agent.heading) for p in population])
        population = list(p for p in sheep if angle(self.space.get_heading(self.pos, p.pos), self.heading) < np.pi/2)
        sheep = population

        dec =  Decision(couple(self, sheep))
        return dec

    def fear(self, neighbours):
        wolves = list(filter_by_type(neighbours, WolfAgent))
        return Decision(escape(self, wolves), self.fear_speed)

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
        return Decision(hunt(self, food), self.hunger_speed)

    def coupling(self, neighbours):
        wolves = list(filter_by_type(neighbours, WolfAgent))
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

    def penalty(self, coliding):
        for sheep in filter_by_type(coliding, SheepAgent):
            if sheep.energy > 0:
                self.energy, sheep.energy = self.energy + WOLF_EAT_ENERGY, 0
                self.eaten  -= 1
                self.space._remove_agent(sheep.pos, sheep)
