# Author: Douglas Clowes (douglas.clowes@ansto.gov.au) Aug 2015
# vim: ft=python ts=8 sts=4 sw=4 expandtab autoindent smartindent nocindent
#
from statemachine import Classifier
from statemachine import Transition
from statemachine import StateMachine_Text

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
