try:
    from builtins import object
except ImportError:
    pass

from transitions.extensions.markup import MarkupMachine as Machine
from utils import Stuff


from unittest import TestCase

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock


class SimpleModel(object):

    def after_func(self):
        pass


class TestMarkupMachine(TestCase):

    def setUp(self):
        self.stuff = Stuff(machine_cls=Machine)
        self.transitions = [
            {'trigger': 'walk', 'source': 'A', 'dest': 'B'},
            {'trigger': 'run', 'source': 'B', 'dest': 'C'},
            {'trigger': 'sprint', 'source': 'C', 'dest': 'D'}
        ]

    def test_markup_self(self):

        m1 = Machine(states=['A', 'B', 'C'], transitions=self.transitions, initial='A')
        m1.walk()
        m2 = Machine(markup=m1.markup)
        self.assertEqual(m1.state, m2.state)
        self.assertEqual(len(m1.models), len(m2.models))
        self.assertEqual(m1.states.keys(), m2.states.keys())
        self.assertEqual(m1.events.keys(), m2.events.keys())

    def test_markup_self(self):

        model1 = SimpleModel()
        m1 = Machine(model1, states=['A', 'B', 'C'], transitions=self.transitions, initial='A')
        model1.walk()
        m2 = Machine(markup=m1.markup)
        model2 = m2.models[0]
        self.assertIsInstance(model2, SimpleModel)
        self.assertEqual(len(m1.models), len(m2.models))
        self.assertEqual(model1.state, model2.state)
        self.assertEqual(m1.states.keys(), m2.states.keys())
        self.assertEqual(m1.events.keys(), m2.events.keys())



    # TODO:
    #   * adapt diagrams to use markup