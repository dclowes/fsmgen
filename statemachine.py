#!/usr/bin/env python
# Author: Douglas Clowes (douglas.clowes@ansto.gov.au) Aug 2015
# vim: ft=python ts=8 sts=4 sw=4 expandtab autoindent smartindent
#

# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=missing-docstring
# pylint: disable=global-statement
#

class Event(object):
    def __init__(self, name, arglist=None):
        self.name = name
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
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

class Transition(object):
    def __init__(self, source, event, actions=None, targets=None):
        self.source = source
        self.event = event
        self.actions = actions
        self.targets = targets

    def __repr__(self):
        return ", ".join([self.source, self.event, repr(self.actions), repr(self.targets)])

class Classifier(object):
    def __init__(self, source, event, actions=None, targets=None):
        self.source = source
        self.event = event
        self.actions = actions
        self.targets = targets

    def __repr__(self):
        return ", ".join([self.source, self.event, repr(self.actions), repr(self.targets)])

class Action(object):
    def __init__(self, name, code_type, code_text=None):
        self.name = name
        self.code_type = code_type
        self.code_text = code_text

    def __repr__(self):
        return "%s(%s) {%s}" % (self.name, self.code_type, self.code_text)

class StateMachine(object):
    def __init__(self, name):
        self.name = name
        self.actions = []
        self.events = []
        self.states = []
        self.transitions = []
        self.classifiers = []

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
        if (transition.source, transition.event) not in [(t.source, t.event) for t in self.transitions]:
            self.transitions.append(transition)
        else:
            print "Duplicate transition:", transition

    def addClassifier(self, classifier):
        assert isinstance(classifier, Classifier)
        assert classifier.source in [s.name for s in self.states]
        assert classifier.event in [e.name for e in self.events]
        if (classifier.source, classifier.event) not in [(t.source, t.event) for t in self.classifiers]:
            self.classifiers.append(classifier)
        else:
            print "Duplicate classifier:", classifier

    def addAction(self, action):
        assert isinstance(action, Action)
        self.actions.append(action)

    def printit(self):
        print "StateMachine:", self.name
        print "States:", ", ".join([repr(s) for s in self.states])
        print "Events:", ", ".join([repr(s) for s in self.events])
        for c in self.classifiers:
            print "Classifier:", c
        for t in self.transitions:
            print "Transition:", t
        for a in self.actions:
            print "Action:", a

