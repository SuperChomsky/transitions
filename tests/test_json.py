try:
    from builtins import object
except ImportError:
    pass

import warnings
import sys

from transitions.extensions.json import JSONMachine as Machine

from unittest import TestCase, skipIf

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock


class TestJSONTransitions(TestCase):

    def test_states(self):
        def condition_func():
            pass

        m = Machine(states=['A', 'B', 'C'], transitions=[
            ['go', 'A', 'B'],
            ['walk', '*', 'C'],
            {'trigger': 'foo', 'source': 'A', 'dest': 'C', 'before': 'before', 'conditions': condition_func,
             'prepare': 'prepare', 'after': 'after'}
        ], initial='A', auto_transitions=False)
        print(m.json())
