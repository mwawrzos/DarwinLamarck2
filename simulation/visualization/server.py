from mesa.visualization.ModularVisualization import ModularServer

from simulation.visualization.widgets.minimap import VerySimpleCanvas
from simulation.visualization.widgets.histogram import Histogram
from simulation.visualization.widgets.text import VerySimpleText
from simulation.environment import Model, create_population

import gen.toolboxes # required to register necesary types
from gen.checkpoints import CheckpointManager


agent_canvas = VerySimpleCanvas(lambda _: {})

# histogram = Histogram(list(range(4)), 200, 500, lambda sheep: sheep.strategy.decision)
histogram2 = Histogram(list(range(1, 202)), 200, 500, lambda sheep: sheep.energy)

def reset_model(species, seed):
    model = Model(seed, 2000)
    population = create_population(*species, model.space)
    model.add_population(population)

    return model

experiment_path = r'C:\Users\mwawrzos\dev\DarwinLamarck2\checkpoints\2018_05_27_11_49_34'
epoch = 0
population, seed = CheckpointManager(experiment_path).load_epoch(epoch)

server = ModularServer(reset_model,
                       [agent_canvas, histogram2],
                       "Simulation",
                       {'seed': seed,
                        'species': population})
server.launch()