class StateMachine_Text(StateMachine):
    def __init__(self, other):
        StateMachine.__init__(self, "Unknown")
        if isinstance(other, StateMachine):
            self.name = other.name
            self.actions = other.actions
            self.events = other.events
            self.states = other.states
            self.transitions = other.transitions
            self.classifiers = other.classifiers

    def StateTable1(self):
        the_states = sorted([s.name for s in self.states])
        txt = ['<TABLE BORDER=1>']
        txt += ['<TR>']
        txt += ['<TH><TABLE WIDTH=100%>']
        txt += ['<TR><TD ALIGN="right">Next(&gt;)</TD></TR>']
        txt += ['<TR><TD ALIGN="left">Current(v)</TD></TR>']
        txt += ['</TABLE></TH>']
        for s_next in the_states:
            txt += ['<TH>%s</TH>' % s_next]
        txt += ['</TR>\n']
        for s_curr in the_states:
            txt += ['<TR><TD VALIGN="top"><B>%s</B></TD>' % s_curr]
            for s_next in the_states:
                txt += ['<TD VALIGN="top"><TABLE>']
                if s_curr == s_next:
                    for block in self.classifiers:
                        if block.source == s_curr:
                            event = block.event
                            action = ',<BR/>'.join(block.actions)
                            txt += ['<TR><TD VALIGN="top"><B>%s</B></TD>' % event]
                            txt += ['<TD VALIGN="top">%s</TD></TR>' % action]
                for block in self.transitions:
                    if block.source == s_curr and s_next in block.targets:
                        event = block.event
                        action = ',<BR/>'.join(block.actions)
                        txt += ['<TR><TD VALIGN="top"><B>%s</B></TD>' % event]
                        txt += ['<TD VALIGN="top">%s</TD></TR>' % action]
                txt += ['</TABLE></TD>']
            txt += ['</TR>']
        txt += ['</TABLE>']
        return txt

    def StateTable2(self):
        the_states = sorted([s.name for s in self.states])
        the_events = sorted([e.name for e in self.events])
        txt = ['<TABLE BORDER=1>']
        txt += ['<TR>']
        txt += ['<TH><TABLE WIDTH=100%>']
        txt += ['<TR><TD VALIGN="right">State(&gt;)</TD></TR>']
        txt += ['<TR><TD VALIGN="left">Event(v)</TD></TR>']
        txt += ['</TABLE></TH>']
        for s in the_states:
            txt += ['<TH>%s</TH>' % s]
        txt += ['</TR>\n']
        for e in the_events:
            txt += ['<TR><TD VALIGN="top"><B>%s</B></TD>' % e]
            for s in the_states:
                txt += ['<TD VALIGN="top"><TABLE>']
                the_blocks = [b for b in self.classifiers + self.transitions if b.source == s]
                for block in the_blocks:
                    if e == block.event:
                        action = ',<BR/>'.join(block.actions)
                        next_state = ''
                        if isinstance(block, Transition):
                            next_state = '<B>' + ',<BR>'.join(block.targets) + '</B>'
                        txt += ['<TR><TD VALIGN="top">%s</TD><TD VALIGN="top">%s</TD></TR>' % (action, next_state)]
                txt += ['</TABLE></TD>']
            txt += ['</TR>']
        txt += ['</TABLE>']
        return txt

    def StateTable3(self):
        the_states = sorted([s.name for s in self.states])
        the_events = sorted([e.name for e in self.events])
        txt = ['<TABLE BORDER=1>\n']
        txt += ['<TR>']
        for t in ['State', 'Event', 'Actions', 'Next']:
            txt += ['<TH>%s</TH>' % t]
        txt += ['</TR>\n']
        for s in the_states:
            for e in the_events:
                the_blocks = [b for b in self.classifiers + self.transitions if b.source == s]
                for block in the_blocks:
                    if e == block.event:
                        txt += ['<TR>']
                        txt += ['<TD VALIGN="top"><B>%s</B></TD>' % s]
                        txt += ['<TD VALIGN="top"><B>%s</B></TD>' % e]
                        action = ',<BR/>'.join(block.actions)
                        txt += ['<TD VALIGN="top">%s</TD>' % action]
                        next_state = ''
                        if isinstance(block, Transition):
                            next_state = '<B>' + ',<BR>'.join(block.targets) + '</B>'
                        else:
                            next_state = s
                        txt += ['<TD VALIGN="top">%s</TD>' % next_state]
                        txt += ['</TR>\n']
        txt += ['</TABLE>\n']
        return txt

    def DotStateMachine(self):
        the_states = sorted([s.name for s in self.states])
        txt = ['digraph G {']
        txt += ['  size="11,8";']
        txt += ['  ratio="expand";']
        txt += ['  rankdir=LR;']
        txt += ['  node [shape=plaintext];']
        txt += ['  labelloc="t";']
        txt += ['  label=<<B>%s</B>>' % self.name]
        txt += ['']
        for state in the_states:
            label = ['<TABLE><TR><TD PORT="f0"><B>']
            label += ['%s' % state]
            label += ['</B></TD></TR>']
            the_blocks = [b for b in self.classifiers if b.source == state]
            the_blocks += [b for b in self.transitions if b.source == state]
            for idx, block in enumerate(the_blocks):
                label += ['<TR><TD><TABLE>']
                label += ['<TR><TD PORT="f%d">' % (idx + 1)]
                label += ['<B>%s</B></TD></TR>' % block.event]
                if len(block.actions) > 0:
                    label += ['<TR><TD>%s</TD></TR>' % '</TD></TR><TR><TD>'.join(block.actions)]
                label += ['</TABLE></TD></TR>']
            label += ['</TABLE>']
            txt += ['  %s[label=<%s>];' % (state, ''.join(label))]
            for idx, block in enumerate(the_blocks):
                if isinstance(block, Transition):
                    for t in block.targets:
                        txt += ['    %s:f%d -> %s:f0;' % (state, idx + 1, t)]
        txt += ['}']
        return txt

    def TextStateMachine(self):
        the_states = sorted([s.name for s in self.states])
        the_events = sorted([e.name for e in self.events])
        txt = ['STATEMACHINE %s {' % self.name]
        txt += ['  STATES\n    %s;' % ',\n    '.join(the_states)]
        txt += ['  EVENTS\n    %s;' % ',\n    '.join(the_events)]
        for state in the_states:
            txt += ['  State %s = {' % state]
            the_blocks = [b for b in self.classifiers if b.source == state]
            the_blocks += [b for b in self.transitions if b.source == state]
            for block in the_blocks:
                line = '%s' % block.event
                if isinstance(block, Classifier):
                    line += ' --> %s' % ', '.join(block.actions)
                    if len(block.targets) > 0:
                        next_events = sorted([e[0] for e in block.targets])
                        line += ' => %s' % ', '.join(next_events)
                else:
                    if len(block.actions) > 0:
                        line += ' -> %s' % ', '.join(block.actions)
                    if len(block.targets) > 0:
                        line += ' => %s' % ', '.join(block.targets)
                txt += ['    %s;' % line]
            txt += ['  }']
        for action in self.actions:
            txt += ['  CODE %s %s = {' % (action.code_type, action.name)]
            txt += ['    @TCL']
            for line in action.code_text[1]:
                txt += [line]
            txt += ['    @END']
            txt += ['  }']
        txt += ['}']
        return txt

