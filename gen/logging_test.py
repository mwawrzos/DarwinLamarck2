from unittest import TestCase, mock

import gen.logging as log
import gen.toolboxes as tbx

class TestLogging(TestCase):
    def setUp(self):
        self.stats = log.Stats()
        self.foo_mock = mock.MagicMock()
        self.logger = self.stats.log_decorator(self.foo_mock)
        self.pop, = tbx.environment(tbx.sheep(3), tbx.wolves(3)).population()

        x = 42
        for spec in self.pop:
            for ind in spec:
                ind.fitness.values = x, x
                x += 1

    def test_logging(self):
        self.foo_mock.return_value = (self.pop,)
        self.logger([])
