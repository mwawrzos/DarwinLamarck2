import random
from deap import base, tools, creator, algorithms

from environment import Environment

creator.create('FitnessMax', base.Fitness, weights=(1.,.1))
creator.create('Sheep', list, fitness=creator.FitnessMax)
creator.create('Wolf', list, fitness=creator.FitnessMax)

def bounded(low=0, high=1):
    def bounder(func):
        def wrapper(*args, **kwargs):
            res, = func(*args, **kwargs)
            for i in range(len(res)):
                res[i] = max(low, min(high, res[i]))
            return res,
        return wrapper
    return bounder

def common_toolbox():
    toolbox = base.Toolbox()
    toolbox.register('random', random.random)
    toolbox.register('mate', tools.cxTwoPoint)
    toolbox.register('new_population', algorithms.varAnd, cxpb=0.5, mutpb=0.1, toolbox=toolbox)
    return toolbox

def identity_tuple(x):
    return x,

def sheep(count):
    toolbox = common_toolbox()
    toolbox.register('individual', tools.initRepeat, creator.Sheep, toolbox.random, n=7)
    toolbox.register('population', tools.initRepeat, list, toolbox.individual, n=count)
    toolbox.register('select', tools.selTournament, tournsize=3, k=count)
    return toolbox

def wolves(count):
    toolbox = common_toolbox()
    toolbox.register('individual', tools.initRepeat, creator.Wolf, toolbox.random, n=5)
    toolbox.register('population', tools.initRepeat, list, toolbox.individual, n=count)
    toolbox.register('select', tools.selTournament, tournsize=3, k=count)
    # toolbox.register('select', tools.emo.identity) #, tournsize=3, k=count)
    return toolbox

def lamarckian(toolbox):
    toolbox.__name__ = 'lama'
    toolbox.register('change_positive', tools.mutGaussian, mu= 1e-4, std=5e-5)
    toolbox.decorate('change_positive', bounded())
    toolbox.register('change_negative', tools.mutGaussian, mu=-1e-4, std=5e-5)
    toolbox.decorate('change_negative', bounded())
    toolbox.register('mutate', identity_tuple)
    return toolbox

def darwinian(toolbox):
    toolbox.__name__ = 'dar'
    toolbox.register('change_positive', tools.emo.identity)
    toolbox.register('change_negative', tools.emo.identity)
    toolbox.register('mutate', tools.mutGaussian, mu=0, sigma=1e-2, indpb=1e-1)
    toolbox.decorate('mutate', bounded())
    return toolbox

def call(method):
    def caller(toolbox, *args, **kwargs):
        return toolbox.__getattribute__(method)(*args, **kwargs)
    return caller

def run_member(foo, pop, *args):
    return [foo(*x) for x in zip(pop, *args)]

def environment(*species):
    toolbox = base.Toolbox()
    toolbox.register('population',     run_member, call('population'),     species)
    toolbox.register('select',         run_member, call('select'),         species)
    toolbox.register('mate',           run_member, call('mate'),           species)
    toolbox.register('mutate',         run_member, call('mutate'),         species)
    toolbox.register('new_population', run_member, call('new_population'), species)
    
    return toolbox
