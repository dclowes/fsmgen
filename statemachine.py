#!/usr/bin/env python
# Author: Douglas Clowes (douglas.clowes@ansto.gov.au) Aug 2015
# vim: ft=python ts=8 sts=4 sw=4 expandtab autoindent smartindent nocindent
#

# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-instance-attributes
# pylint: disable=missing-docstring
# pylint: disable=global-statement
# pylint: disable=too-few-public-methods
#

import os

class Event(object):
    def __init__(self, name, arglist=None):
        self.name = name
        self.comments = []
        self.arglist = arglist
    def __repr__(self):
        txt = self.name
        if self.arglist:
            txt = self.name + '(' + ', '.join(self.arglist) + ')'
        return txt
    def __str__(self):
        txt = self.name
        if self.arglist:
            txt = self.name + '(' + ', '.join(self.arglist) + ')'
        return txt

class State(object):
    def __init__(self, name, base_list=None):
        self.name = name
        self.comments = []
        if base_list is None:
            self.base_list = []
        else:
            self.base_list = base_list

    def __repr__(self):
        if len(self.base_list) > 0:
            return self.name + '(' + ', '.join(self.base_list) + ')'
        else:
            return self.name

class Transition(object):
    def __init__(self, source, event, actions=[], targets=[]):
        self.source = source
        self.event = event
        self.actions = actions
        self.targets = targets

    def __repr__(self):
        return ", ".join([self.source, self.event, repr(self.actions), repr(self.targets)])

class Classifier(object):
    def __init__(self, source, event, actions=[], targets=[]):
        self.source = source
        self.event = event
        self.actions = actions
        self.targets = targets

    def __repr__(self):
        return ", ".join([self.source, self.event, repr(self.actions), repr(self.targets)])

class Action(object):
    def __init__(self, name):
        self.name = name
        self.comments = []
        self.code_text = {}

    def __repr__(self):
        if self.code_text:
            return "%s (%s) {%s}" % (self.name, self.comments, self.code_text)
        else:
            return "%s" % self.name

class Test(object):
    def __init__(self, tests):
        self.tests = tests

    def __repr__(self):
        return ", ".join(self.tests)

