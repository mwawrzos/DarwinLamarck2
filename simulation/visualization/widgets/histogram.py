import numpy as np
from mesa.visualization.ModularVisualization import VisualizationElement

from simulation.boids import SheepAgent, filter_by_type

class Histogram(VisualizationElement):
    package_includes = ['Chart.min.js']
    local_includes = ['simulation/visualization/widgets/histogram.js']

    def __init__(self, bins, canvas_height, canvas_width, getter):
        super().__init__()
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.bins = bins
        new_element = "new Histogram({}, {}, {})"
        new_element = new_element.format(bins,
                                         canvas_width,
                                         canvas_height)
        self.js_code = "elements.push(" + new_element + ");"
        self.getter = getter

    def render(self, model):
        sheep = filter_by_type(model.schedule.agents, SheepAgent) # filter(t_matcher(SheepAgent), model.schedule.agents)
        wealth_values = list(map(self.getter, sheep))
        hist = np.histogram(wealth_values, bins=self.bins)[0]
        return [int(x) for x in hist]
