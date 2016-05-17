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
    def __init__(self, name, base_list=None):
        self.name = name
        if base_list == None:
            self.base_list = []
        else:
            self.base_list = base_list

    def __repr__(self):
        if len(self.base_list) > 0:
            return self.name + '(' + ', '.join(self.base_list) + ')'
        else:
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

class Test(object):
    def __init__(self, tests):
        self.tests = tests

    def __repr__(self):
        return ", ".join(self.tests)

class StateMachine(object):
    def __init__(self, name):
        self.name = name
        self.uname = name.upper()
        self.actions = []
        self.events = []
        self.states = []
        self.tests = []
        self.transitions = []
        self.classifiers = []

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
        for t in self.tests:
            print "Test:", t

class StateMachine_Text(StateMachine):
    def __init__(self, other):
        StateMachine.__init__(self, other.name)
        if isinstance(other, StateMachine):
            self.name = other.name[:]
            self.actions = other.actions[:]
            self.events = other.events[:]
            self.states = other.states[:]
            self.tests = other.tests[:]
            self.transitions = other.transitions[:]
            self.classifiers = other.classifiers[:]

    def Inheritance(self):
        base_states = {}
        for derived in [state for state in self.states if len(state.base_list) > 0]:
            for b in derived.base_list:
                base_states[b] = None
            replaced = [sc.event for sc in self.classifiers + self.transitions if sc.source == derived.name]
            print "Derived:", derived, replaced
            inherited = [sc for sc in self.classifiers + self.transitions if sc.source in derived.base_list]
            print "Inherited:", derived, inherited
            virtual = [i for i in inherited if i.event not in replaced]
            print "Virtual:", derived, virtual
            for item in virtual:
                if isinstance(item, Classifier):
                    self.addClassifier(Classifier(derived.name, item.event, item.actions, item.targets))
                else:
                    self.addTransition(Transition(derived.name, item.event, item.actions, item.targets))
        target_states = {}
        for s in self.transitions:
            for t in s.targets:
                target_states[t] = None
        print "Targets:", target_states
        ghosts = [s for s in self.transitions if s.source not in target_states]
        print "Ghosts:", ghosts
        print "Bases:", base_states
        for s in ghosts:
            if s.source in base_states:
                self.transitions.remove(s)
                print "Removed:", s

    def TextStateMachine(self):
        the_states = sorted([s.name for s in self.states])
        the_events = sorted([e.name for e in self.events])
        txt = ['STATEMACHINE %s {' % self.name]
        txt += ['  STATES\n    %s;' % ',\n    '.join(the_states)]
        txt += ['  EVENTS\n    %s;' % ',\n    '.join(the_events)]
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
        for action in sorted(self.actions, key=lambda action: action.name.lower()):
            print "##Action:", action
            txt += ['  CODE %s %s {' % (action.code_type, action.name)]
            for action_item in action.code_text:
                txt += ['    @%s' % action_item[0]]
                for line in action_item[1]:
                    txt += [line]
                txt += ['    @END']
            txt += ['  }']
        for test in self.tests:
            txt += ['  Test %s;' % ',\n    '.join(test.tests)]
        txt += ['}']
        return txt

class StateMachine_HTML(StateMachine_Text):
    def __init__(self, other):
        StateMachine_Text.__init__(self, other)
        self.Inheritance()

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

    def DotStateMachine2(self):
        the_states = sorted([s.name for s in self.states])
        txt = ['digraph G {']
        txt += ['  size="11,8";']
        txt += ['  ratio="expand";']
        txt += ['  rankdir=LR;']
        txt += ['  node [shape=plaintext];']
        txt += ['  labelloc="t";']
        txt += ['  label=<<B>%s</B>>' % self.name]
        txt += ['']
        colors = ['red', 'green', 'blue', 'orange', 'purple', 'magenta', 'cyan', 'yellow']
        for state in the_states:
            label = ['<TABLE><TR><TD PORT="%s"><B>' % state]
            label += ['%s' % state]
            label += ['</B></TD></TR>']
            the_blocks = [b for b in sorted(self.classifiers) if b.source == state]
            the_blocks += [b for b in sorted(self.transitions) if b.source == state]
            idx = 0
            for block in the_blocks:
                label += ['<TR><TD><TABLE>']
                label += ['<TR><TD PORT="%s">' % block.event]
                label += ['<B>%s</B></TD></TR>' % block.event]
                if len(block.actions) > 0:
                    label += ['<TR><TD>%s</TD></TR>' % '</TD></TR><TR><TD>'.join(block.actions)]
                label += ['</TABLE></TD></TR>']
            label += ['</TABLE>']
            txt += ['  %s[label=<%s>];' % (state, ''.join(label))]
            for block in the_blocks:
                if isinstance(block, Transition):
                    for t in block.targets:
                        txt += ['    %s:%s -> %s:%s;' % (state, block.event, t, t)]
                else:
                    style = 'dir=both;arrowtail=inv;style=dotted;color=%s' % colors[idx]
                    idx += 1
                    if idx >= len(colors):
                        idx = 0
                    for t in block.targets:
                        if t[0] in [b.event for b in the_blocks]:
                            txt += ['    %s:%s -> %s:%s[%s];' % (state, block.event, state, t[0], style)]
        txt += ['}']
        return txt