class StateMachine_Python(StateMachine_Text):
    def __init__(self, other):
        StateMachine_Text.__init__(self, other)

    def Generate_Python(self):
        the_states = sorted([s.name for s in self.states])
        the_events = sorted([e.name for e in self.events])
        action_list = []
        classifier_list = []
        test_list = []
        func_name = 'StateSwitch_%s'  % self.name
        txt = ['def %s(state, event):' % func_name]
        txt += ['    next_state = state']
        txt += ['    next_event = None']
        for s in the_states:
            txt += ['    if state == "%s":' % s]
            for e in the_events:
                the_blocks = [b for b in self.classifiers + self.transitions if b.source == s]
                for block in the_blocks:
                    if e == block.event:
                        txt += ['        if event == "%s":' % e]
                        for action in block.actions:
                            if isinstance(block, Classifier):
                                txt += ['            next_event = %s(state, event)' % (action)]
                                if action not in [c[0] for c in classifier_list]:
                                    classifier_list.append((action, block.targets))
                            else:
                                txt += ['            %s(state, event)' % (action)]
                                if action not in action_list:
                                    action_list.append(action)
                        if isinstance(block, Transition) and len(block.targets) > 0:
                            txt += ['            next_state = "%s"' % (block.targets[0])]
                            test_list.append((s, e, block.targets[0]))
                        else:
                            test_list.append((s, e, s))
                        txt += ['            return (next_state, next_event)']
        txt += ['    return (next_state, next_event)']
        txt += ['']
        slen = max([len(s) for s in the_states])
        elen = max([len(e) for e in the_events])
        txt += ['if __name__ == "__main__":']
        print "Classifiers:", classifier_list
        for action in classifier_list:
            txt += ['    def %s(state, event):' % action[0]]
            line = '"State %%-%ds event %%-%ds: %s" %% (state, event)' % (slen, elen, action[0])
            txt += ['        print %s' % line]
            txt += ['        return "%s"' % action[1][0][0]]
        print "Actions:", action_list
        for action in action_list:
            txt += ['    def %s(state, event):' % action]
            line = '"State %%-%ds event %%-%ds: %s" %% (state, event)' % (slen, elen, action)
            txt += ['        print %s' % line]
        print "Tests:", test_list
        for test in test_list:
            s1 = test[0]
            ev = test[1]
            s2 = test[2]
            txt += ['    assert %s("%s", "%s")[0] == "%s"' % (func_name, s1, ev, s2)]
        return txt

    def Generate_TCL(self):
        the_states = sorted([s.name for s in self.states])
        the_events = sorted([e.name for e in self.events])
        action_list = []
        classifier_list = []
        test_list = []
        func_name = 'StateSwitch_%s'  % self.name
        txt = ['proc %s {state event} {' % func_name]
        txt += ['    set next_state ${state}']
        txt += ['    set next_event {}']
        for s in the_states:
            txt += ['    if {${state} == "%s"} {' % s]
            for e in the_events:
                the_blocks = [b for b in self.classifiers + self.transitions if b.source == s]
                for block in the_blocks:
                    if e == block.event:
                        txt += ['        if {${event} == "%s"} {' % e]
                        for action in block.actions:
                            if isinstance(block, Classifier):
                                txt += ['            set next_event [%s ${state} ${event}]' % (action)]
                                if action not in [c[0] for c in classifier_list]:
                                    classifier_list.append((action, block.targets))
                            else:
                                txt += ['            %s ${state} ${event}' % (action)]
                                if action not in action_list:
                                    action_list.append(action)
                        if isinstance(block, Transition) and len(block.targets) > 0:
                            txt += ['            set next_state "%s"' % (block.targets[0])]
                            test_list.append((s, e, block.targets[0]))
                        else:
                            test_list.append((s, e, s))
                        txt += ['            return [list ${next_state} ${next_event}]']
                        txt += ['        }']
            txt += ['        return [list ${next_state} ${next_event}]']
            txt += ['    }']
        txt += ['    return [list ${next_state} ${next_event}]']
        txt += ['}']
        slen = max([len(s) for s in the_states])
        elen = max([len(e) for e in the_events])
        txt += ['if { "[lindex [split [info nameofexecutable] "/"] end]" == "tclsh"} {']
        print "Classifiers:", classifier_list
        for action in classifier_list:
            txt += ['    proc %s {state event} {' % action[0]]
            line = 'State [format "%%-%ds" ${state}] event [format "%%-%ds" ${event}]: %s' %\
                    (slen, elen, action[0])
            txt += ['        puts "%s"' % line]
            txt += ['        return "%s"' % action[1][0][0]]
            txt += ['    }']
        print "Actions:", action_list
        for action in action_list:
            txt += ['    proc %s {state event} {' % action]
            line = 'State [format "%%-%ds" ${state}] event [format "%%-%ds" ${event}]: %s' %\
                    (slen, elen, action)
            txt += ['        puts "%s"' % line]
            txt += ['    }']
        print "Tests:", test_list
        for test in test_list:
            s1 = test[0]
            ev = test[1]
            s2 = test[2]
            txt += ['    if {[lindex [%s "%s" "%s"] 0] != "%s"} {error "fail!"}' % (func_name, s1, ev, s2)]
        txt += ['} else {']
        for action in action_list:
            the_blocks = [b for b in self.actions if b.name == action and b.code_type == 'action']
            for code in [c.code_text[1] for c in the_blocks if c.code_text[0] == 'TCL']:
                txt += ['    proc %s {state event} {' % action]
                txt += ['        ' + l for l in code]
                txt += ['    }']
        txt += ['}']
        return txt

    def Generate_C(self):
        the_states = sorted([s.name for s in self.states])
        the_events = sorted([e.name for e in self.events])
        the_actions = []
        classifier_list = {}
        test_list = []
        the_blocks = [b for b in self.classifiers + self.transitions]
        max_actions = 0
        for block in the_blocks:
            if len(block.actions) > max_actions:
                max_actions = len(block.actions)
            for action in block.actions:
                if action not in the_actions:
                    the_actions.append(action)
        the_actions = sorted(the_actions)
        uname = self.name.upper()
        hdr = ['#ifndef %s_H' % uname]
        hdr += ['#define %s_H' % uname]
        hdr += ['#include "statemachine.h"']
        hdr += ['#define %s_NUM_STATES %d' % (uname, len(the_states))]
        hdr += ['#define %s_NUM_EVENTS %d' % (uname, len(the_events))]
        hdr += ['#define %s_NUM_TRANS %d' % (uname, len(the_blocks))]
        hdr += ['#define %s_NUM_ACTIONS %d' % (uname, len(the_actions))]
        hdr += ['#define %s_MAX_ACTIONS %d' % (uname, max_actions)]
        hdr += ['enum %s_STATES {' % uname]
        for idx, state in enumerate(the_states):
            hdr += ['    %s = %d,' % (state, idx + 1)]
        hdr += ['};']
        hdr += ['enum %s_EVENTS {' % uname]
        for idx, event in enumerate(the_events):
            hdr += ['    %s = %d,' % (event, idx + 1)]
        hdr += ['};', '']
        hdr += ['enum %s_ACTIONS {' % uname]
        for idx, action in enumerate(the_actions):
            hdr += ['    %s = %d,' % (action, idx + 1)]
        hdr += ['};', '']
        hdr += ['extern fsmStateMachine fsm_%s;' % self.name, '']
        hdr += ['#endif /* %s_H */' % uname]

        txt = ['#include "%s.h"' % self.name]
        txt += ['#include <stdlib.h>']
        txt += ['#include <stdio.h>']
        txt += ['']
        tab_idx = 0
        act_idx = 0
        act_txt = ['static int action_table[] = {']
        map_txt = ['static int map_table[] = {', '    0,']
        tab_txt = ['static fsmTransTab trans_table[] = {']
        for state in the_states:
            map_txt += ['    %d, /* %s */' % (tab_idx, state)]
            for event in the_events:
                for block in the_blocks:
                    if block.source == state:
                        if block.event == event:
                            actions = ','.join(block.actions)
                            act_cnt = len(block.actions)
                            target = "0"
                            if isinstance(block, Transition) and len(block.targets) > 0:
                                target = block.targets[0]
                            if act_cnt > 0:
                                act_txt += ['    %s,' % actions]
                            if isinstance(block, Transition):
                                act_typ = 'fsmActionTrans'
                            else:
                                act_typ = 'fsmActionClass'
                                for action in block.actions:
                                    if action not in classifier_list:
                                        classifier_list[action] = block.targets[0]
                            line = '    {%s, %s, %s, %s, %d, %d},' %\
                                    (state, event, target, act_typ, act_idx, act_cnt)
                            line = '%-60s /* %d %s */' % (line, tab_idx, repr(block))
                            tab_txt += [line]
                            act_idx += act_cnt
                            tab_idx += 1
        act_txt += ['};', '']
        map_txt += ['    %d' % tab_idx]
        map_txt += ['};', '']
        tab_txt += ['};', '']
        txt += act_txt
        txt += map_txt
        txt += tab_txt
        txt += ['']
        txt += ['static char *state_names[] = {', '    0,']
        for state in the_states:
            txt += ['    "%s",' % state]
        txt += ['    0', '};', '']
        txt += ['static char *event_names[] = {', '    0,']
        for event in the_events:
            txt += ['    "%s",' % event]
        txt += ['    0', '};', '']
        txt += ['static char *action_names[] = {', '    0,']
        for action in the_actions:
            txt += ['    "%s",' % action]
        txt += ['    0', '};', '']
        txt += ['struct fsmActionTab_t {']
        txt += ['    fsmActionFunc *action;']
        txt += ['};', '']
        txt += ['static fsmActionFunc action_funcs[%s_NUM_ACTIONS+1];' % uname]
        txt += ['']
        txt += ['fsmStateMachine fsm_%s = {' % self.name]
        txt += ['    .name="%s",' % self.name]
        txt += ['    %s_NUM_STATES,' % uname]
        txt += ['    %s_NUM_EVENTS,' % uname]
        txt += ['    %s_NUM_TRANS,' % uname]
        txt += ['    %s_NUM_ACTIONS,' % uname]
        txt += ['    %s_MAX_ACTIONS,' % uname]
        txt += ['    map_table,']
        txt += ['    action_table,']
        txt += ['    state_names,']
        txt += ['    event_names,']
        txt += ['    action_names,']
        txt += ['    trans_table,']
        txt += ['    action_funcs']
        txt += ['};', '']
        for action in the_actions:
            txt += ['static int %s_test(fsmInstance *smi, fsmState state, fsmEvent event) {' %action]
            if action in classifier_list:
                next_event = classifier_list[action][0]
                txt += ['    printf("State: %%-20s, Event: %%-20s, Action: %-20s, NextEvent: %s\\n", smi->fsm->stateNames[state], smi->fsm->eventNames[event]);' % (action, next_event)]
                txt += ['    return %s;' % next_event]
            else:
                txt += ['    printf("State: %%-20s, Event: %%-20s, Action: %-20s\\n", smi->fsm->stateNames[state], smi->fsm->eventNames[event]);' % action]
                txt += ['    return 0;']
            txt += ['}', '']
        txt += ['void register_%s_actions(void) {' % (self.name)]
        txt += ['    fsmStateMachine *fsm = &fsm_%s;' % (self.name)]
        for action in the_actions:
            txt += ['    fsmSetActionFunction(fsm, %s, %s_test);' % (action, action)]
        txt += ['};', '']
        txt += ['void test_%s_actions(void) {' % (self.name)]
        txt += ['    fsmStateMachine *fsm = &fsm_%s;' % (self.name)]
        txt += ['    fsmInstance smi = { .name="test", .fsm=fsm };']
        txt += ['    fsmState state;']
        txt += ['    fsmEvent event;']
        txt += ['    int idx;']
        txt += ['    register_%s_actions();' % (self.name), '']
        txt += ['    for (state = 1; state <= fsm->numStates; ++state)']
        txt += ['        for (event = 1; event <= fsm->numEvents; ++event)']
        txt += ['            for (idx = 0; idx < fsm->numTrans; ++idx) {']
        txt += ['                fsmTransTab *tab = &fsm->transTab[idx];']
        txt += ['                if (tab->si == state && tab->ei == event) {']
        txt += ['                    smi.currentState = state;']
        txt += ['                    fsmRunStateMachine(&smi, event);']
        txt += ['                    if (smi.currentState != state)']
        txt += ['                        printf("       %s ===> %s\\n", fsm->stateNames[state], fsm->stateNames[smi.currentState]);']
        txt += ['                }']
        txt += ['            }']
        txt += ['};', '']
        return (hdr, txt)

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
