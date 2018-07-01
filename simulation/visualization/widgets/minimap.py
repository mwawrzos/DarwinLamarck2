from mesa.visualization.ModularVisualization import VisualizationElement

import numpy as np

from simulation.boids import Agent


class VerySimpleCanvas(VisualizationElement):
    local_includes = ['simulation/visualization/widgets/minimap.js']

    def __init__(self, portrayal_method, canvas_width=500, canvas_height=500):
        super().__init__()
        self.portrayal_method = portrayal_method
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        new_elements = 'new VerySimpleContinuousModule(%s, %s)' % (self.canvas_width, self.canvas_height)
        self.js_code = 'elements.push(%s);' % new_elements

    def render(self, model):
        space_state = []
        for i, obj in enumerate(model.space.agents):
            x, y, = obj.pos
            x, y = x, y
            if isinstance(obj, Agent):
                vx, vy = obj.pos + obj.heading / 20
                vx, vy = vx, vy
                v2x, v2y = obj.pos
                v2x, v2y = v2x, v2y
            else:
                vx, vy = x, y
                v2x, v2y = x, y
            portrayal = {
                'Color': obj.COLOR,
                'x': x,
                'y': y,
                'vx': vx,
                'vy': vy,
                'v2x': v2x,
                'v2y': v2y,
                'r': obj.RADIUS
            }
            if hasattr(obj, 'VIEW_RANGE'):
                portrayal['rs'] = obj.VIEW_RANGE
            space_state.append(portrayal)
        return space_state