class StateMachine_Python(StateMachine_Text):
    def __init__(self, other):
        StateMachine_Text.__init__(self, other)
        self.Inheritance()

    def Generate_Python(self):
        the_states = sorted([s.name for s in self.states])
        the_events = sorted([e.name for e in self.events])
        action_list = []
        classifier_list = []
        test_list = []
        txt = []
        txt += ['# Generated by program']
        txt += ['# pylint: disable=invalid-name']
        txt += ['# pylint: disable=line-too-long']
        txt += ['# pylint: disable=too-many-lines']
        txt += ['# pylint: disable=too-many-locals']
        txt += ['# pylint: disable=too-many-branches']
        txt += ['# pylint: disable=too-many-statements']
        txt += ['# pylint: disable=too-many-return-statements']
        txt += ['# pylint: disable=missing-docstring']
        txt += ['# pylint: disable=global-statement']
        txt += ['# pylint: disable=unused-argument']
        func_name = 'StateSwitch_%s'  % self.name
        txt += ['def %s(context, state, event):' % func_name]
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
                                txt += ['            next_event = %s(context, state, event)' % (action)]
                                if action not in [c[0] for c in classifier_list]:
                                    classifier_list.append((action, block.targets))
                            else:
                                txt += ['            %s(context, state, event)' % (action)]
                                if action not in action_list:
                                    action_list.append(action)
                        if isinstance(block, Transition) and len(block.targets) > 0:
                            txt += ['            next_state = "%s"' % (block.targets[0])]
                            test_list.append((s, e, block.targets[0]))
                        else:
                            test_list.append((s, e, s))
                        txt += ['            return (next_state, next_event, 1)']
            txt += ['        return (next_state, next_event, 0)']
        txt += ['    return (next_state, next_event, 0)']
        txt += ['']
        txt += ['def RunStateSwitch_%s(context, state, event):' % self.name]
        txt += ['    next_state = state']
        txt += ['    next_event = event']
        txt += ['    rule_count = 0']
        txt += ['    while next_event is not None:']
        txt += ['        state_event = StateSwitch_%s(context, state, next_event)' % self.name]
        txt += ['        next_event = state_event[1]']
        txt += ['        rule_count = rule_count + state_event[2]']
        txt += ['    next_state = state_event[0]']
        txt += ['    if next_state != state:']
        txt += ['        state_event = StateSwitch_%s(context, state, "Exit")' % self.name]
        txt += ['        state_event = StateSwitch_%s(context, next_state, "Entry")' % self.name]
        txt += ['    return (next_state, next_event, rule_count)']
        txt += ['']
        slen = max([len(s) for s in the_states])
        elen = max([len(e) for e in the_events])
        txt += ['if __name__ == "__main__":']
        print "Classifiers:", classifier_list
        for action in classifier_list:
            txt += ['    def %s(context, state, event):' % action[0]]
            line = '"State %%-%ds event %%-%ds: %s" %% (state, event)' % (slen, elen, action[0])
            txt += ['        print %s' % line]
            txt += ['        return "%s"' % action[1][0][0]]
        print "Actions:", action_list
        for action in action_list:
            txt += ['    def %s(context, state, event):' % action]
            line = '"State %%-%ds event %%-%ds: %s" %% (state, event)' % (slen, elen, action)
            txt += ['        print %s' % line]
        print "Tests:", test_list
        txt += ['    def TestStateSwitch_%s():' % self.name]
        for test in test_list:
            s1 = test[0]
            ev = test[1]
            s2 = test[2]
            txt += ['        state_event = %s("Context", "%s", "%s")' % (func_name, s1, ev)]
            txt += ['        assert state_event[2] > 0']
            txt += ['        assert state_event[0] == "%s"' % (s2)]
        txt += ['    TestStateSwitch_%s()' % self.name]
        txt += ['    print "TestStateSwitch_%s() passed"' % self.name]
        for test in self.tests:
            print "Test::", test
            txt += ['    state_event = ("%s", None, 0)' % test.tests[0]]
            for t in test.tests:
                if t in the_states:
                    txt += ['    assert state_event[0] == "%s"' % t]
                else:
                    txt += ['    state_event = %s("Context", state_event[0], "%s")' % (func_name, t)]
                    txt += ['    assert state_event[2] > 0']
            txt += ['    print "Test Passed: %s"' % repr(test)]
        txt2 = ['else:']
        for action in action_list:
            the_blocks = [b for b in self.actions if b.name == action and b.code_type == 'action']
            if len(the_blocks) == 0:
                continue
            txt2 += ['    def %s (context, state, event):' % action]
            print "##The Blocks:", the_blocks
            for code_block in the_blocks:
                print "##CodeBlock:", code_block
                print "##CodeText:", code_block.code_text
                for code_text in [c[1] for c in code_block.code_text if c[0] == 'PYTHON']:
                    print "##CodeText:", code_text
                    # Calculate the minimum white space for indent adjustment
                    min_wh = min([len(s) - len(s.lstrip(' ')) for s in code_text])
                    for code in code_text:
                        print "##Code:", code[min_wh:]
                        txt2 += ['        ' + code[min_wh:]]
        if len(txt2) > 1:
            txt += txt2
        txt += ['# vim: ft=python ts=8 sts=4 sw=4 expandtab autoindent smartindent nocindent']
        return txt

