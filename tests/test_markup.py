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
        m2 = Machine(markup=m1.markup())
        self.assertEqual(m1.state, m2.state)
        self.assertEqual(len(m1.states), len(m2.states))

    # TODO:
    #   * test markup class loading model
    #   * couple markup generation to add_state and add_transition
    #   * adapt diagrams to use markup