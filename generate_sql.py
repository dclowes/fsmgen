# Author: Douglas Clowes (douglas.clowes@ansto.gov.au) Aug 2015
# vim: ft=python ts=8 sts=4 sw=4 expandtab autoindent smartindent nocindent
#
import os
from statemachine import Action, Classifier, Transition
from statemachine import Event, State
from statemachine import StateMachine, StateMachine_Text
import sqlite3

class StateMachine_SQL(StateMachine_Text):
    def __init__(self, other):
        if isinstance(other, type("")) and other.endswith(".sqlite"):
            if os.path.exists(other):
                self.loadSQL(other)
        elif isinstance(other, StateMachine):
            StateMachine_Text.__init__(self, other)
        #self.Inheritance()

    def loadSQL(self, database):
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

        curs.execute("SELECT name, bases, flags, comments FROM states")
        for name, bases, flags, comments in curs.fetchall():
            item = State(name)
            if len(bases) > 0:
                item.base_list = bases.split("\n")
            if len(flags) > 0:
                item.flags = flags.split(",")
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

    def Generate(self):
        import sqlite3
        dest_file = "%s.sqlite" % self.dest_file
        if os.path.exists(dest_file):
            os.remove(dest_file)
        conn = sqlite3.connect(dest_file)
        curs = conn.cursor()
        curs.execute("CREATE TABLE statemachine (name TEXT, comments TEXT)")
        curs.execute("CREATE TABLE states (name TEXT, bases TEXT, flags TEXT, comments TEXT)")
        curs.execute("CREATE TABLE events (name TEXT, comments TEXT)")
        curs.execute("CREATE TABLE actions (name TEXT, comments TEXT)")
        curs.execute("CREATE TABLE code (name TEXT, type TEXT, lines TEXT)")
        curs.execute("CREATE TABLE transitions (state TEXT, event TEXT, actions TEXT, targets TEXT)")
        curs.execute("CREATE TABLE classifications (state TEXT, event TEXT, actions TEXT, targets TEXT)")
        curs.execute("CREATE TABLE tests (test TEXT)")

        curs.execute("INSERT INTO statemachine VALUES (:1, :2)", (self.name, "\n".join(self.comments)))
        for s in sorted(self.states, key=lambda state: state.name):
            curs.execute("INSERT INTO states VALUES (:1, :2, :3, :4)",
                         (s.name,
                          "\n".join(s.base_list),
                          ",".join(sorted(s.flags)),
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

