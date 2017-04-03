# Author: Douglas Clowes (douglas.clowes@ansto.gov.au) Aug 2015
# vim: ft=python ts=8 sts=4 sw=4 expandtab autoindent smartindent nocindent
#
from statemachine import Classifier
from statemachine import Transition
from statemachine import StateMachine_Text

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

