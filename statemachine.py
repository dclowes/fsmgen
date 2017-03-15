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
        if isinstance(other, type("")) and other.endswith(".sqlite"):
            self.loadSQL(other)
            return
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

    def loadSQL(self, database):
        import sqlite3
        conn = sqlite3.connect(database)
        curs = conn.cursor()
        curs.execute("SELECT name, comments FROM statemachine")
        name, comments = curs.fetchone()
        StateMachine.__init__(self, name)
        self.name = name
        if len(comments) > 0:
            self.comments = comments.split("\n")
        self.dest_file = database
        curs.execute("SELECT name, comments FROM actions")
        for name, comments in curs.fetchall():
            item = Action(name)
            if len(comments) > 0:
                item.comments = comments.split("\n")
            self.addAction(item)

        curs.execute("SELECT name, comments FROM events")
        for name, comments in curs.fetchall():
            item = Event(name)
            if len(comments) > 0:
                item.comments = comments.split("\n")
            self.addEvent(item)

        curs.execute("SELECT name, bases, comments FROM states")
        for name, bases, comments in curs.fetchall():
            item = State(name)
            if len(bases) > 0:
                item.base_list = bases.split("\n")
            if len(comments) > 0:
                item.comments = comments.split("\n")
            self.addState(item)

        curs.execute("SELECT state, event, actions, targets FROM transitions")
        for state, event, actions, targets in curs.fetchall():
            item = Transition(state, event)
            if len(actions) > 0:
                item.actions = actions.split("\n")
            if len(targets) > 0:
                item.targets = targets.split("\n")
            self.addTransition(item)

        curs.execute("SELECT state, event, actions, targets FROM classifications")
        for state, event, actions, targets in curs.fetchall():
            item = Classifier(state, event)
            if len(actions) > 0:
                item.actions = actions.split("\n")
            if len(targets) > 0:
                item.targets = targets.split("\n")
            self.addClassifier(item)
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
                    style = 'dir=both,arrowtail=inv,style=dotted,color=%s' % colors[idx]
                    idx += 1
                    if idx >= len(colors):
                        idx = 0
                    for t in block.targets:
                        if t[0] in [b.event for b in the_blocks]:
                            txt += ['    %s:%s -> %s:%s[%s];' % (state, block.event, state, t[0], style)]
        txt += ['}']
        return txt

    def mkSource(self, block):
        if len(block.actions) == 0:
            return block.event
        return block.event + '_source'

    def mkTarget(self, block):
        if len(block.actions) == 0:
            return block.event
        return block.event + '_target'

    def DotStateMachine3(self):
        target_map = {}
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
            label = ['<TABLE>']
            label += ['<TR><TD PORT="%s"><B>%s</B></TD></TR>' % (state, state)]
            the_blocks = [b for b in sorted(self.classifiers) if b.source == state]
            the_blocks += [b for b in sorted(self.transitions) if b.source == state]
            idx = 0
            for block in the_blocks:
                target_text = self.mkTarget(block)
                source_text = self.mkSource(block)
                target_map["%s:%s" % (state, block.event)] = (target_text, source_text)
                label += ['<TR><TD><TABLE>']
                label += ['  <TR><TD PORT="%s"><B>%s</B></TD></TR>' % (self.mkTarget(block), block.event)]
                for (n, a) in enumerate(block.actions):
                    if n < len(block.actions) - 1:
                        label += ['    <TR><TD>%s</TD></TR>' % a]
                    else:
                        label += ['    <TR><TD PORT="%s">%s</TD></TR>' % (self.mkSource(block), a)]
                label += ['</TABLE></TD></TR>']
            label += ['</TABLE>']
            txt += ['  %s[label=<%s>];' % (state, '\n    '.join(label))]
            for block in the_blocks:
                if isinstance(block, Transition):
                    for t in block.targets:
                        txt += ['    %s:%s -> %s:%s;' % (state, self.mkSource(block), t, t)]
                else:
                    style = 'dir=both,arrowtail=inv,style=dotted,color=%s' % colors[idx]
                    idx += 1
                    if idx >= len(colors):
                        idx = 0
                    for t in block.targets:
                        for b in [b for b in the_blocks if t[0] == b.event]:
                            txt += ['    %s:%s -> %s:%s[%s];' % (state, self.mkSource(block), state, self.mkTarget(b), style)]
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
        # print "Classifiers:", classifier_list
        for action in classifier_list:
            txt += ['    def %s(context, state, event):' % action[0]]
            line = '"State %%-%ds event %%-%ds: %s" %% (state, event)' % (slen, elen, action[0])
            txt += ['        print %s' % line]
            txt += ['        return "%s"' % action[1][0]]
        # print "Actions:", action_list
        for action in action_list:
            txt += ['    def %s(context, state, event):' % action]
            line = '"State %%-%ds event %%-%ds: %s" %% (state, event)' % (slen, elen, action)
            txt += ['        print %s' % line]
        # print "Tests:", test_list
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
            # print "Test::", test
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
            the_blocks = [b for b in self.actions if b.name == action and 'action' in b.code_text]
            if len(the_blocks) == 0:
                continue
            txt2 += ['    def %s (context, state, event):' % action]
            # print "##The Blocks:", the_blocks
            for code_block in the_blocks:
                # print "##CodeBlock:", code_block
                # print "##CodeText:", code_block.code_text
                for code_text in [c[1] for c in code_block.code_text if c[0] == 'PYTHON']:
                    # print "##CodeText:", code_text
                    # Calculate the minimum white space for indent adjustment
                    min_wh = min([len(s) - len(s.lstrip(' ')) for s in code_text])
                    for code in code_text:
                        # print "##Code:", code[min_wh:]
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
        txt = []
        txt += ['proc %s {context state event} {' % func_name]
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
        # print "Classifiers:", classifier_list
        for action in classifier_list:
            txt += ['    proc %s {context state event} {' % action[0]]
            line = 'State [format "%%-%ds" ${state}] event [format "%%-%ds" ${event}]: %s' %\
                    (slen, elen, action[0])
            txt += ['        puts "%s"' % line]
            txt += ['        return "%s"' % action[1][0]]
            txt += ['    }']
        # print "Actions:", action_list
        for action in action_list:
            txt += ['    proc %s {context state event} {' % action]
            line = 'State [format "%%-%ds" ${state}] event [format "%%-%ds" ${event}]: %s' %\
                    (slen, elen, action)
            txt += ['        puts "%s"' % line]
            txt += ['    }']
        # print "Tests:", test_list
        for test in test_list:
            s1 = test[0]
            ev = test[1]
            s2 = test[2]
            txt += ['    set state_event [%s "Ctx" "%s" "%s"]' % (func_name, s1, ev)]
            txt += ['    if {[lindex ${state_event} 2] <= 0} {error "count fail!"}']
            txt += ['    if {[lindex ${state_event} 0] != "%s"} {error "state fail!"}' % (s2)]
        txt += ['    puts "TestStateSwitch_%s() passed"' % self.name]
        for test in self.tests:
            # print "Test::", test
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
            the_blocks = [b for b in self.actions if b.name == action and 'action' in b.code_text]
            if len(the_blocks) == 0:
                continue
            txt2 += ['    proc %s {context state event} {' % action]
            # print "##The Blocks:", the_blocks
            for code_block in the_blocks:
                # print "##CodeBlock:", code_block
                # print "##CodeText:", code_block.code_text
                for code_text in [c[1] for c in code_block.code_text if c[0] == 'TCL']:
                    # print "##CodeText:", code_text
                    # Calculate the minimum white space for indent adjustment
                    min_wh = min([len(s) - len(s.lstrip(' ')) for s in code_text])
                    for code in code_text:
                        # print "##Code:", code[min_wh:]
                        txt2 += ['        ' + code[min_wh:]]
            txt2 += ['    }']
        if len(txt2) > 1:
            txt += txt2
        txt += ['}']
        return txt

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

