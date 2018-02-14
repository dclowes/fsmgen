# Author: Douglas Clowes (douglas.clowes@ansto.gov.au) Aug 2015
# vim: ft=python ts=8 sts=4 sw=4 expandtab autoindent smartindent nocindent
#

from statemachine import Action, Classifier, Transition
from statemachine import Event, State
from statemachine import StateMachine, StateMachine_Text

doActions = True
doClassifiers = False
doSelf = False

class StateMachine_UML(StateMachine_Text):
    def __init__(self, other):
        StateMachine_Text.__init__(self, other)
        self.Inheritance()

    def Generate(self):
        the_states = {}
        for state in self.states:
            the_states[state.name] = state
        txt = ['@startuml']
        txt += ['title %s' % self.uname]
        for state in sorted(the_states):
            txt += ['state %s : %s' % (state, '\\n'.join(the_states[state].comments))]
            if 'INITIAL' in [f.upper() for f in the_states[state].flags]:
                txt += ["[*] -> %s" % state]
        txt += ['']
        for state in sorted(the_states):
            if doClassifiers: # Classifiers
                the_blocks = [b for b in sorted(self.classifiers, key=lambda x:x.event) if b.source == state]
                for block in the_blocks:
                    line = '%s --> %s : %s' %\
                            (state,
                                state,
                                block.event)
                    if doActions:
                        if len(block.targets) == 0:
                            line += '(%s)' %\
                                    ','.join(block.actions)
                        else:
                            line += '(%s):\\n%s' %\
                                    (','.join(block.actions),
                                    ',\\n'.join(block.targets))
                    txt.append(line)
            the_blocks = [b for b in sorted(self.transitions, key=lambda x:x.event) if b.source == state]
            for block in the_blocks:
                if len(block.targets) == 0:
                    tgts = state
                    if doSelf == False:
                        continue
                else:
                    tgts = ','.join(block.targets)
                line = '%s --> %s : %s' %\
                        (state,
                            tgts,
                            block.event)
                if doActions:
                    if len(block.actions) > 0:
                        line += '\\n(%s)' %\
                                ',\\n'.join(block.actions)
                txt.append(line)
        txt += ['@enduml']
        return txt