class StateMachine_TCL(StateMachine_Text):
    def __init__(self, other):
        StateMachine_Text.__init__(self, other)
        self.Inheritance()

    def Generate_TCL(self):
        the_states = sorted([s.name for s in self.states])
        the_events = sorted([e.name for e in self.events])
        action_list = []
        classifier_list = []
        test_list = []
        func_name = 'StateSwitch_%s'  % self.name
        txt = ['proc %s {context state event} {' % func_name]
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
                                txt += ['            set next_event [%s ${context} ${state} ${event}]' % (action)]
                                if action not in [c[0] for c in classifier_list]:
                                    classifier_list.append((action, block.targets))
                            else:
                                txt += ['            %s ${context} ${state} ${event}' % (action)]
                                if action not in action_list:
                                    action_list.append(action)
                        if isinstance(block, Transition) and len(block.targets) > 0:
                            txt += ['            set next_state "%s"' % (block.targets[0])]
                            test_list.append((s, e, block.targets[0]))
                        else:
                            test_list.append((s, e, s))
                        txt += ['            return [list ${next_state} ${next_event} 1]']
                        txt += ['        }']
            txt += ['        return [list ${next_state} ${next_event} 0]']
            txt += ['    }']
        txt += ['    return [list ${next_state} ${next_event} 0]']
        txt += ['}', '']
        txt += ['proc RunStateSwitch_%s {context state event} {' % self.name]
        txt += ['    set next_state ${state}']
        txt += ['    set next_event ${event}']
        txt += ['    set rule_count 0']
        txt += ['    while { ${next_event} != {} } {']
        txt += ['        set state_event [StateSwitch_%s ${context} ${state} ${next_event}]' % self.name]
        txt += ['        set next_event [lindex ${state_event} 1]']
        txt += ['        set rule_count [expr {${rule_count} + [lindex ${state_event} 2]}]']
        txt += ['    }']
        txt += ['    set next_state [lindex ${state_event} 0]']
        txt += ['    if { ${next_state} != ${state} } {']
        txt += ['        set state_event [StateSwitch_%s ${context} ${state} "Exit"]' % self.name]
        txt += ['        set state_event [StateSwitch_%s ${context} ${next_state} "Entry"]' % self.name]
        txt += ['    }']
        txt += ['    return [list ${next_state} ${next_event} ${rule_count}]']
        txt += ['}', '']
        slen = max([len(s) for s in the_states])
        elen = max([len(e) for e in the_events])
        txt += ['if { "[lindex [split [info nameofexecutable] "/"] end]" == "tclsh"} {']
        print "Classifiers:", classifier_list
        for action in classifier_list:
            txt += ['    proc %s {context state event} {' % action[0]]
            line = 'State [format "%%-%ds" ${state}] event [format "%%-%ds" ${event}]: %s' %\
                    (slen, elen, action[0])
            txt += ['        puts "%s"' % line]
            txt += ['        return "%s"' % action[1][0][0]]
            txt += ['    }']
        print "Actions:", action_list
        for action in action_list:
            txt += ['    proc %s {context state event} {' % action]
            line = 'State [format "%%-%ds" ${state}] event [format "%%-%ds" ${event}]: %s' %\
                    (slen, elen, action)
            txt += ['        puts "%s"' % line]
            txt += ['    }']
        print "Tests:", test_list
        for test in test_list:
            s1 = test[0]
            ev = test[1]
            s2 = test[2]
            txt += ['    set state_event [%s "Ctx" "%s" "%s"]' % (func_name, s1, ev)]
            txt += ['    if {[lindex ${state_event} 2] <= 0} {error "count fail!"}']
            txt += ['    if {[lindex ${state_event} 0] != "%s"} {error "state fail!"}' % (s2)]
        txt += ['    puts "TestStateSwitch_%s() passed"' % self.name]
        for test in self.tests:
            print "Test::", test
            txt += ['    set state_event [list "%s" {} 0]' % test.tests[0]]
            for t in test.tests:
                if t in the_states:
                    txt += ['    if {[lindex ${state_event} 0] != "%s"} {error "state fail!"}' % t]
                else:
                    txt += ['    set state_event [%s "Ctx" [lindex ${state_event} 0] "%s"]' % (func_name, t)]
                    txt += ['    if {[lindex ${state_event} 2] <= 0} {error "count fail!"}']
            txt += ['    puts "Test Passed: %s"' % repr(test)]
        txt2 = ['} else {']
        for action in action_list:
            the_blocks = [b for b in self.actions if b.name == action and b.code_type == 'action']
            if len(the_blocks) == 0:
                continue
            txt2 += ['    proc %s {context state event} {' % action]
            print "##The Blocks:", the_blocks
            for code_block in the_blocks:
                print "##CodeBlock:", code_block
                print "##CodeText:", code_block.code_text
                for code_text in [c[1] for c in code_block.code_text if c[0] == 'TCL']:
                    print "##CodeText:", code_text
                    # Calculate the minimum white space for indent adjustment
                    min_wh = min([len(s) - len(s.lstrip(' ')) for s in code_text])
                    for code in code_text:
                        print "##Code:", code[min_wh:]
                        txt2 += ['        ' + code[min_wh:]]
            txt2 += ['    }']
        if len(txt2) > 1:
            txt += txt2
        txt += ['}']
        return txt