class StateMachine(object):
    def __init__(self, name):
        self.name = name
        self.uname = name.upper()
        self.comments = []
        self.actions = []
        self.events = []
        self.states = []
        self.tests = []
        self.transitions = []
        self.classifiers = []
        self.action_list = []
        self.outputs = []

    def __repr__(self):
        text = "name = %s" % repr(self.name)
        text += ", uname = %s" % repr(self.uname)
        text += ", states = [%s]" % ', '.join([repr(s) for s in self.states])
        text += ", events = [%s]" % ', '.join([repr(s) for s in self.events])
        text += ", classifiers = [%s]" % ', '.join([repr(s) for s in self.classifiers])
        text += ", transitions = [%s]" % ', '.join([repr(s) for s in self.transitions])
        text += ", tests = [%s]" % ', '.join([repr(s) for s in self.tests])
        text += ", actions = [%s]" % ', '.join([repr(s) for s in self.actions])
        return '{ ' + text + ' }'

    def addEvent(self, event):
        assert isinstance(event, Event)
        if event not in self.events:
            self.events.append(event)

    def addState(self, state):
        assert isinstance(state, State)
        if state not in self.states:
            self.states.append(state)

    def addTransition(self, transition):
        assert isinstance(transition, Transition)
        assert transition.source in [s.name for s in self.states]
        assert transition.event in [e.name for e in self.events]
        if (transition.source, transition.event) in [(t.source, t.event) for t in self.transitions]:
            print "Duplicate transition:", transition
        elif (transition.source, transition.event) in [(t.source, t.event) for t in self.classifiers]:
            print "Conflicted classification:", transition
        else:
            self.transitions.append(transition)

    def addClassifier(self, classifier):
        assert isinstance(classifier, Classifier)
        assert classifier.source in [s.name for s in self.states]
        assert classifier.event in [e.name for e in self.events]
        if (classifier.source, classifier.event) in [(t.source, t.event) for t in self.classifiers]:
            print "Duplicate classifier:", classifier
        elif (classifier.source, classifier.event) in [(t.source, t.event) for t in self.transitions]:
            print "Conflicted transition:", classifier
        else:
            self.classifiers.append(classifier)

    def addAction(self, action):
        assert isinstance(action, Action)
        self.actions.append(action)

    def addTest(self, test):
        assert isinstance(test, Test)
        for item in test.tests:
            assert item in [s.name for s in self.states] + [e.name for e in self.events]
        assert test.tests[0] in [s.name for s in self.states]
        assert test.tests[-1] in [s.name for s in self.states]
        self.tests.append(test)

    def getEvent(self, name):
        for e in self.events:
            if e.name == name:
                return e
        return None

    def getState(self, name):
        for s in self.states:
            if s.name == name:
                return s
        return None

    def getAction(self, name):
        for a in self.actions:
            if a.name == name:
                return a
        return None

    def getTargets(self, name):
        for item in self.classifiers:
            if name in item.actions:
                return item.targets
        return []

    def getTrans(self, state, event):
        for item in self.classifiers:
            if item.source == state.name and item.event == event.name:
                return item
        for item in self.transitions:
            if item.source == state.name and item.event == event.name:
                return item
        return None

    def isClassifier(self, name):
        for item in self.classifiers:
            if name in item.actions:
                return True
        return False

    def printit(self):
        print "StateMachine:", self.name
        print "States:", ", ".join([repr(s) for s in self.states])
        print "Events:", ", ".join([repr(s) for s in self.events])
        print "Actions:", ", ".join([repr(s) for s in self.action_list])
        for c in self.classifiers:
            print "Classifier:", c
        for t in self.transitions:
            print "Transition:", t
        for a in self.actions:
            print "Action:", a
        for t in self.tests:
            print "Test:", t

    def Actions(self):
        return sorted(self.actions, key=lambda a: a.name)

    def Events(self):
        result = sorted([e for e in self.events if e.name in ['Entry', 'Exit']],
                        key=lambda e: e.name)
        result += sorted([e for e in self.events if e.name not in ['Entry', 'Exit']],
                         key=lambda e: e.name)
        return result

    def States(self):
        return sorted(self.states, key=lambda s: s.name)