class StateMachine_SQL(StateMachine_Text):
    def __init__(self, other):
        StateMachine_Text.__init__(self, other)
        #self.Inheritance()

    def Generate(self):
        import os
        import sqlite3
        dest_file = "%s.sqlite" % self.dest_file
        if os.path.exists(dest_file):
            os.remove(dest_file)
        conn = sqlite3.connect(dest_file)
        curs = conn.cursor()
        curs.execute("CREATE TABLE statemachine (name TEXT, comments TEXT)")
        curs.execute("CREATE TABLE states (name TEXT, bases TEXT, comments TEXT)")
        curs.execute("CREATE TABLE events (name TEXT, comments TEXT)")
        curs.execute("CREATE TABLE actions (name TEXT, comments TEXT)")
        curs.execute("CREATE TABLE code (name TEXT, type TEXT, lines TEXT)")
        curs.execute("CREATE TABLE transitions (state TEXT, event TEXT, actions TEXT, targets TEXT)")
        curs.execute("CREATE TABLE classifications (state TEXT, event TEXT, actions TEXT, targets TEXT)")
        curs.execute("CREATE TABLE tests (test TEXT)")

        curs.execute("INSERT INTO statemachine VALUES (:1, :2)", (self.name, "\n".join(self.comments)))
        for s in sorted(self.states, key=lambda state: state.name):
            curs.execute("INSERT INTO states VALUES (:1, :2, :3)",
                         (s.name,
                          "\n".join(s.base_list),
                          "\n".join(s.comments)))
        for e in sorted(self.events, key=lambda event: event.name):
            curs.execute("INSERT INTO events VALUES (:1, :2)",
                         (e.name,
                          "\n".join(e.comments)))
        for a in sorted(self.actions, key=lambda action: action.name):
            curs.execute("INSERT INTO actions VALUES (:1, :2)",
                         (a.name,
                          "\n".join(a.comments)))
        for block in sorted(self.transitions, key=lambda block: (block.source, block.event)):
            curs.execute("INSERT INTO transitions VALUES (:1, :2, :3, :4)",
                         (block.source,
                          block.event,
                          "\n".join(block.actions),
                          "\n".join(block.targets)))
        for block in sorted(self.classifiers, key=lambda block: (block.source, block.event)):
            curs.execute("INSERT INTO classifications VALUES (:1, :2, :3, :4)",
                         (block.source,
                          block.event,
                          "\n".join(block.actions),
                          "\n".join(block.targets)))
        for action in self.actions:
            # print "Actions:", action
            for block in action.code_text:
                # print "  block:", block
                curs.execute("INSERT INTO code VALUES (:1, :2, :3)",
                             (action.name,
                              block,
                              '\n'.join(action.code_text[block])))

        for test in self.tests:
            # print "Test:", type(repr(test)), repr(test)
            curs.execute("INSERT INTO tests VALUES (:1)", (repr(test),))

        conn.commit()

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

