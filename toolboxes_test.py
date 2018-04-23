from unittest import TestCase, mock
import toolboxes

LOWER_BND = 1
UPPER_BND = 1000
MID_VAL   = (UPPER_BND + LOWER_BND) / 2
LOW_VAL   = LOWER_BND - 100
HIGH_VAL  = UPPER_BND + 100

class TestBounded(TestCase):
    def tes_allow_values_in_bounds(self):
        self.assertEqual(
            toolboxes.bounded(low=LOWER_BND, high=UPPER_BND)(lambda : ([MID_VAL, MID_VAL, MID_VAL],))(),
            ([MID_VAL, MID_VAL, MID_VAL],))

    def test_keeps_lower_bound(self):
        self.assertEqual(
            toolboxes.bounded(low=LOWER_BND, high=UPPER_BND)(lambda : ([MID_VAL, LOW_VAL, MID_VAL],))(),
            ([MID_VAL, LOWER_BND, MID_VAL],)
        )

    def test_keeps_upper_bound(self):
        self.assertEqual(
            toolboxes.bounded(low=LOWER_BND, high=UPPER_BND)(lambda : ([MID_VAL, HIGH_VAL, MID_VAL],))(),
            ([MID_VAL, UPPER_BND, MID_VAL],)
        )

def contains_fitness(population):
    return [hasattr(agent, 'fitness') for agent in population]

class TestSheep(TestCase):
    def setUp(self):
        self.sheep = toolboxes.sheep(3)
        self.population = self.sheep.population()

    def test_population(self):
        self.assertEqual(contains_fitness(self.population),
                         [True]*len(self.population))

    def test_select(self):
        population = self.sheep.select(self.population)
        self.assertEqual(contains_fitness(population),
                         [True]*len(population))

class TestWolves(TestCase):
    def setUp(self):
        self.wolves = toolboxes.wolves(3)
        self.population = self.wolves.population()

    def test_population(self):
        self.assertEqual(contains_fitness(self.population),
                         [True]*len(self.population))

    def test_select(self):
        population = self.wolves.select(self.population)
        self.assertEqual(contains_fitness(population),
                         [True]*len(population))

class TestLamarckian(TestCase):
    def setUp(self):
        self.individual = toolboxes.sheep(3).individual()
        self.lamarckian  = toolboxes.lamarckian(toolboxes.common_toolbox())

    def test_change_positive(self):
        individual, = self.lamarckian.change_positive(self.individual)
        self.assertTrue(hasattr(individual, 'fitness'))

    def test_change_negative(self):
        individual, = self.lamarckian.change_negative(self.individual)
        self.assertTrue(hasattr(individual, 'fitness'))

    def test_mutate(self):
        self.assertEqual(self.lamarckian.mutate(self.individual),
                         self.individual)

class TestDarwinian(TestCase):
    def setUp(self):
        self.individual = toolboxes.sheep(3).individual()
        self.darwinian  = toolboxes.darwinian(toolboxes.common_toolbox())

    def test_change_positive(self):
        self.assertEqual(self.darwinian.change_positive(self.individual),
                         self.individual)

    def test_change_negative(self):
        self.assertEqual(self.darwinian.change_negative(self.individual),
                         self.individual)

    def test_mutate(self):
        individual, = self.darwinian.mutate(self.individual)
        self.assertTrue(hasattr(individual, 'fitness'))

class TestEnvironment(TestCase):
    def setUp(self):
        class SpecieMock:
            def __init__(self, prefix):
                self.population     = mock.MagicMock(return_value=prefix + '_population')
                self.select         = mock.MagicMock(return_value=prefix + '_select')
                self.mate           = mock.MagicMock(return_value=prefix + '_mate')
                self.mutate         = mock.MagicMock(return_value=prefix + '_mutate')
                self.new_population = mock.MagicMock(return_value=prefix + '_new_population')
        specie_a, specie_b = SpecieMock('a'), SpecieMock('b')

        self.environment = toolboxes.environment(specie_a, specie_b)
        
    def test_delegates_population_call(self):
        self.assertEqual(self.environment.population(),
                         ['a_population', 'b_population'])
        
    def test_delegates_select_call(self):
        self.assertEqual(self.environment.select(),
                         ['a_select', 'b_select'])
        
    def test_delegates_mate_call(self):
        self.assertEqual(self.environment.mate(),
                         ['a_mate', 'b_mate'])
        
    def test_delegates_mutate_call(self):
        self.assertEqual(self.environment.mutate(),
                         ['a_mutate', 'b_mutate'])
        
    def test_delegates_new_population_call(self):
        self.assertEqual(self.environment.new_population(),
                         ['a_new_population', 'b_new_population'])