class StateMachine_Text(StateMachine):
    def __init__(self, other):
        if isinstance(other, StateMachine):
            StateMachine.__init__(self, other.name)
            # Copy from the other one
            self.name = other.name[:]
            self.dest_file = other.dest_file
            self.comments = other.comments[:]
            self.outputs = other.outputs[:]
            self.actions = other.actions[:]
            self.events = other.events[:]
            self.states = other.states[:]
            self.tests = other.tests[:]
            self.transitions = other.transitions[:]
            self.classifiers = other.classifiers[:]
            self.action_list = other.action_list[:]
            return

    def Inheritance(self):
        '''
        Expand inheritance by merging transitions from the base class
        that are not in the derived class.
        Then remove any state (ghost) that is not a target.
        '''
        base_states = {}
        for derived in [state for state in self.states if len(state.base_list) > 0]:
            for b in derived.base_list:
                base_states[b] = None
            replaced = [sc.event for sc in self.classifiers + self.transitions if sc.source == derived.name]
            # print "Derived:", derived, replaced
            inherited = [sc for sc in self.classifiers + self.transitions if sc.source in derived.base_list]
            # print "Inherited:", derived, inherited
            virtual = [i for i in inherited if i.event not in replaced]
            # print "Virtual:", derived, virtual
            for item in virtual:
                if isinstance(item, Classifier):
                    self.addClassifier(Classifier(derived.name, item.event, item.actions, item.targets))
                else:
                    self.addTransition(Transition(derived.name, item.event, item.actions, item.targets))
        target_states = {}
        for s in self.transitions:
            for t in s.targets:
                target_states[t] = None
        # print "Targets:", target_states
        ghosts = [s for s in self.transitions if s.source not in target_states]
        # print "Ghosts:", ghosts
        # print "Bases:", base_states
        for s in ghosts:
            if s.source in base_states:
                self.transitions.remove(s)
                # print "Removed:", s

    def TextStateMachine(self):
        the_states = sorted([s.name for s in self.states])
        the_events = sorted([e.name for e in self.events])
        txt = ['STATEMACHINE %s {' % self.name]
        if len(self.outputs) > 0:
            txt += ['  OUPUT ' + ', '.join(self.outputs) + ';']
        txt += ['  STATES']
        for state in the_states:
            s = self.getState(state)
            lines = ['    %s' % state]
            if len(s.comments) == 0:
                lines[0] += ' "No Comment"'
            elif len(s.comments) == 1:
                lines[0] += ' "%s"' %s.comments[0]
            elif len(s.comments) > 1:
                lines += ['      "%s"' % c for c in s.comments]
            if state == the_states[-1]:
                lines[-1] += ';'
            else:
                lines[-1] += ','
            txt += lines
        txt += ['  EVENTS']
        for event in the_events:
            e = self.getEvent(event)
            lines = ['    %s' % event]
            if len(e.comments) == 0:
                lines[0] += ' "No Comment"'
            elif len(e.comments) == 1:
                lines[0] += ' "%s"' %e.comments[0]
            elif len(e.comments) > 1:
                lines += ['      "%s"' % c for c in e.comments]
            if event == the_events[-1]:
                lines[-1] += ';'
            else:
                lines[-1] += ','
            txt += lines
        txt += ['  ACTIONS']
        the_actions = sorted(self.actions)
        for action in the_actions:
            comments = action.comments
            lines = ['    %s' % action.name]
            if len(comments) == 0:
                lines[0] += ' "No Comment"'
            elif len(comments) == 1:
                lines[0] += ' "%s"' % comments[0]
            elif len(comments) > 1:
                lines += ['      "%s"' % c for c in comments]
            if action == the_actions[-1]:
                lines[-1] += ';'
            else:
                lines[-1] += ','
            txt += lines
        for state in the_states:
            s = self.getState(state)
            if s and len(s.base_list) > 0:
                txt += ['  State %s (%s) {' % (state, ', '.join(s.base_list))]
            else:
                txt += ['  State %s {' % state]
            the_blocks = [b for b in self.classifiers if b.source == state]
            the_blocks += [b for b in self.transitions if b.source == state]
            for block in the_blocks:
                line = '%s' % block.event
                if isinstance(block, Classifier):
                    line += ' -> %s' % ', '.join(block.actions)
                    if len(block.targets) > 0:
                        next_events = sorted([e for e in block.targets])
                        line += ' --> %s' % ', '.join(next_events)
                else:
                    if len(block.actions) > 0:
                        line += ' -> %s' % ', '.join(block.actions)
                    if len(block.targets) > 0:
                        line += ' => %s' % ', '.join(block.targets)
                txt += ['    %s;' % line]
            txt += ['  }']
        for action in sorted(self.actions, key=lambda action: action.name.lower()):
            # print "##Action:", repr(action)
            if len(action.code_text) > 0:
                txt += ['  CODE %s {' % (action.name)]
                for code_type in sorted(action.code_text):
                    txt += ['    @%s' % code_type]
                    for line in action.code_text[code_type]:
                        txt += [line]
                    txt += ['    @END']
                txt += ['  }']
        for test in self.tests:
            txt += ['  Test %s;' % ',\n    '.join(test.tests)]
        txt += ['}']
        return txt

if __name__ == "__main__":
    print Event("test")
    print Event("test", ['with', 'args'])
    print State("Idle")
    print Transition("Idle", "test", "none", "Error")
    print Classifier("Idle", "test", "classify_me", "sub_event")
    print StateMachine("fred")
    sm = StateMachine("fred")
    sm.addEvent(Event("fredEvent"))
    sm.addEvent(Event("billEvent"))
    sm.addState(State("fredState"))
    sm.addState(State("billState"))
    sm.addTransition(Transition("fredState", "billEvent", "do_something", "billState"))
    sm.addTransition(Transition("billState", "fredEvent", "do_something", "fredState"))
    sm.addTransition(Transition("billState", "fredEvent", "do_something", "fredState"))
    sm.addClassifier(Classifier("billState", "fredEvent", "do_decide", "nextEvent"))
    sm.printit()
