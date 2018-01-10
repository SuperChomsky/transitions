try:
    from builtins import object
except ImportError:
    pass

import warnings
import sys

from transitions.extensions.exchange import ExchangeMachine as Machine

from unittest import TestCase, skipIf

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock


class TestExchangeTransitions(TestCase):


    # def test_markup(self):
    #
    #     markup = dict(states=['A', 'B'], transitions=[dict(src='A', dest='B')])
    #

    def test_states(self):
        def condition_func():
            pass

        m1 = Machine(states=['A', 'B', 'C'], transitions=[
            ['go', 'A', 'B'],
            ['walk', '*', 'A'],
            {'trigger': 'foo', 'source': 'B', 'dest': 'C', 'before': 'before', 'conditions': condition_func,
             'prepare': 'prepare', 'after': 'after'}
        ], initial='A', auto_transitions=False)
        m1.go()
        m2 = Machine(markup=m1.markup())
        self.assertEqual(m1.state, m2.state)
        self.assertEqual(len(m1.states), len(m2.states))

