from unittest import TestCase, mock

import simulation.environment as env

import gen.toolboxes as tbx

def contains_fitness(population):
    return [hasattr(agent, 'fitness') for agent in population]

class TestEnvironment(TestCase):
    def setUp(self):
        self.env = env.Environment(1)

    def test_empty_input(self):
        sheep = []
        wolves = []
        species = sheep, wolves
        self.assertEqual(self.env.run_simulation(species, 42),
                         (species,))

    def test_input(self):
        sheep = tbx.sheep(3).population()
        wolves = tbx.wolves(3).population()
        species = sheep, wolves
        (sheep, wolves), = self.env.run_simulation(species, 42)
        self.assertEqual(((sheep, wolves),),
                         (species,))
        self.assertEqual(contains_fitness(sheep), [True]*3)
        self.assertEqual(contains_fitness(wolves), [True]*3)