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
        self.script_context = False

    def mkEvent(self, name=None):
        return "'%s'" % name

    def mkActionFunc(self, action):
        txt = []
        txt += ['proc %s {context state event} {' % action]
        return txt

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
        if self.script_context:
            txt += ['        debug_log ${context} 1 "StateSwitch ${context} ${state} ${next_event} => ${state_event}"']
        txt += ['        set next_state [lindex ${state_event} 0]']
        txt += ['        set rule_count [expr {${rule_count} + [lindex ${state_event} 2]}]']
        txt += ['        if { ${next_state} != ${state} } {']
        txt += ['            set state_event [StateSwitch_%s ${context} ${state} "Exit"]' % self.name]
        if self.script_context:
            txt += ['            debug_log ${context} 1 "StateSwitch ${context} ${state} Exit => ${state_event}"']
        txt += ['            set state_event [StateSwitch_%s ${context} ${next_state} "Entry"]' % self.name]
        if self.script_context:
            txt += ['            debug_log ${context} 1 "StateSwitch ${context} ${next_state} Entry => ${state_event}"']
        txt += ['        }']
        txt += ['        set next_event [lindex ${state_event} 1]']
        txt += ['        set state ${next_state}']
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

    def gen_bdy_block(self, indent, block):
        txt = []
        txt += ['%s# BEGIN CUSTOM: %s [[[' % (indent, block)]
        if block in self.code_blocks:
            txt += self.code_blocks[block]
            self.done_blocks.append(block)
        elif block.endswith('action code'):
            txt += ['%sreturn {}' % (indent)]
        txt += ['%s# END CUSTOM: %s ]]]' % (indent, block)]
        return txt

    def Generate_Skel(self):
        txt = []
        self.done_blocks = []
        code_blocks = self.code_blocks
        lines_emitted = sum([len(code_blocks[block]) for block in code_blocks])
        for action in self.Actions():
            name = action.name
            if self.isClassifier(name):
                txt += ['# Classifier returns:']
                for target in self.getTargets(name):
                    txt += ['#    %s' % self.mkEvent(target)]
            else:
                txt += ['# Transition: returns NULL']
            if len(action.comments) > 0:
                txt += ['# Comments:']
                for line in action.comments:
                    txt += ['#    %s' % line]
            txt += self.mkActionFunc(name)
            if self.script_context:
                txt += ['  set catch_status [ catch {']
                txt += ['    debug_log ${context} 1 "Action: %s dev=${context}, state=${state}, event=${event}, sct=[sct]"' % (name)]
                txt += self.gen_bdy_block('    ', '%s action code' % name)
                txt += ['  } catch_message ]']
                txt += ['  set tc_root ${context}']
                txt += ['  handle_exception ${catch_status} ${catch_message}']
            else:
                txt += self.gen_bdy_block('    ', '%s action code' % name)
            txt += ['}']
            txt += ['']
        lines_parked = 0
        parked = {}
        for block in self.code_blocks:
            if block not in self.done_blocks:
                parked[block] = self.code_blocks[block]
        if len(parked) > 0:
            print "Blocks Parked:", sorted(parked.keys())
            lines_parked = sum([len(self.code_blocks[block]) for block in parked])
            print "Lines parked:", lines_parked
            txt += ['if {0} {', '# BEGIN PARKING LOT [[[']
            for block in sorted(parked.keys()):
                txt += self.gen_bdy_block('', block)
            txt += ['# END PARKING LOT ]]]', '}']
        print "Custom Lines:", lines_emitted
        txt += ['']
        txt += ['# %s: ft=tcl ts=8 sts=4 sw=4 et nocindent fmr=[[[,]]]' % 'vim']
        return txt

