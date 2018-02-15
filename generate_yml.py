# Author: Douglas Clowes (douglas.clowes@ansto.gov.au) Aug 2015
# vim: ft=python ts=8 sts=4 sw=4 expandtab autoindent smartindent nocindent
#

import yaml
import json
from statemachine import Action, Classifier, Transition
from statemachine import Event, State
from statemachine import StateMachine, StateMachine_Text

doActions = True
doClassifiers = True
doSelf = True

class StateMachine_YML(StateMachine_Text):
    def __init__(self, other):
        StateMachine_Text.__init__(self, other)
        self.Inheritance()
        self.code_default = ['    return NULL;']
        self.config = {}

    def Load(self, template):
        import os
        import sys
        import jinja2
        template_base = os.path.realpath(
            os.path.abspath(
                os.path.dirname(sys.argv[0])
            )
        )
        templateLoader = jinja2.FileSystemLoader(searchpath=template_base)
        templateEnv = jinja2.Environment(loader=templateLoader)
        my_vars = self.Dictify()

        self.config = {}
        template = templateEnv.get_template(
            "template_%s.yml" % template.lower()
        )
        configText = template.render(my_vars)
        self.config = yaml.load(configText)
        print(self.config)
        my_vars['config'] = self.config
        print(yaml.dump(my_vars, indent=4))
        for file in self.config['template']['files']:
            dest_file = file['output']
            my_vars['code_blocks'] = {}
            if 'preload' in file:
                self.Absorb_Skel(file['preload'])
                my_vars['code_blocks'] = self.code_blocks
                print(yaml.dump(my_vars['code_blocks'], indent=4))
            template = templateEnv.get_template(file['input'])
            outputText = template.render(my_vars)
            with open(dest_file, 'w') as fdo:
                fdo.write(outputText)


    def Dictify(self):
        '''
        Produce a python dictionary version of the statemachine description
        '''
        result = {
            'statemachine': self.uname,
            'dest_file': self.dest_file
        }

        # enumerate the states
        the_states = {}
        initial_states = []
        for state in self.states:
            the_states[state.name] = state
        result['states'] = {}
        for state in sorted(the_states):
            this_state = {}
            if the_states[state].comments:
                this_state['comment'] = the_states[state].comments
            if the_states[state].flags:
                this_state['flags'] = the_states[state].flags
                for flag in this_state['flags']:
                    if flag.upper() == 'INITIAL':
                        if not state in initial_states:
                            initial_states.append(state)
            if the_states[state].base_list:
                this_state['inherits'] = the_states[state].base_list
            result['states'][state] = this_state
        if initial_states:
            result['initial_states'] = initial_states

        # enumerate the events
        the_events = {}
        for event in self.events:
            the_events[event.name] = event
        result['events'] = {}
        for event in sorted(the_events):
            this_event = {}
            if the_events[event].comments:
                this_event['comment'] = the_events[event].comments
            result['events'][event] = this_event

        # enumerate the actions
        the_actions = {}
        print("Actions:%s"%yaml.dump(self.actions))
        for action in self.actions:
            the_actions[action.name] = action
        result['actions'] = {}
        for action in sorted(the_actions):
            this_action = {}
            if the_actions[action].comments:
                this_action['comment'] = the_actions[action].comments
            if the_actions[action].code_text:
                this_action['code_text'] = the_actions[action].code_text
            result['actions'][action] = this_action

        # enumerate the transactions
        transactions = {}
        for state in sorted(the_states):
            this_state = {}
            for event in sorted(the_events):
                for block in [b for b in self.classifiers
                              if b.source == state and b.event == event]:
                    this_one = {'actions': [], 'events': [], 'states': []}
                    if block.actions:
                        this_one['actions'] = block.actions
                    if block.targets:
                        this_one['events'] = block.targets
                    this_state[event] = this_one
            for event in sorted(the_events):
                for block in [b for b in self.transitions
                              if b.source == state and b.event == event]:
                    this_one = {'actions': [], 'events': [], 'states': []}
                    if block.actions:
                        this_one['actions'] = block.actions
                    if block.targets:
                        this_one['states'] = block.targets
                    this_state[event] = this_one
            transactions[state] = this_state
        result['transactions'] = transactions

        # enumerate the tests
        tests = []
        for test in self.tests:
            #print "Test:", test.tests
            tests.append(test.tests)
        result['tests'] = tests

        if self.outputs:
            result['outputs'] = self.outputs

        #print(result)
        #print(yaml.dump(result))
        #print(json.dumps(result))
        return result

    def Generate(self):
        txt = ['---']
        txt += ['statemachine: "%s"' % self.uname]

        the_states = {}
        for state in self.states:
            the_states[state.name] = state
        txt += ['states:']
        for state in sorted(the_states):
            txt += ['  - name: "%s"' % state]
            txt += ['    comment: "%s"' % ('\\n'.join(the_states[state].comments))]
            #if 'INITIAL' in [f.upper() for f in the_states[state].flags]:
            #    txt += ["[*] -> %s" % state]
        txt += ['']

        the_events = {}
        for event in self.events:
            the_events[event.name] = event
        txt += ['events:']
        for event in sorted(the_events):
            txt += ['  - name: "%s"' % event]
            txt += ['    comment: "%s"' % ('\\n'.join(the_events[event].comments))]
        txt += ['']

        the_actions = {}
        for action in self.actions:
            the_actions[action.name] = action
        txt += ['actions:']
        for action in sorted(the_actions):
            txt += ['  - name: "%s"' % action]
            txt += ['    comment: "%s"' % ('\\n'.join(the_actions[action].comments))]
        txt += ['']

        txt += ['transitions:']
        for state in sorted(the_states):
            the_blocks = [b for b in self.classifiers if b.source == state]
            for block in sorted(the_blocks, key=lambda b: b.event):
                txt += ['  - transition:']
                txt += ['    state: "%s"' % state]
                txt += ['    event: "%s"' % block.event]
                txt += ['    type: "classifier"']
                if len(block.actions) > 0:
                    txt += ['    actions:']
                    for action in block.actions:
                        txt += ['    - "%s"' % action]
                if len(block.targets) > 0:
                    txt += ['    targets:']
                    for target in block.targets:
                        txt += ['    - "%s"' % target]
            the_blocks = [b for b in self.transitions if b.source == state]
            for block in sorted(the_blocks, key=lambda b: b.event):
                if len(block.targets) == 0:
                    tgts = state
                    if doSelf == False:
                        continue
                else:
                    tgts = ','.join(block.targets)
                txt += ['  - transition:']
                txt += ['    state: "%s"' % state]
                txt += ['    event: "%s"' % block.event]
                txt += ['    type: "transition"']
                if len(block.actions) > 0:
                    txt += ['    actions:']
                    for action in block.actions:
                        txt += ['    - "%s"' % action]
                if len(block.targets) > 0:
                    txt += ['    targets:']
                    for target in block.targets:
                        txt += ['    - "%s"' % target]
        txt += ['...']
        return txt
