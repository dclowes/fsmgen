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
        classifier_list = []
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
        hdr += ['#define %s_NUM_STATES %d' % (uname, len(the_states))]
        hdr += ['#define %s_NUM_EVENTS %d' % (uname, len(the_events))]
        hdr += ['#define %s_NUM_ACTIONS %d' % (uname, len(the_actions))]
        hdr += ['#define %s_MAX_ACTIONS %d' % (uname, max_actions)]
        hdr += ['enum %s_STATES {' % uname]
        for idx, state in enumerate(the_states):
            hdr += ['    %s = %d,' % (state, idx + 1)]
        hdr += ['};']
        hdr += ['enum %s_EVENTS {' % uname]
        for idx, event in enumerate(the_events):
            hdr += ['    %s = %d,' % (event, idx + 1)]
        hdr += ['};']
        hdr += ['enum %s_ACTIONS {' % uname]
        for idx, action in enumerate(the_actions):
            hdr += ['    %s = %d,' % (action, idx + 1)]
        hdr += ['};']
        hdr += ['#endif /* %s_H */' % uname]

        txt = ['#include "%s.h"' % self.name]
        txt += ['#include <stdlib.h>']
        txt += ['#include <stdio.h>']
        txt += ['typedef struct {']
        txt += ['    enum %s_STATES si;' % uname]
        txt += ['    enum %s_EVENTS ei;' % uname]
        txt += ['    enum %s_ACTIONS ac[%s_MAX_ACTIONS];' % (uname, uname)]
        txt += ['    enum %s_STATES so;' % uname]
        txt += ['} trans_t;']
        txt += ['static trans_t trans_table[] = {']
        idx = 0
        map_txt = ['static int map_table[] = {', '    0,']
        for state in the_states:
            map_txt += ['    %d, /* %s */' % (idx, state)]
            for event in the_events:
                for block in the_blocks:
                    if block.source == state:
                        if block.event == event:
                            actions = ','.join(block.actions)
                            target = "0"
                            if isinstance(block, Transition) and len(block.targets) > 0:
                                target = block.targets[0]
                            line = '{%s, %s, {%s}, %s},' % (state, event, actions, target)
                            line = '%-60s /* %d %s */' % (line, idx, repr(block))
                            txt += [line]
                            idx += 1
        txt += ['};']
        map_txt += ['    %d' % idx]
        map_txt += ['};']
        txt += map_txt
        txt += ['']
        txt += ['static char *state_names[] = {', '    0,']
        for state in the_states:
            txt += ['    "%s",' % state]
        txt += ['    0', '};']
        txt += ['static char *event_names[] = {', '    0,']
        for event in the_events:
            txt += ['    "%s",' % event]
        txt += ['    0', '};']
        txt += ['static char *action_names[] = {', '    0,']
        for action in the_actions:
            txt += ['    "%s",' % action]
        txt += ['    0', '};']
        txt += ['']
        txt += ['int trans_fn(int state, int event) {']
        txt += ['    int i;']
        txt += ['    for (i = map_table[state]; i < map_table[state + 1]; ++i) {']
        txt += ['        if (trans_table[i].si == state && trans_table[i].ei == event)']
        txt += ['            return i;']
        txt += ['    }']
        txt += ['    return -1;']
        txt += ['}']
        txt += ['void print_tfr(int j) {']
        txt += ['    int k;']
        txt += ['    printf("%s(%s)", state_names[trans_table[j].si], event_names[trans_table[j].ei]);']
        txt += ['    for (k = 0; k < %s_MAX_ACTIONS; ++k) {' % uname]
        txt += ['        char *action = action_names[trans_table[j].ac[k]];']
        txt += ['        if (trans_table[j].ac[k] == 0)']
        txt += ['            break;']
        txt += ['        printf("%s%s", k == 0 ? ": " : ", ", action);']
        txt += ['    }']
        txt += ['    if (trans_table[j].so) {']
        txt += ['        printf(" => %s", state_names[trans_table[j].so]);']
        txt += ['    }']
        txt += ['    printf("\\n");']
        txt += ['}']
        txt += ['']
        txt += ['int main(int argc, char *argv[]) {']
        txt += ['    int i, j, k;']
        txt += ['    for (i = 0; i < %s_NUM_STATES; ++i) {' % uname]
        txt += ['        int state = i + 1;']
        txt += ['        printf("STATE: %s\\n", state_names[state]);']
        txt += ['        for (j = map_table[state]; j < map_table[state + 1]; ++j) {']
        txt += ['            print_tfr(j);']
        txt += ['        }']
        txt += ['    }']
        txt += ['    for (i = 0; i < %s_NUM_STATES; ++i) {' % uname]
        txt += ['        for (j = 0; j < %s_NUM_EVENTS; ++j) {' % uname]
        txt += ['            k = trans_fn(i, j);']
        txt += ['            if (k > 0) {']
        txt += ['                print_tfr(k);']
        txt += ['            }']
        txt += ['        }']
        txt += ['    }']
        txt += ['}']
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
