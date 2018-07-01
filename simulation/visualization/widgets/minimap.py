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
                v2x, v2y = np.array(obj.decision._pos) * 3e-3 + obj.pos
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
            if i == 1:
                # print('DEBUG', getattr(obj, 'debug', ''))
                # print('<<', obj.decision._pos, '>>', obj.pos, id(obj))
                # print('[[ x y    ', x, y)
                # print('[[ vx vy  ', vx, vy)
                # print('[[ v2x v2y', v2x, v2y, ']]')
                # print(i, portrayal, obj.decision.name)
                # print(obj.decision.angles)
                # print(obj.decision.sheep_asd)
                portrayal['Color'] = 'magenta'
                for influencer in obj.decision.influencers:
                    x, y = influencer
                    x, y = x, y
                    space_state.append({
                            'Color': 'black',
                            'x': x,
                            'y': y,
                            'vx': x,
                            'vy': y,
                            'v2x': x,
                            'v2y': y,
                            'r': obj.RADIUS * 2
                        })
            space_state.append(portrayal)
        # print('='*30, model.schedule.time, '='*30)
        return space_state