class StateMachine_GCC(StateMachine_Text):
    def __init__(self, other):
        StateMachine_Text.__init__(self, other)
        self.Inheritance()
        self.prefix = 'FSM_'
        self.prefix = ''

    def mkFunc(self, name=None):
        if name:
            return  self.prefix + '%s_%s' % (self.uname, name)
        return self.prefix + '%s' % (self.uname)

    def mkName(self, name=None):
        if name:
            return  self.prefix + '%s_%s' % (self.uname, name)
        return self.prefix + '%s' % (self.uname)

    def mkState(self, name=None):
        if name:
            return  self.prefix + '%s_STATE_%s' % (self.uname, name)
        return  self.prefix + '%s_STATE' % (self.uname)

    def mkEvent(self, name=None):
        if name:
            return  self.prefix + '%s_EVENT_%s' % (self.uname, name)
        return  self.prefix + '%s_EVENT' % (self.uname)

    def mkAction(self, name=None):
        if name:
            return  self.prefix + '%s_ACTION_%s' % (self.uname, name)
        return  self.prefix + '%s_ACTION' % (self.uname)

    def Generate_Hdr(self, stts, evts, acts):
        hdr = []
        hdr += ['#ifndef %s_H' % self.uname]
        hdr += ['#define %s_H' % self.uname]
        # States
        hdr += ['', '/* States */']
        hdr += ['typedef const struct %s_t *%s;'\
                % (self.mkState(), self.mkState())]
        for item in stts:
            hdr += ['extern  const %s %s;'\
                    % (self.mkState(), self.mkState(item[0]))]
        # Events
        hdr += ['', '/* Events */']
        hdr += ['typedef const struct %s_t *%s;'\
                % (self.mkEvent(), self.mkEvent())]
        for item in evts:
            hdr += ['extern  const %s %s;'\
                    % (self.mkEvent(), self.mkEvent(item[0]))]
        # Actions
        hdr += ['', '/* Actions */']
        hdr += ['typedef const struct %s_t *%s;'\
                % (self.mkAction(), self.mkAction())]
        for item in acts:
            hdr += ['extern  const %s %s;'\
                    % (self.mkAction(), self.mkAction(item[0]))]
        # Instance
        hdr += ['', '/* Statemachine Instance */']
        hdr += ['typedef struct %s_t *%s;'\
                % (self.mkName(), self.mkName())]
        # Functions
        hdr += ['', '/* Statemachine Functions */']
        hdr += ['', '/* User Supplied Action/Classifier Functions */']
        hdr += ['typedef %s (*%s)('\
                % (self.mkEvent(), self.mkFunc('Action'))]
        hdr += ['    %s smi,' % self.mkName()]
        hdr += ['    %s state, ' % self.mkState()]
        hdr += ['    %s event);' % self.mkEvent()]
        # Constructor
        hdr += ['', '/* Statemachine Instance Constructor */']
        hdr += ['%s %s(const char *name, %s initial);'\
                % (self.mkName(), self.mkFunc('InstanceMake'), self.mkState())]
        hdr += ['', '/* Statemachine Instance Destructor */']
        hdr += ['void %s(%s smi);' % (self.mkName('InstanceKill'), self.mkFunc())]
        hdr += ['', '/* Statemachine Instance Driver */']
        hdr += ['void %s(%s smi,'\
                % (self.mkFunc('InstanceRun'), self.mkName())]
        hdr += ['    %s ev);'\
                % (self.mkEvent())]
        #
        hdr += ['', '/* Statemachine Class Action Setter */']
        hdr += ['void %s('\
                % (self.mkFunc('ClassSetAction'))]
        hdr += ['    %s action,'\
                % (self.mkAction())]
        hdr += ['    %s af);'\
                % (self.mkFunc('Action'))]
        hdr += ['', '/* Statemachine Instance Action Setter */']
        hdr += ['void %s(%s smi,'\
                % (self.mkFunc('InstanceSetAction'), self.mkName())]
        hdr += ['    %s action,'\
                % (self.mkAction())]
        hdr += ['    %s af);'\
                % (self.mkFunc('Action'))]
        #hdr += ['extern fsmStateMachine fsm_%s;' % self.name]
        hdr += ['', '#endif /* %s_H */' % self.uname]
        return hdr

    def Generate_Code(self):
        txt = []
        txt += ['/* Create an Instance of this Statemachine */']
        txt += ['%s %s(const char *name, %s initial)'\
                % (self.mkName(), self.mkFunc('InstanceMake'), self.mkState())]
        txt += ['{']
        txt += ['    %s smi = (%s) calloc(1, sizeof(struct %s_t));'\
                % (self.mkName(), self.mkName(), self.mkName())]
        txt += ['    if (smi == NULL)']
        txt += ['        return NULL;']
        txt += ['    /* TODO initialisation */']
        txt += ['    smi->name = strdup(name);']
        txt += ['    smi->fsm = &fsm_%s;' % self.name]
        txt += ['    smi->actionTab = (%s *) calloc(%s, sizeof(%s));'\
                % (self.mkFunc('Action'), self.mkName('NUM_ACTIONS'), self.mkFunc('Action'))]
        txt += ['    smi->currentState = initial;']
        txt += ['    return smi;']
        txt += ['}']
        txt += ['']
        txt += ['/* Destroy an Instance of this Statemachine */']
        txt += ['void %s(%s smi)' % (self.mkFunc('InstanceKill'), self.mkName())]
        txt += ['{']
        txt += ['    if (smi == NULL)']
        txt += ['        return;']
        txt += ['    free(smi->name);']
        txt += ['    free(smi->actionTab);']
        txt += ['    free(smi);']
        txt += ['}']
        txt += ['']
        txt += ['/* Run one Event for this Instance of this Statemachine */']
        txt += ['%s %s(%s smi, %s ev)'\
                % (self.mkState(), self.mkFunc('RunStateEvent'), self.mkName(), self.mkEvent())]
        txt += ['{']
        txt += ['    int i, j, k;']
        txt += ['    %s next_event = NULL;' % self.mkEvent()]
        txt += ['    %s next_state = smi->currentState;' % self.mkState()]
        txt += ['    const fsmStateMachine *fsm = smi->fsm;']
        txt += ['    int s_beg = fsm->mapTab[smi->currentState->index];']
        txt += ['    int s_end = fsm->mapTab[smi->currentState->index + 1];']
        txt += ['    do {']
        txt += ['        next_event = NULL;']
        txt += ['        if (ev == NULL) {']
        txt += ['            return next_state;']
        txt += ['        }']
        txt += ['        for (i = s_beg; i < s_end; ++i) {']
        txt += ['            if (fsm->transTab[i].ei == ev) {']
        txt += ['                fsmTransTab *tab = &fsm->transTab[i];']
        txt += ['                fsmActionType actionType = tab->ac_type;']
        txt += ['                %s fn;' % self.mkFunc('Action')]
        txt += ['                switch (actionType) {']
        txt += ['                    case fsmActionClass:']
        txt += ['                        k = tab->ac_class;']
        txt += ['                        fn = fsm->actionTab[k];']
        txt += ['                        if (smi->actionTab && smi->actionTab[k])']
        txt += ['                            fn = smi->actionTab[k];']
        txt += ['                        next_event = (*fn)(smi, smi->currentState, ev);']
        txt += ['                        ev = next_event;']
        txt += ['                        break;']
        txt += ['                    case fsmActionTrans:']
        txt += ['                        if (tab->so)']
        txt += ['                            next_state = tab->so;']
        txt += ['                        for (j = 0; j < tab->ac_count; ++ j) {']
        txt += ['                            k = fsm->actTab[tab->ac_start + j]->index;']
        txt += ['                            fn = fsm->actionTab[k];']
        txt += ['                            if (smi->actionTab && smi->actionTab[k])']
        txt += ['                                fn = smi->actionTab[k];']
        txt += ['                            (void) (*fn)(smi, smi->currentState, ev);']
        txt += ['                        }']
        txt += ['                        break;']
        txt += ['                }']
        txt += ['                break;']
        txt += ['            }']
        txt += ['        }']
        txt += ['    } while (next_event);']
        txt += ['    return next_state;']
        txt += ['}']
        txt += ['']
        txt += ['void %s(%s smi, %s ev)'\
                % (self.mkFunc('InstanceRun'), self.mkName(), self.mkEvent())]
        txt += ['{']
        txt += ['    %s next_state = %s(smi, ev);'\
                % (self.mkState(), self.mkFunc('RunStateEvent'))]
        txt += ['    if (next_state != smi->currentState) {']
        txt += ['        if (smi->fsm->exitEvent)']
        txt += ['            %s(smi, smi->fsm->exitEvent);'\
                % self.mkFunc('RunStateEvent')]
        txt += ['        smi->currentState = next_state;']
        txt += ['        if (smi->fsm->entryEvent)']
        txt += ['            %s(smi, smi->fsm->entryEvent);'\
                % self.mkFunc('RunStateEvent')]
        txt += ['    }']
        txt += ['}']
        txt += ['']
        txt += ['void %s(' % self.mkFunc('ClassSetAction')]
        txt += ['        %s action,' % self.mkAction()]
        txt += ['        %s func)' % self.mkFunc('Action')]
        txt += ['{']
        txt += ['    if (action->index > 0 && action->index <= %s)'\
                % self.mkName('NUM_ACTIONS')]
        txt += ['        action_funcs[action->index] = func;']
        txt += ['}']
        txt += ['']
        txt += ['void %s(' % self.mkFunc('InstanceSetAction')]
        txt += ['        %s smi,' % self.mkName()]
        txt += ['        %s action,' % self.mkAction()]
        txt += ['        %s func)' % self.mkFunc('Action')]
        txt += ['{']
        txt += ['    if (action->index > 0 && action->index <= %s)'\
                % self.mkName('NUM_ACTIONS')]
        txt += ['        smi->actionTab[action->index] = func;']
        txt += ['}']
        return txt

    def Generate_C(self):
        the_states = sorted([s.name for s in self.states])
        the_events = sorted([e.name for e in self.events])
        the_actions = []
        classifier_list = {}
        the_blocks = [b for b in self.classifiers + self.transitions]
        max_actions = 0
        for block in the_blocks:
            if len(block.actions) > max_actions:
                max_actions = len(block.actions)
            for action in block.actions:
                if action not in the_actions:
                    the_actions.append(action)
        the_actions = sorted(the_actions)
        tkns = []
        tkns += [('NUM_STATES', len(the_states))]
        tkns += [('NUM_EVENTS', len(the_events))]
        tkns += [('NUM_TRANS', len(the_blocks))]
        tkns += [('NUM_ACTIONS', len(the_actions))]
        tkns += [('MAX_ACTIONS', max_actions)]
        stts = []
        for idx, state in enumerate(the_states):
            stts += [(state, idx + 1)]
        evts = []
        for idx, event in enumerate(the_events):
            evts += [(event, idx + 1)]
        acts = []
        for idx, action in enumerate(the_actions):
            acts += [(action, idx + 1)]
        print "tkns:", tkns
        print "stts:", stts
        print "evts:", evts
        print "acts:", acts

        hdr = self.Generate_Hdr(stts, evts, acts)

        txt = []
        txt += ['#include <stdlib.h>']
        txt += ['#include <stdio.h>']
        txt += ['#include <string.h>']
        txt += ['']
        for item in tkns:
            txt += ['#define %s %d'\
                    % (self.mkName(item[0]), item[1])]
        txt += ['']
        # States
        txt += ['', '/* States */']
        txt += ['struct %s_t {' % self.mkState()]
        txt += ['    char *name;']
        txt += ['    int  index;']
        txt += ['};']
        txt += ['enum {']
        for item in stts:
            txt += ['    e%s = %s,' % (self.mkState(item[0]), item[1])]
        txt += ['};']
        txt += ['static const struct %s_t state_pointers [] = {' % self.mkState()]
        txt += ['    { NULL, %s },' % self.mkName('NUM_STATES')]
        for item in stts:
            txt += ['    { "%s", %d },'\
                    % (item[0], item[1])]
        txt += ['    { NULL, 0 }']
        txt += ['};']
        for item in stts:
            txt += ['const %s %s = &state_pointers[%d];'\
                    % (self.mkState(), self.mkState(item[0]), item[1])]
        # Events
        txt += ['', '/* Events */']
        txt += ['struct %s_t {' % self.mkEvent()]
        txt += ['    char *name;']
        txt += ['    int  index;']
        txt += ['};']
        txt += ['enum {']
        for item in evts:
            txt += ['    e%s = %s,' % (self.mkEvent(item[0]), item[1])]
        txt += ['};']
        txt += ['static const struct %s_t event_pointers [] = {' % self.mkEvent()]
        txt += ['    { NULL, %s },' % self.mkName('NUM_EVENTS')]
        for item in evts:
            txt += ['    { "%s", %d },'\
                    % (item[0], item[1])]
        txt += ['    { NULL, 0 }']
        txt += ['};']
        for item in evts:
            txt += ['const %s %s = &event_pointers[%d];'\
                    % (self.mkEvent(), self.mkEvent(item[0]), item[1])]
        # Actions
        txt += ['', '/* Actions */']
        txt += ['struct %s_t {' % self.mkAction()]
        txt += ['    char *name;']
        txt += ['    int  index;']
        txt += ['};']
        txt += ['enum {']
        for item in acts:
            txt += ['    e%s = %s,' % (self.mkAction(item[0]), item[1])]
        txt += ['};']
        txt += ['static const struct %s_t action_pointers [] = {' % self.mkAction()]
        txt += ['    { NULL, %s },' % self.mkName('NUM_ACTIONS')]
        for item in acts:
            txt += ['    { "%s", %d },'\
                    % (item[0], item[1])]
        txt += ['    { NULL, 0 }']
        txt += ['};']
        for item in acts:
            txt += ['const %s %s = &action_pointers[%d];'\
                    % (self.mkAction(), self.mkAction(item[0]), item[1])]
        #
        txt += ['']
        txt += ['typedef struct fsmTransTab_t fsmTransTab;']
        txt += ['typedef enum {']
        txt += ['    fsmActionClass = 1, /* Classifier Action Entry */']
        txt += ['    fsmActionTrans = 2  /* Transition Action Entry */']
        txt += ['} fsmActionType;']
        txt += ['struct fsmTransTab_t {']
        txt += ['    %s si; /* Input State */' % self.mkState()]
        txt += ['    %s ei; /* Input Event */' % self.mkEvent()]
        txt += ['    fsmActionType ac_type; /* Classifier or Transition */']
        txt += ['    union {']
        txt += ['        struct { /* Classifier Action Entry */']
        txt += ['            int ac_class; /* Action Classifier */']
        txt += ['            int ev_start; /* First output Event */']
        txt += ['            int ev_count; /* Number of candidates */']
        txt += ['        };']
        txt += ['        struct { /* Transition Action Entry */']
        txt += ['            %s so;        /* Output State */' % self.mkState()]
        txt += ['            int ac_start; /* First Action */']
        txt += ['            int ac_count; /* Number of Actions */']
        txt += ['        };']
        txt += ['    };']
        txt += ['};']
        # Generate the Transition Tables
        act_txt = ['/* TODO: the action_table has sequences of actions per transition */']
        act_txt += ['static const struct %s_t * const action_table[] = {' % self.mkAction()]
        evt_txt = ['/* TODO: the event_table has sequences of events per classifier */']
        evt_txt += ['static const struct %s_t * event_table[] = {' % self.mkEvent()]
        map_txt = ['/* TODO: the map_table has indexes into trans_table per state */']
        map_txt += ['static int map_table[] = {', '    0,']
        tab_txt = ['/* TODO: describe the transition_table */']
        tab_txt += ['static fsmTransTab trans_table[] = {']
        act_idx = 0
        evt_idx = 0
        tab_idx = 0
        for state in the_states:
            map_txt += ['    %d, /* %s */' % (tab_idx, state)]
            for event in the_events:
                for block in the_blocks:
                    if block.source == state and block.event == event:
                        act_cnt = len(block.actions)
                        for item in block.actions:
                            act_txt += ['    &action_pointers[e%s],' % self.mkAction(item)]
                        target = state
                        if isinstance(block, Transition) and len(block.targets) > 0:
                            target = block.targets[0]
                        line = ''
                        line += '    { /* %d */\n' % (tab_idx)
                        line += '        .si=&state_pointers[e%s],\n' % (self.mkState(state))
                        line += '        .ei=&event_pointers[e%s],\n' % (self.mkEvent(event))
                        if isinstance(block, Transition):
                            line += '        .ac_type=fsmActionTrans,\n'
                            line += '        .so=&state_pointers[e%s],\n' % self.mkState(target)
                            line += '        .ac_start=%d,\n' % act_idx
                            line += '        .ac_count=%d,\n' % act_cnt
                        else:
                            evt_cnt = len(block.targets)
                            for item in block.targets:
                                evt_txt += ['    &event_pointers[e%s],' % self.mkEvent(item[0])]
                            line += '        .ac_type=fsmActionClass,\n'
                            line += '        .ac_class=e%s,\n' % self.mkAction(block.actions[0])
                            line += '        .ev_start=%d,\n' % evt_idx
                            evt_idx += evt_cnt
                            line += '        .ev_count=%s,\n' % evt_cnt
                            for action in block.actions:
                                if action not in classifier_list:
                                    classifier_list[action] = block.targets[0]
                        line += '    },'
                        tab_txt += [line]
                        tab_idx += 1
                        act_idx += act_cnt
        act_txt += ['};', '']
        evt_txt += ['};', '']
        map_txt += ['    %d' % tab_idx]
        map_txt += ['};', '']
        tab_txt += ['};', '']
        txt += act_txt
        txt += evt_txt
        txt += map_txt
        txt += tab_txt
        txt += ['']
        txt += ['static char *state_names[] = {', '    0,']
        for state in the_states:
            txt += ['    "%s",' % self.mkState(state)]
        txt += ['    0', '};', '']
        txt += ['static char *event_names[] = {', '    0,']
        for event in the_events:
            txt += ['    "%s",' % self.mkEvent(event)]
        txt += ['    0', '};', '']
        txt += ['static char *action_names[] = {', '    0,']
        for action in the_actions:
            txt += ['    "%s",' % self.mkAction(action)]
        txt += ['    0', '};', '']
        txt += ['']
        txt += ['static %s action_funcs[%s+1];' % (self.mkFunc('Action'), self.mkName('NUM_ACTIONS'))]
        txt += ['', '/* State Machine Class */']
        txt += ['typedef struct fsmStateMachine_t fsmStateMachine;']
        txt += ['struct fsmStateMachine_t {']
        txt += ['    char *name;']
        txt += ['    int numStates;']
        txt += ['    int numEvents;']
        txt += ['    int numTrans;']
        txt += ['    int numActions;']
        txt += ['    int maxActions;']
        txt += ['    %s entryEvent;' % self.mkEvent()]
        txt += ['    %s exitEvent;' % self.mkEvent()]
        txt += ['    int *mapTab;']
        txt += ['    const %s * actTab;' % self.mkAction()]
        txt += ['    const %s * evtTab;' % self.mkEvent()]
        txt += ['    char **stateNames;']
        txt += ['    char **eventNames;']
        txt += ['    char **actionNames;']
        txt += ['    fsmTransTab *transTab;']
        txt += ['    %s *actionTab; /* Class Actions */' % self.mkFunc('Action')]
        txt += ['};']
        txt += ['', '/* State Machine Instance */']
        txt += ['struct %s_t {' % self.mkName()]
        txt += ['    char *name;']
        txt += ['    const fsmStateMachine *fsm;']
        txt += ['    %s *actionTab; /* Instance Actions */' % self.mkFunc('Action')]
        txt += ['    %s currentState;' % self.mkState()]
        txt += ['    void *priv; /* private */']
        txt += ['    void (*killPriv)(void*);']
        txt += ['};']
        txt += ['', '/* State Machine Initializer */']
        txt += ['static const fsmStateMachine fsm_%s = {' % self.name]
        txt += ['    .name="%s",' % self.name]
        txt += ['    .numStates=%s,' % self.mkName('NUM_STATES')]
        txt += ['    .numEvents=%s,' % self.mkName('NUM_EVENTS')]
        txt += ['    .numTrans=%s,' % self.mkName('NUM_TRANS')]
        txt += ['    .numActions=%s,' % self.mkName('NUM_ACTIONS')]
        txt += ['    .maxActions=%s,' % self.mkName('MAX_ACTIONS')]
        txt += ['    .entryEvent=&event_pointers[e%s],' % (self.mkEvent('Entry'))]
        txt += ['    .exitEvent=&event_pointers[e%s],' % (self.mkEvent('Exit'))]
        txt += ['    .mapTab=map_table,']
        txt += ['    .actTab=action_table,']
        txt += ['    .evtTab=event_table,']
        txt += ['    .stateNames=state_names,']
        txt += ['    .eventNames=event_names,']
        txt += ['    .actionNames=action_names,']
        txt += ['    .transTab=trans_table,']
        txt += ['    .actionTab=action_funcs']
        txt += ['};', '']
        txt += self.Generate_Code()
        txt += ['', '#ifdef UNIT_TEST']
        for action in the_actions:
            txt += ['static %s %s_test(' % (self.mkEvent(), self.mkAction(action))]
            txt += ['        %s smi,' % self.mkName()]
            txt += ['        %s state,' % self.mkState()]
            txt += ['        %s event)' % self.mkEvent()]
            txt += ['{']
            if action in classifier_list:
                next_event = classifier_list[action][0]
                txt += ['    printf("State: %%-20s, Event: %%-20s, Classifier: %-20s, NextEvent: %s\\n", state->name, event->name);' % (action, next_event)]
                txt += ['    return %s;' % self.mkEvent(next_event)]
            else:
                txt += ['    printf("State: %%-20s, Event: %%-20s, ActionFunc: %-20s\\n", state->name, event->name);' % action]
                txt += ['    return NULL;']
            txt += ['}', '']
        txt += ['static void register_%s_actions(void) {' % (self.name)]
        for action in the_actions:
            txt += ['    %s(%s, %s_test);'\
                    % (self.mkFunc('ClassSetAction'), self.mkAction(action), self.mkAction(action))]
        txt += ['};', '']
        txt += ['static void test_%s_actions(void) {' % (self.name)]
        txt += ['    %s smi;' % (self.mkName())]
        txt += ['    int state;']
        txt += ['    int event;']
        txt += ['    int idx;']
        txt += ['    register_%s_actions();' % (self.name), '']
        txt += ['    smi = %s("test", %s);' % (self.mkFunc('InstanceMake'), self.mkState(the_states[0]))]
        txt += ['    for (state = 1; state <= %s; ++state)' % self.mkName('NUM_STATES')]
        txt += ['        for (event = 1; event <= %s; ++event)' % self.mkName('NUM_EVENTS')]
        txt += ['            for (idx = 0; idx < %s; ++idx) {' % self.mkName('NUM_TRANS')]
        txt += ['                fsmTransTab *tab = &trans_table[idx];']
        txt += ['                if (tab->si->index == state && tab->ei->index == event) {']
        txt += ['                    smi->currentState = &state_pointers[state];']
        txt += ['                    %s(smi, &event_pointers[event]);' % self.mkFunc('InstanceRun')]
        txt += ['                    if (smi->currentState->index != state)']
        txt += ['                        printf("       %s ===> %s\\n", state_names[state], smi->currentState->name);']
        txt += ['                }']
        txt += ['            }']
        for test in self.tests:
            print "Test::", test
            txt += ['    do {']
            txt += ['        smi->currentState = %s;' % test.tests[0]]
            for t in test.tests:
                if t in the_states:
                    txt += ['        if (smi->currentState != %s) {' % t]
                    txt += ['            printf("State is %%s but expected %s\\n", fsm->stateNames[smi.currentState]);' % t]
                    txt += ['            break;']
                    txt += ['        }']
                else:
                    txt += ['        fsmRunStateMachine(&smi, %s);' % t]
            txt += ['        printf("Test Passed: %s\\n");' % repr(test)]
            txt += ['    } while (0);']
        txt += ['    %s(smi);' % (self.mkFunc('InstanceKill'))]
        txt += ['};', '']
        txt += ['static void fsmPrintStateMachine(void)']
        txt += ['{']
        txt += ['']
        txt += ['}']
        txt += ['']
        txt += ['int main(int argc, char *argv[]) {']
        txt += ['    fsmPrintStateMachine();']
        txt += ['    test_%s_actions();' % (self.name)]
        txt += ['};', '']
        txt += ['#endif /* UNIT_TEST */']
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
