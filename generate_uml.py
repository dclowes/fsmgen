# Author: Douglas Clowes (douglas.clowes@ansto.gov.au) Aug 2015
# vim: ft=python ts=8 sts=4 sw=4 expandtab autoindent smartindent nocindent
#

from statemachine import Action, Classifier, Transition
from statemachine import Event, State
from statemachine import StateMachine, StateMachine_Text

class StateMachine_UML(StateMachine_Text):
    def __init__(self, other):
        StateMachine_Text.__init__(self, other)
        self.Inheritance()

    def Generate(self):
        the_states = sorted([s.name for s in self.states])
        txt = ['@startuml']
        txt += ['title %s' % self.uname]
        for state in the_states:
            txt += ['state %s' % state]
        txt += ['']
        for state in the_states:
            the_blocks = [b for b in sorted(self.classifiers) if b.source == state]
            for block in the_blocks:
                if len(block.targets) == 0:
                    txt += ['%s --> %s : %s(%s)' %
                            (state,
                             state,
                             block.event,
                             ','.join(block.actions))]
                else:
                    txt += ['%s --> %s : %s(%s):\\n%s' %
                            (state,
                             state,
                             block.event,
                             ','.join(block.actions),
                             ',\\n'.join(block.targets))]
            the_blocks = [b for b in sorted(self.transitions) if b.source == state]
            for block in the_blocks:
                if len(block.targets) == 0:
                    tgts = state
                else:
                    tgts = ','.join(block.targets)
                if len(block.actions) == 0:
                    txt += ['%s --> %s : %s' %
                            (state,
                             tgts,
                             block.event)]
                else:
                    txt += ['%s --> %s : %s\\n(%s)' %
                            (state,
                             tgts,
                             block.event,
                             ',\\n'.join(block.actions))]
        txt += ['@enduml']
        return txt
