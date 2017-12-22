import json
from six import string_types
from functools import partial
import itertools

from ..core import Machine


class JSONMachine(Machine):

    def __init__(self, *args, **kwargs):
        self._json = {}
        self.with_auto_transitions = True
        self.with_reference_names = True
        super(JSONMachine, self).__init__(*args, **kwargs)

    def json(self):
        self._json['states'] = [state for state in self.states]
        self._json['transitions'] = self._convert_transitions()
        return self._json

    def _convert_transitions(self):
        json_transitions = []
        for event in self.events.values():
            if self._omit_auto_transitions(event):
                continue

            for transitions in event.transitions.items():
                src = transitions[0]
                for trans in transitions[1]:
                    new_json = {"trigger": event.name, "src": src, "dest": trans.dest,
                                "prepare": [rep(f) for f in trans.prepare],
                                "conditions": [rep(f.func) for f in trans.conditions if f.target],
                                "unless": [rep(f.func) for f in trans.conditions if not f.target],
                                "before": [rep(f) for f in trans.before],
                                "after": [rep(f) for f in trans.after]}
                    json_transitions.append({k: v for k, v in new_json.items() if v})
        return json_transitions

    def _omit_auto_transitions(self, event):
        return self._is_auto_transition(event) and not self.with_auto_transitions

    # auto transition events commonly a) start with the 'to_' prefix, followed by b) the state name
    # and c) contain a transition from each state to the target state (including the target)
    def _is_auto_transition(self, event):
        if event.name.startswith('to_') and len(event.transitions) == len(self.states):
            state_name = event.name[len('to_'):]
            if state_name in self.states:
                return True
        return False


def rep(func):
    """ Return a string representation for `func`. """
    if isinstance(func, string_types):
        return func
    try:
        return func.__name__
    except AttributeError:
        pass
    if isinstance(func, partial):
        return "%s(%s)" % (
            func.func.__name__,
            ", ".join(itertools.chain(
                (str(_) for _ in func.args),
                ("%s=%s" % (key, value)
                 for key, value in iteritems(func.keywords if func.keywords else {})))))
    return str(func)