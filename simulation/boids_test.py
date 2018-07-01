from unittest import TestCase, mock

import numpy as np

from simulation import boids

DUMMY_POS      = np.array([0xbaba, 0xb05])
DUMMY_POS2     = np.array([0xABC, 0xDEF])
DUMMY_VIEW     = 0xA13A
DUMMY_DISTANCE = 0xD157

class FlockTest(TestCase):
    def setUp(self):
        self.agent = mock.MagicMock(
            pos=DUMMY_POS,
            VIEW_RANGE=DUMMY_VIEW)

    def assert_called_with_np(self, foo, calls_args):
        for n, (found_args, expected_args) in enumerate(zip(foo.calls_args, calls_args)):
            self.assertEqual(len(found_args),
                             len(expected_args),
                             'In {N} call expected {NUM_EXPECTED} args, while {NUM_FOUND} found'.format(
                                 N=n,
                                 NUM_EXPECTED=len(expected_args),
                                 NUM_FOUND=len(found_args)))
            for i, (received, expected) in enumerate(zip(found_args, expected_args)):
                np.testing.assert_equal(received, expected, 'In {N} call invalid {I}th argument'.format(N=n, I=i))

    def test_first_pos_nonempty_list(self):
        populaiton = [mock.MagicMock(pos=np.array([i, i])) for i in range(10)]
        np.testing.assert_equal(boids.first_pos(self.agent, populaiton),
                                populaiton[0].pos)

    def test_first_pos_nonempty_generator(self):
        populaiton = (mock.MagicMock(pos=np.array([i, i])) for i in range(10))
        np.testing.assert_equal(boids.first_pos(self.agent, populaiton),
                                np.array([0, 0]))

    def test_first_pos_empty_population(self):
        populaiton = []
        np.testing.assert_equal(boids.first_pos(self.agent, populaiton),
                                DUMMY_POS + [DUMMY_VIEW, 0])

    def test_avoidance_score_works_on_gen_and_list(self):
        population = [mock.MagicMock(pos=DUMMY_POS + i) for i in range(10)]
        self.assertEqual(boids.avoidance_score(self.agent, population),
                         boids.avoidance_score(self.agent, iter(population)))

    def test_avoidance_score_depends_only_on_closest(self):
        dense_population  = [mock.MagicMock(pos=DUMMY_POS + i) for i in range(10, 20, 1)]
        sparse_population = [mock.MagicMock(pos=DUMMY_POS + i) for i in range(10, 30, 2)]
        np.testing.assert_equal(dense_population[0].pos, sparse_population[0].pos)
        
        get_distance = self.agent.space.get_distance
        
        get_distance.return_value = DUMMY_DISTANCE
        dense_score = boids.avoidance_score(self.agent, dense_population)
        self.assert_called_with_np(get_distance, [self.agent.pos, dense_population[0].pos])
        get_distance.reset_mock()
        
        get_distance.return_value = DUMMY_DISTANCE
        sparese_score = boids.avoidance_score(self.agent, sparse_population)
        self.assert_called_with_np(get_distance, [self.agent.pos, dense_population[0].pos])
        
        self.assertEqual(dense_score, sparese_score)

    def test_avoidance_score_is_higher_for_closer_neighbors(self):
        far_population = [mock.MagicMock(pos=DUMMY_POS + i) for i in range(3, 13)]
        close_population = [mock.MagicMock(pos=DUMMY_POS + i) for i in range(2, 12)]

        get_distance = self.agent.space.get_distance
        
        get_distance.return_value = DUMMY_DISTANCE + 1
        far_score = boids.avoidance_score(self.agent, far_population)
        self.assert_called_with_np(get_distance, [self.agent.pos, far_population[0].pos])
        get_distance.reset_mock()
        
        get_distance.return_value = DUMMY_DISTANCE
        close_score = boids.avoidance_score(self.agent, close_population)
        self.assert_called_with_np(get_distance, [self.agent.pos, close_population[0].pos])

        self.assertGreater(close_score, far_score)

    def test_avoid(self):
        ME = np.array(DUMMY_POS)
        HE = np.array(DUMMY_POS2)
        avoid_vector = boids.avoid(ME - HE, DUMMY_VIEW)
        self.assertAlmostEqual(np.linalg.norm((ME + avoid_vector) - HE), DUMMY_VIEW)
        self.assertGreater(DUMMY_VIEW, np.linalg.norm(avoid_vector))

    @mock.patch('simulation.boids.avoid', return_value=np.ones(2))
    def test_escape_empty_population(self, avoid_mock):
        np.testing.assert_equal(
            boids.escape(self.agent, []),
            np.zeros(2))

    @mock.patch('simulation.boids.avoid', return_value=np.ones(2))
    def test_escape_nonempty_population(self, avoid_mock):
        POP = [mock.MagicMock(pos=np.array([x, y])) for x, y in [[4,-2], [7,8], [-3,-7], [5,1], [-3,0]]]
        POP_SIZE = len(POP)
        np.testing.assert_equal(
            boids.escape(self.agent, POP),
            np.ones(2) * POP_SIZE)
        self.assert_called_with_np(avoid_mock, [[self.agent.pos - neighbor.pos, self.agent.VIEW_RANGE] for neighbor in POP])

