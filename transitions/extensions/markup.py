from six import string_types, iteritems
from functools import partial
import itertools
import importlib

from ..core import Machine
from .nesting import HierarchicalMachine


class MarkupMachine(Machine):

    def __init__(self, *args, **kwargs):
        self._markup = kwargs.pop('markup', {})
        self.with_auto_transitions = kwargs.pop('with_auto_transitions', False)
        self.skip_references = True

        if self._markup:
            models_markup = self._markup.pop('model', [])
            super(MarkupMachine, self).__init__(None, **self._markup)
            for m in models_markup:
                self._add_markup_model(m)
        else:
            super(MarkupMachine, self).__init__(*args, **kwargs)
            self._markup['initial'] = self.initial
            self._markup['before_state_change'] = [x for x in (rep(f) for f in self.before_state_change) if x]
            self._markup['after_state_change'] = [x for x in (rep(f) for f in self.before_state_change) if x]
            self._markup['prepare_event'] = [x for x in (rep(f) for f in self.prepare_event) if x]
            self._markup['finalize_event'] = [x for x in (rep(f) for f in self.finalize_event) if x]
            self._markup['name'] = self.name
            self._markup['send_event'] = self.send_event
            self._markup['auto_transitions'] = self.auto_transitions
            self._markup['ignore_invalid_triggers'] = self.ignore_invalid_triggers
            self._markup['queued'] = self.has_queue

    @property
    def markup(self):
        self._markup['model'] = self._convert_models()
        return self._markup

    def add_transition(self, trigger, source, dest, conditions=None,
                       unless=None, before=None, after=None, prepare=None, **kwargs):
        super(MarkupMachine, self).add_transition(trigger, source, dest, conditions=conditions, unless=unless,
                                                  before=before, after=after, prepare=prepare, **kwargs)
        self._markup['transitions'] = self._convert_transitions()

    def add_states(self, states, on_enter=None, on_exit=None, ignore_invalid_triggers=None, **kwargs):
        super(MarkupMachine, self).add_states(states, on_enter=on_enter, on_exit=on_exit,
                                              ignore_invalid_triggers=ignore_invalid_triggers, **kwargs)
        self._markup['states'] = self._convert_states(self.states.values())

    def _convert_states(self, states):
        return [{'name': state.name} for state in states]

    def _add_markup_model(self, markup):
        initial = markup.get('state', None)
        if markup['class-name'] == 'self':
            self.add_model(self, initial)
        else:
            mod_name, cls_name = markup['class-name'].rsplit('.', 1)
            cls = getattr(importlib.import_module(mod_name), cls_name)
            self.add_model(cls(), initial)

    def _convert_models(self):
        models = []
        for m in self.models:
            model_def = dict(state=m.state)
            model_def['class-name'] = 'self' if m == self else m.__module__ + "." + m.__class__.__name__
            models.append(model_def)
        return models

    def _convert_transitions(self):
        json_transitions = []
        skip = self.skip_references
        for event in self.events.values():
            if self._omit_auto_transitions(event):
                continue

            for transitions in event.transitions.items():
                src = transitions[0]
                for trans in transitions[1]:
                    new_json = {"trigger": event.name, "source": src, "dest": trans.dest,
                                "prepare": [x for x in (rep(f, skip) for f in trans.prepare) if x],
                                "conditions": [x for x in (rep(f.func, skip) for f in trans.conditions if f.target) if x],
                                "unless": [x for x in (rep(f.func, skip) for f in trans.conditions if not f.target) if x],
                                "before": [x for x in (rep(f, skip) for f in trans.before) if x],
                                "after": [x for x in (rep(f, skip) for f in trans.after) if x]}
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


class HierarchicalMarkupMachine(MarkupMachine, HierarchicalMachine):

    def _convert_states(self, states):
        return self._convert_nested_states([state for state in states if not state.parent])

    def _convert_nested_states(self, states):
        return [{'name': state._name} if not state.children else
                {'name': state._name, 'children': self._convert_nested_states(state.children)} for state in states]


def rep(func, skip_references=False):
    """ Return a string representation for `func`. """
    if isinstance(func, string_types):
        return func
    if skip_references:
        return None
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
