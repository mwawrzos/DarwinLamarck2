from unittest import TestCase, mock
import numpy as np

import space

class CachedSpaceTest(TestCase):
    R = 1e-3
    epsilon = 1e-10
    eR = R - epsilon
    AROUND_CENTER = np.array([[eR,     0],
                              [0,      eR],
                              [eR/2,   eR/2],
                              [1-eR,   0],
                              [0,      1-eR],
                              [1-eR/2, 1-eR/2]])
    HEADINGS      = np.concatenate((AROUND_CENTER[:3], -AROUND_CENTER[:3]))
    DISTANCES     = np.array([eR, eR, np.sqrt(eR*eR/2)]*2)

    def setUp(self):
        self.space = space.CachedSpace()
        self.agents = [0, 1]
        for i in range(2):
            self.agents[i] = mock.MagicMock()
            self.space.place_agent(self.agents[i], np.random.rand(2))

    def test_place_agent(self):
        pos = np.random.rand(2)
        agent = mock.MagicMock()
        self.space.place_agent(agent, pos)

        np.testing.assert_array_equal(agent.pos, pos)
        self.assertTrue(agent in self.space.agents)
        self.assertTrue(self.space._outdated)

    def test_move_agent(self):
        pos = np.random.rand(2)
        self.space.move_agent(self.agents[0], pos)
        np.testing.assert_array_equal(self.agents[0].pos, pos)
        self.assertTrue(self.space._outdated)

    def test_get_neighbors(self):
        self.space.move_agent(self.agents[0], np.array([0, 0]))
        self.space.place_agent(mock.MagicMock(), np.array([.5,.5]))

        for x, y in self.AROUND_CENTER:
            self.space.move_agent(self.agents[1], np.array([x, y]))
            self.assertEqual(self.agents,
                             list(self.space.get_neighbors(self.agents[0], self.R)),
                             'agent in %s should be found' % np.array((x, y)))

    def test_get_heading(self):
        pos1 = 0, 0
        for pos2, heading in zip(self.AROUND_CENTER, self.HEADINGS):
            np.testing.assert_array_almost_equal(
                heading,
                self.space.get_heading(pos1, pos2),
                err_msg='from {pos1} to {pos2}'.format(pos1=pos1, pos2=pos2)
            )

    def test_get_distance(self):
        for pos1 in (0, 0), (1, 1):
            for pos2, distance in zip(self.AROUND_CENTER, self.DISTANCES):
                np.testing.assert_array_almost_equal(
                    distance,
                    self.space.get_distance(pos1, pos2),
                    err_msg='from {pos1} to {pos2}'.format(pos1=pos1, pos2=pos2)
                )

    def test_torus_adj(self):
        pos = np.random.rand(2)
        shifts = space.create_shifts(pos)
        for shift in shifts:
            np.testing.assert_array_almost_equal(
                pos,
                self.space.torus_adj(shift),
                err_msg='from shift {}'.format(shift)
            )

    def test_remowing(self):
        self.space.move_agent(self.agents[0], np.array([0, 0]))
        self.space.move_agent(self.agents[1], np.array([self.R/2,self.R/2]))

        self.space._remove_agent(self.agents[1].pos, self.agents[1])

        self.assertEqual([self.agents[0]],
                         list(self.space.get_neighbors(self.agents[0], self.R)),
                         'agent 1 should be removed')

