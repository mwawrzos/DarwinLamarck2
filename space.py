from mesa.space import ContinuousSpace

import numpy as np
import scipy.spatial.distance


SHIFTS = np.array([np.array([x, y])
                   for x in [0, 1]
                   for y in [0, 1]])

class CachedSpace(ContinuousSpace):
    def __init__(self):
        self.agents              = []
        self.not_removed         = []
        self.torus               = True
        self.x_min = self.y_min  = 0
        self.x_max = self.y_max  = 1
        self.width = self.height = 1

    def place_agent(self, agent, pos):
        self._outdated = True
        agent._idx = len(self.agents)
        self.agents.append(agent)
        self.not_removed.append(True)
        agent.pos = pos

    def move_agent(self, agent, pos):
        self._outdated = True
        agent.pos = pos

    def get_neighbors(self, agent, radius, include_center=True):
        self._update()
        distances = self._distances[agent._idx]
        neighbors = (distances <= radius) * self.not_removed
        neighbors[agent._idx] *= include_center
        idxs, = np.nonzero(neighbors)
        return (self.agents[idx] for idx in idxs)

    def get_heading(self, pos_1, pos_2):
        headings = pos_2 - (pos_1 + SHIFTS)
        lengths  = np.linalg.norm(headings, axis=1)
        return headings[lengths == lengths.min()][0]

    def get_distance(self, pos_1, pos_2):
        sp1, sp2 = pos_1 + SHIFTS, pos_2 + SHIFTS
        combinations = np.array([np.meshgrid(sp1[:,0], sp2[:,0]),
                                 np.meshgrid(sp1[:,1], sp2[:,1])]).reshape(16, 2, 2)
        headings = combinations[:, 0] - combinations[:, 1]
        lengths  = np.linalg.norm(headings, axis=1)
        return lengths[lengths == lengths.min()][0]

    def _remove_agent(self, pos, agent):
        self.not_removed[agent._idx] = False

    def _update(self):
        if self._outdated:
            self._clean_removed()

            pos = np.array([a.pos for a in self.agents])
            l = len(pos)
            shifts = pos + SHIFTS.reshape(4,1,2)
            shifts = shifts.reshape(4*l, 2)
            self._distances = scipy.spatial.distance.pdist(shifts)
            self._distances = scipy.spatial.distance.squareform(self._distances)
            self._distances = self._distances.reshape(4, l, 4, l)
            self._distances = self._distances.swapaxes(1, 2)
            self._distances = self._distances.reshape(4*4, l, l)
            self._distances = self._distances.min(axis=0)
            self._outdated = False

    def _clean_removed(self):
        tmp         = self.agents
        self.agents = []

        for not_rm, agent in zip(self.not_removed, tmp):
            if not_rm:
                agent._idx = len(self.agents)
                self.agents.append(agent)

        self.not_removed = [True] * len(self.agents)
