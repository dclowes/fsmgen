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

from statemachine import Classifier, Transition
from generate_gcc import StateMachine_GCC 
#import statemachine

class StateMachine_GCC3(StateMachine_GCC):
    def __init__(self, other):
        StateMachine_GCC.__init__(self, other)

    def gen_hdr_actions(self):
        hdr = []
        hdr += ['/* Actions */']
        hdr += ['typedef const struct %s_t *%s;' %
                (self.mkAction(),
                 self.mkAction())]
        for action in self.Actions():
            hdr += ['extern const %s %s;' % (self.mkAction(), self.mkAction(action.name))]
        return hdr

    def gen_hdr_events(self):
        hdr = []
        hdr += ['/* Events */']
        hdr += ['typedef const struct %s_t *%s;' %
                (self.mkEvent(),
                 self.mkEvent())]
        for event in self.Events():
            hdr += ['extern const %s %s;' % (self.mkEvent(), self.mkEvent(event.name))]
        return hdr

    def gen_hdr_states(self):
        hdr = []
        hdr += ['/* States */']
        hdr += ['typedef const struct %s_t *%s;' %
                (self.mkState(),
                 self.mkState())]
        for state in self.States():
            hdr += ['extern const %s %s;' % (self.mkState(), self.mkState(state.name))]
        return hdr

    def gen_hdr_funcs(self):
        hdr = []
        # Instance
        hdr += ['/* Statemachine Instance */']
        hdr += ['typedef struct %s_t *%s;'\
                % (self.mkName(), self.mkName())]
        # Functions
        hdr += ['', '/* Statemachine Functions */']
        hdr += ['', '/* User Supplied Action/Classifier Functions */']
        hdr += ['typedef %s (*%s)('\
                % (self.mkEvent(), self.mkFunc('Action'))]
        hdr += ['    %s smi,' % self.mkName()]
        hdr += ['    %s state,' % self.mkState()]
        hdr += ['    %s event,' % self.mkEvent()]
        hdr += ['    void *pContext,']
        hdr += ['    void *pPrivate);']
        # Constructor
        hdr += ['', '/* Statemachine Instance Constructor */']
        hdr += ['%s %s(const char *name, %s initial);'\
                % (self.mkName(), self.mkFunc('InstanceMake'), self.mkState())]
        hdr += ['', '/* Statemachine Instance Destructor */']
        hdr += ['void %s(%s smi);' % (self.mkName('InstanceKill'), self.mkFunc())]
        hdr += ['', '/* Statemachine Instance Driver */']
        hdr += ['void %s(%s smi, %s ev, void *pContext);'\
                % (self.mkFunc('InstanceRun'), self.mkName(), self.mkEvent())]
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
        hdr += ['', '/* Statemachine Class Action Initial Setter */']
        hdr += ['void %s(void);' % self.mkFunc('ClassInit')]
        hdr += ['', '/* Report Function accessors */']
        hdr += ['void %s(%s smi, void (*reportFunc)(%s smi, const char *fmt, ...));'\
                % (self.mkFunc('SetReportFunc'), self.mkName(), self.mkName())]
        hdr += ['void (*%s(%s smi))(%s smi, const char *fmt, ...);'\
                % (self.mkFunc('GetReportFunc'), self.mkName(), self.mkName())]
        hdr += ['', '/* Private data accessors */']
        hdr += ['void %s(%s smi, void *data, void (*pKiller)(void *));' % (self.mkFunc('SetPrivate'), self.mkName())]
        hdr += ['void *%s(%s smi);' % (self.mkFunc('GetPrivate'), self.mkName())]
        hdr += ['const char *%s(%s smi);' % (self.mkFunc('GetName'), self.mkName())]
        return hdr

    def gen_hdr(self):
        hdr = []
        hdr += ['#ifndef %s_FSM_H' % self.uname]
        hdr += ['#define %s_FSM_H' % self.uname]
        hdr += ['']
        hdr += self.gen_hdr_states()
        hdr += ['']
        hdr += self.gen_hdr_events()
        hdr += ['']
        hdr += self.gen_hdr_actions()
        hdr += ['']
        hdr += self.gen_hdr_funcs()
        hdr += ['']
        hdr += ['#endif /* %s_FSM_H */' % self.uname]
        return hdr

    def gen_bdy_prefix(self):
        txt = []
        txt += ['#include <stdlib.h>']
        txt += ['#include <stdio.h>']
        txt += ['#include <string.h>']
        txt += ['']
        txt += ['#define %s_NUM_STATES %d' % (self.uname, len(self.states))]
        txt += ['#define %s_NUM_EVENTS %d' % (self.uname, len(self.events))]
        txt += ['#define %s_NUM_ACTIONS %d' % (self.uname, len(self.actions))]
        txt += ['']
        return txt

    def gen_bdy_actions(self):
        txt = []
        txt += ['/* Actions */']
        txt += ['struct %s_t {' % self.mkAction()]
        txt += ['    int index;']
        txt += ['    char *name;']
        txt += ['};']

        txt += ['enum {']
        for index, action in enumerate(self.Actions()):
            txt += ['    e%s = %d,' % (self.mkAction(action.name), index + 1)]
        txt += ['};']

        for action in self.Actions():
            txt += ['static const struct %s_t s%s = {e%s, "%s"};' %
                    (self.mkAction(),
                     self.mkAction(action.name),
                     self.mkAction(action.name),
                     action.name)]
        for action in self.Actions():
            txt += ['const %s %s = &s%s;' %
                    (self.mkAction(),
                     self.mkAction(action.name),
                     self.mkAction(action.name))]
        txt += ['static const struct %s_t *%s_table[] = {' % (self.mkAction(), self.mkAction())]
        txt += ['    NULL,']
        for action in self.Actions():
            txt += ['    &s%s,' % (self.mkAction(action.name))]
        txt += ['};']
        return txt

    def gen_bdy_events(self):
        txt = []
        txt += ['/* Events */']
        txt += ['struct %s_t {' % self.mkEvent()]
        txt += ['    int index;']
        txt += ['    char *name;']
        txt += ['};']

        txt += ['enum {']
        for index, event in enumerate(self.Events()):
            txt += ['    e%s = %d,' % (self.mkEvent(event.name), index + 1)]
        txt += ['};']

        for event in self.Events():
            txt += ['static const struct %s_t s%s = {e%s, "%s"};' %
                    (self.mkEvent(),
                     self.mkEvent(event.name),
                     self.mkEvent(event.name),
                     event.name)]
        for event in self.Events():
            txt += ['const %s %s = &s%s;' %
                    (self.mkEvent(),
                     self.mkEvent(event.name),
                     self.mkEvent(event.name))]
        txt += ['static const struct %s_t * const %s_table[] = {' % (self.mkEvent(), self.mkEvent())]
        txt += ['    NULL,']
        for event in self.Events():
            txt += ['    &s%s,' % (self.mkEvent(event.name))]
        txt += ['};']
        return txt

    def gen_bdy_states(self):
        txt = []

        txt += ['/* States */']
        txt += ['enum {']
        for index, state in enumerate(self.States()):
            txt += ['    e%s = %d,' % (self.mkState(state.name), index + 1)]
        txt += ['};']

        txt += self.gen_def_trans()
        txt += self.gen_bdy_trans()

        txt += ['/* State Data */']
        txt += ['struct %s_t {' % self.mkState()]
        txt += ['    int index;']
        txt += ['    const char *name;']
        txt += ['    const fsmTransTab *transTab[];']
        txt += ['};']
        for state in self.States():
            txt += ['static struct %s_t const s%s = {' % (self.mkState(), self.mkState(state))]
            txt += ['    .index=e%s,' % (self.mkState(state.name))]
            txt += ['    .name="%s",' % (state.name)]
            txt += ['    .transTab={']
            txt += ['                   NULL,']
            for event in self.Events():
                if self.getTrans(state, event):
                    txt += ['        &%s,' % (self.mkTrans(state, event))]
                else:
                    txt += ['        NULL, /* %s */' % (self.mkTrans(state, event))]
            txt += ['   }']
            txt += ['};']
        txt += ['']
        for state in self.States():
            txt += ['const %s %s = &s%s;' %
                    (self.mkState(),
                     self.mkState(state.name),
                     self.mkState(state.name))]
        txt += ['static struct %s_t const * const %s_table[] = {' % (self.mkState(), self.mkState())]
        txt += ['    NULL,']
        for state in self.States():
            txt += ['    &s%s,' % (self.mkState(state))]
        txt += ['    NULL']
        txt += ['};']
        return txt

    def gen_def_trans(self):
        txt = []
        txt += ['/* Transition Table Structures */']
        txt += ['typedef enum {']
        txt += ['    fsmActionClass = 1, /* Classifier Action Entry */']
        txt += ['    fsmActionTrans = 2  /* Transition Action Entry */']
        txt += ['} fsmActionType;']
        txt += ['typedef struct fsmTransTab_t {']
        txt += ['    int inState;  /* Input State */']
        txt += ['    int inEvent;  /* Input Event */']
        txt += ['    fsmActionType ac_type; /* Classifier or Transition */']
        txt += ['    int ac_code;  /* Classifier Func or Output State */']
        txt += ['    int ac_list[];    /* Output Events or Action Funcs */']
        txt += ['} fsmTransTab;']
        return txt

    def gen_bdy_trans(self):
        txt = []
        txt = ['/* Transition Table Entries */']
        for state in self.States():
            for event in self.Events():
                trans = self.getTrans(state, event)
                if trans:
                    txt += ['const static fsmTransTab %s = {' % self.mkTrans(state.name, event.name)]
                    txt += ['    .inState=e%s,' % self.mkState(state.name)]
                    txt += ['    .inEvent=e%s,' % self.mkEvent(event.name)]
                    if isinstance(trans, Classifier):
                        # TODO Classifier body
                        txt += ['    .ac_type=fsmActionClass,']
                        txt += ['    .ac_code=e%s,' % self.mkAction(trans.actions[0])]
                        txt += ['    .ac_list= {']
                        for tab in trans.targets:
                            txt += ['        e%s,' % self.mkEvent(tab)]
                        txt += ['        0}']
                    elif isinstance(trans, Transition):
                        # TODO body
                        txt += ['    .ac_type=fsmActionTrans,']
                        if len(trans.targets) > 0:
                            txt += ['    .ac_code=e%s,' % self.mkState(trans.targets[0])]
                        else:
                            txt += ['    .ac_code=0,']
                        txt += ['    .ac_list= {']
                        for tab in trans.actions:
                            txt += ['        e%s,' % self.mkAction(tab)]
                        txt += ['        0}']
                    txt += ['};']
        txt += ['']
        for state in self.States():
            for event in self.Events():
                trans = self.getTrans(state, event)
                if trans:
                    if isinstance(trans, Classifier):
                        pass # TODO line
                    elif isinstance(trans, Transition):
                        pass # TODO line
                    else:
                        txt += ['    NULL,']
        return txt

    def gen_bdy(self):
        txt = []
        txt += self.gen_bdy_prefix()
        txt += self.gen_bdy_actions()
        txt += self.gen_bdy_events()
        txt += self.gen_bdy_states()
        txt += self.gen_bdy_fsm()
        txt += self.gen_bdy_Code()
        txt += self.gen_bdy_unit_test()
        return txt

    def gen_bdy_block(self, indent, block):
        txt = ['%s/* BEGIN CUSTOM: %s {{{ */' % (indent, block)]
        if block in self.code_blocks:
            txt += self.code_blocks[block]
            self.done_blocks.append(block)
        elif block.endswith('action code'):
            txt += ['%sreturn NULL;' % (indent)]
        txt += ['%s/* END CUSTOM: %s }}} */' % (indent, block)]
        return txt

    def gen_bdy_skel(self):
        txt = []
        self.done_blocks = []
        code_blocks = self.code_blocks
        lines_emitted = sum([len(code_blocks[block]) for block in code_blocks])
        txt += ['#include <stdlib.h>']
        txt += self.gen_bdy_block('', 'include files')
        txt += ['']
        txt += ['/* @brief private data type used in action routines */']
        txt += ['typedef %s_PRIVATE_DATA *pPRIVATE_DATA;' % self.mkName()]
        txt += ['']
        txt += ['/* Place forward declarations, used in the action code, here */']
        txt += self.gen_bdy_block('', 'forward declarations')
        txt += ['']
        for action in self.Actions():
            name = action.name
            if self.isClassifier(name):
                txt += ['/* Classifier returns: */']
                for target in self.getTargets(name):
                    txt += ['/*    %s */' % self.mkEvent(target)]
            else:
                txt += ['/* Transition: returns NULL */']
            if len(action.comments) > 0:
                txt += ['/* Comments: */']
                for line in action.comments:
                    txt += ['/*    %s */' % line]
            txt += self.mkActionFunc(name)
            txt += ['{']
            txt += ['    pPRIVATE_DATA self = (pPRIVATE_DATA) pPrivate;']
            txt += self.gen_bdy_block('    ', '%s action code' % name)
            txt += ['}']
            txt += ['']
        txt += ['/*']
        txt += [' * Initialize the Class to use these functions']
        txt += [' */']
        txt += ['void %s(void)' % self.mkFunc('ClassInit')]
        txt += ['{']
        for action in self.Actions():
            txt += ['    %s(%s, %s);' % (self.mkFunc('ClassSetAction'), self.mkAction(action.name), action.name)]
        txt += ['}']
        txt += ['']
        txt += ['/*']
        txt += [' * Example function to construct the instance']
        txt += [' * Also sets the private data and private destructor (or NULL)']
        txt += [' */']
        txt += ['static %s make(' % self.mkName()]
        txt += ['    char *name,']
        txt += ['    %s initialState,' % self.mkState()]
        txt += ['    void *pPrivate,']
        txt += ['    void (*pKiller)(void *))']
        txt += ['{']
        txt += ['    %s smi;' % self.mkName()]
        txt += ['    smi = %s(name, initialState);' % (self.mkFunc('InstanceMake'))]
        txt += ['    %s(smi, pPrivate, pKiller);' % (self.mkFunc('SetPrivate'))]
        txt += ['    return smi;']
        txt += ['}']
        txt += ['']
        txt += ['/* Place function definitions, used in the action code, here */']
        txt += self.gen_bdy_block('', 'control code')
        txt += ['']
        txt += ['#ifdef UNIT_TEST']
        txt += ['']
        txt += ['/* Place function definitions, used in the test code, here */']
        txt += self.gen_bdy_block('', 'test code')
        txt += ['']
        txt += ['int main(int argc, char *argv[])']
        txt += ['{']
        txt += ['    %s smi;' % self.mkName()]
        txt += ['    %s_PRIVATE_DATA private_data;' % self.mkName()]
        txt += ['']
        txt += ['    %s();' % self.mkFunc('ClassInit')]
        txt += ['    memset(&private_data, 0, sizeof(private_data));']
        txt += ['    smi = make(']
        txt += ['        "test", %s,' % self.mkState('')]
        txt += ['        &private_data, NULL);']
        txt += ['    %s(smi,' % self.mkFunc('SetReportFunc')]
        txt += ['        NULL);']
        txt += ['']
        txt += ['    /* test something */']
        txt += self.gen_bdy_block('    ', 'main code')
        txt += ['']
        txt += ['    %s(smi);' % self.mkFunc('InstanceKill')]
        txt += ['    return EXIT_SUCCESS;']
        txt += ['}']
        txt += ['']
        txt += ['#endif /* UNIT_TEST */']
        lines_parked = 0
        parked = {}
        for block in self.code_blocks:
            if block not in self.done_blocks:
                parked[block] = self.code_blocks[block]
        if len(parked) > 0:
            print "Blocks Parked:", sorted(parked.keys())
            lines_parked = sum([len(self.code_blocks[block]) for block in parked])
            print "Lines parked:", lines_parked
            txt += ['#if 0 /* BEGIN PARKING LOT {{{*/']
            for block in parked.keys():
                txt += self.gen_bdy_block('', block)
            txt += ['#endif /* END PARKING LOT }}}*/']
        print "Custom Lines:", lines_emitted
        txt += ['']
        txt += ['/*']
        txt += [' * vim: ft=c ts=8 sts=4 sw=4 et cindent']
        txt += [' */']
        return txt

    def gen_skl(self):
        return self.gen_bdy_skel()

    def gen_bdy_fsm(self):
        txt = []
        txt += ['static %s action_funcs[%s+1];' % (self.mkFunc('Action'), self.mkName('NUM_ACTIONS'))]
        txt += ['', '/* State Machine Class */']
        txt += ['typedef struct fsmStateMachine_t fsmStateMachine;']
        txt += ['struct fsmStateMachine_t {']
        txt += ['    char *name;']
        txt += ['    int numStates;']
        txt += ['    int numEvents;']
        txt += ['    int numActions;']
        txt += ['    const %s *stateTable;' % (self.mkState())]
        txt += ['    const %s *eventTable;' % (self.mkEvent())]
        txt += ['    const %s *actionTable;' % (self.mkAction())]
        txt += ['    %s entryEvent;' % self.mkEvent()]
        txt += ['    %s exitEvent;' % self.mkEvent()]
        txt += ['    %s *actionTab; /* Class Actions */' % self.mkFunc('Action')]
        txt += ['};']
        txt += ['', '/* Event Queue Entry */']
        txt += ['typedef struct EventQueueEntry_t {']
        txt += ['    struct EventQueueEntry_t *next;']
        txt += ['    %s_EVENT ev;' % self.mkName()]
        txt += ['    void *pContext;']
        txt += ['} *pQueueEntry;']
        txt += ['', '/* State Machine Instance */']
        txt += ['struct %s_t {' % self.mkName()]
        txt += ['    char *name;']
        txt += ['    const fsmStateMachine *fsm;']
        txt += ['    %s *actionTab; /* Instance Actions */' % self.mkFunc('Action')]
        txt += ['    %s currentState;' % self.mkState()]
        txt += ['    void (*reportFunc)(%s smi, const char *fmt, ...);' % self.mkName()]
        txt += ['    void *pPrivate; /* private */']
        txt += ['    void (*pKiller)(void*);']
        txt += ['    struct {']
        txt += ['        pQueueEntry pHead;']
        txt += ['        pQueueEntry pTail;']
        txt += ['        int iLength;']
        txt += ['    } EventQueue, EmptyQueue;']
        txt += ['};']
        txt += ['', '/* State Machine Initializer */']
        txt += ['static const fsmStateMachine fsm_%s = {' % self.name]
        txt += ['    .name="%s",' % self.name]
        txt += ['    .numStates=%s,' % self.mkName('NUM_STATES')]
        txt += ['    .numEvents=%s,' % self.mkName('NUM_EVENTS')]
        txt += ['    .numActions=%s,' % self.mkName('NUM_ACTIONS')]
        txt += ['    .stateTable=%s_table,' % (self.mkState())]
        txt += ['    .eventTable=%s_table,' % (self.mkEvent())]
        txt += ['    .actionTable=%s_table,' % (self.mkAction())]
        txt += ['    .entryEvent=&s%s,' % self.mkEvent('Entry')]
        txt += ['    .exitEvent=&s%s,' % self.mkEvent('Exit')]
        txt += ['    .actionTab=action_funcs']
        txt += ['};', '']
        return txt

    def gen_bdy_unit_test(self):
        txt = ['', '#ifdef UNIT_TEST']
        for action in self.Actions():
            txt += ['static %s %s_test(' % (self.mkEvent(), self.mkAction(action))]
            txt += ['        %s smi,' % self.mkName()]
            txt += ['        %s state,' % self.mkState()]
            txt += ['        %s event,' % self.mkEvent()]
            txt += ['        void *pContext,']
            txt += ['        void *pPrivate)']
            txt += ['{']
            if self.isClassifier(action.name):
                next_event = self.getTargets(action.name)[0]
                txt += ['    printf("State: %%-20s, Event: %%-20s, Classifier: %-20s, NextEvent: %s\\n", state->name, event->name);' % (action, next_event)]
                txt += ['    return %s;' % self.mkEvent(next_event)]
            else:
                txt += ['    printf("State: %%-20s, Event: %%-20s, ActionFunc: %-20s\\n", state->name, event->name);' % action]
                txt += ['    return NULL;']
            txt += ['}', '']
        txt += ['static void register_%s_actions(void) {' % (self.name)]
        for action in self.Actions():
            txt += ['    %s(%s, %s_test);'\
                    % (self.mkFunc('ClassSetAction'), self.mkAction(action), self.mkAction(action))]
        txt += ['};', '']
        txt += ['static void test_%s_actions(void) {' % (self.name)]
        txt += ['    %s smi;' % (self.mkName())]
        txt += ['    int state;']
        txt += ['    int event;']
        txt += ['    int idx;']
        txt += ['    register_%s_actions();' % (self.name), '']
        txt += ['    smi = %s("test", %s);' % (self.mkFunc('InstanceMake'), self.mkState(self.states[0]))]
        txt += ['    for (state = 1; state <= %s; ++state)' % self.mkName('NUM_STATES')]
        txt += ['        for (event = 1; event <= %s; ++event) {' % self.mkName('NUM_EVENTS')]
        txt += ['                const fsmTransTab *tab = %s_table[state]->transTab[event];' % (self.mkState())]
        txt += ['                if (tab) {']
        txt += ['                    smi->currentState = %s_table[state];' % (self.mkState())]
        txt += ['                    %s(smi, %s_table[event], NULL);' % (self.mkFunc('InstanceRun'), self.mkEvent())]
        txt += ['                    if (smi->currentState->index != state)']
        txt += ['                        printf("       %%s ===> %%s\\n", %s_table[state]->name, smi->currentState->name);' % (self.mkState())]
        txt += ['                }']
        txt += ['            }']
        for test in self.tests:
            # print "Test::", test
            txt += ['    do {']
            txt += ['        smi->currentState = %s;' % self.mkState(test.tests[0])]
            for t in test.tests:
                if self.getState(t):
                    txt += ['        if (smi->currentState != %s) {' % self.mkState(t)]
                    txt += ['            printf("State is %%s but expected %s\\n", smi->currentState->name);' % t]
                    txt += ['            break;']
                    txt += ['        }']
                else:
                    txt += ['        %s(smi, %s, NULL);' % (self.mkFunc('InstanceRun'), self.mkEvent(t))]
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
        return txt

    def gen_bdy_Code(self):
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
        txt += ['    if (action_funcs[0] == NULL)']
        txt += ['        %s();' % (self.mkFunc('ClassInit'))]
        txt += ['    smi->name = strdup(name);']
        txt += ['    smi->fsm = &fsm_%s;' % self.name]
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
        txt += ['    if (smi->actionTab)']
        txt += ['        free(smi->actionTab);']
        txt += ['    if (smi->pPrivate && smi->pKiller)']
        txt += ['        (*smi->pKiller)(smi->pPrivate);']
        txt += ['    while (smi->EmptyQueue.pHead) {']
        txt += ['        pQueueEntry entry;']
        txt += ['        entry = smi->EmptyQueue.pHead;']
        txt += ['        smi->EmptyQueue.pHead = smi->EmptyQueue.pHead->next;']
        txt += ['        free(entry);']
        txt += ['    }']
        txt += ['    free(smi);']
        txt += ['}']
        txt += ['']
        txt += ['/* Run one Event for this Instance of this Statemachine */']
        txt += ['static %s %s('% (self.mkState(), self.mkFunc('RunStateEvent'))]
        txt += ['    %s smi,' % (self.mkName())]
        txt += ['    %s ev,' % (self.mkEvent())]
        txt += ['    void *pContext)']
        txt += ['{']
        txt += ['    int i, j, k;']
        txt += ['    int nTrans=0, nActns=0;']
        txt += ['    %s next_event = NULL;' % self.mkEvent()]
        txt += ['    %s next_state = smi->currentState;' % self.mkState()]
        txt += ['    const fsmStateMachine *fsm = smi->fsm;']
        txt += ['    const fsmTransTab *tab = NULL;']
        txt += ['    do {']
        txt += ['        next_event = NULL;']
        txt += ['        if (ev == NULL) {']
        txt += ['            return next_state;']
        txt += ['        }']
        txt += ['        tab = next_state->transTab[ev->index];']
        txt += ['        if (tab) {']
        txt += ['            fsmActionType actionType = tab->ac_type;']
        txt += ['            %s fn;' % self.mkFunc('Action')]
        txt += ['            ++nTrans;']
        txt += ['            switch (actionType) {']
        txt += ['                case fsmActionClass:']
        txt += ['                    k = tab->ac_code;']
        txt += ['                    fn = fsm->actionTab[k];']
        txt += ['                    if (smi->actionTab && smi->actionTab[k])']
        txt += ['                        fn = smi->actionTab[k];']
        txt += ['                    if (smi->reportFunc)']
        txt += ['                        (*smi->reportFunc)(smi,']
        txt += ['                            "%s(%s) -> %s",']
        txt += ['                            smi->currentState->name,']
        txt += ['                            ev->name,']
        txt += ['                            fsm->actionTable[k]->name);']
        txt += ['                    next_event = (*fn)(smi, smi->currentState, ev, pContext, smi->pPrivate);']
        txt += ['                    ev = next_event;']
        txt += ['                    break;']
        txt += ['                case fsmActionTrans:']
        txt += ['                    if (tab->ac_code)']
        txt += ['                        next_state = fsm->stateTable[tab->ac_code];']
        txt += ['                    nActns = 0;']
        txt += ['                    for (j = 0; tab->ac_list[j]; ++ j) {']
        txt += ['                        ++nActns;']
        txt += ['                        k = tab->ac_list[j];']
        txt += ['                        fn = fsm->actionTab[k];']
        txt += ['                        if (smi->actionTab && smi->actionTab[k])']
        txt += ['                            fn = smi->actionTab[k];']
        txt += ['                        if (smi->reportFunc)']
        txt += ['                            (*smi->reportFunc)(smi,']
        txt += ['                                "%s(%s) [%s]",']
        txt += ['                                smi->currentState->name,']
        txt += ['                                ev->name,']
        txt += ['                                fsm->actionTable[k]->name);']
        txt += ['                        (void) (*fn)(smi, smi->currentState, ev, pContext, smi->pPrivate);']
        txt += ['                    }']
        txt += ['                    if (nActns == 0) /* no actions reported */']
        txt += ['                        if (smi->reportFunc)']
        txt += ['                            (*smi->reportFunc)(smi,']
        txt += ['                                "%s(%s) [<no actions>]",']
        txt += ['                                smi->currentState->name,']
        txt += ['                                ev->name);']
        txt += ['                    break;']
        txt += ['            }']
        txt += ['        }']
        txt += ['        if (nTrans == 0) /* event not handled */']
        txt += ['            if (smi->reportFunc)']
        txt += ['                (*smi->reportFunc)(smi,']
        txt += ['                    "%s(%s) [<unhandled>]",']
        txt += ['                    smi->currentState->name,']
        txt += ['                    ev->name);']
        txt += ['    } while (next_event);']
        txt += ['    return next_state;']
        txt += ['}']
        txt += ['']
        txt += ['void %s(%s smi, %s ev, void *pContext)'\
                % (self.mkFunc('InstanceRun'), self.mkName(), self.mkEvent())]
        txt += ['{']
        txt += ['    pQueueEntry event;']
        txt += ['    if (smi->EmptyQueue.pHead) {']
        txt += ['        event = smi->EmptyQueue.pHead;']
        txt += ['        --smi->EmptyQueue.iLength;']
        txt += ['        smi->EmptyQueue.pHead = event->next;']
        txt += ['        if (smi->EmptyQueue.pHead == NULL)']
        txt += ['            smi->EmptyQueue.pTail = NULL;']
        txt += ['        else']
        txt += ['            event->next = NULL;']
        txt += ['    } else {']
        txt += ['        event = calloc(1, sizeof(struct EventQueueEntry_t));']
        txt += ['        /* TODO: check return */']
        txt += ['        if (smi->reportFunc)']
        txt += ['            (*smi->reportFunc)(smi,']
        txt += ['                "new event queue entry in %s(%s)",']
        txt += ['                smi->currentState->name,']
        txt += ['                ev->name);']
        txt += ['    }']
        txt += ['    event->ev = ev;']
        txt += ['    event->pContext = pContext;']
        txt += ['    /* the current event is always on the queue */']
        txt += ['    /* if queue is busy, we must have recursed */']
        txt += ['    if (smi->EventQueue.pHead) {']
        txt += ['       /* push this event on the tail and return */']
        txt += ['        smi->EventQueue.pTail->next = event;']
        txt += ['        smi->EventQueue.pTail = event;']
        txt += ['        ++smi->EventQueue.iLength;']
        txt += ['        if (smi->reportFunc)']
        txt += ['            (*smi->reportFunc)(smi,']
        txt += ['                "recursive event in %s(%s) is %s",']
        txt += ['                smi->currentState->name,']
        txt += ['                smi->EventQueue.pHead->ev->name,']
        txt += ['                ev->name);']
        txt += ['        return;']
        txt += ['    } else {']
        txt += ['       /* push this event on the queue and continue */']
        txt += ['        smi->EventQueue.pHead = smi->EventQueue.pTail = event;']
        txt += ['        ++smi->EventQueue.iLength;']
        txt += ['    }']
        txt += ['    while (event) {']
        txt += ['        ev = event->ev;']
        txt += ['        pContext = event->pContext;']
        txt += ['        %s next_state = %s(smi, ev, pContext);'\
                % (self.mkState(), self.mkFunc('RunStateEvent'))]
        txt += ['        while (next_state != smi->currentState) {']
        txt += ['            if (smi->fsm->exitEvent)']
        txt += ['                %s(smi, smi->fsm->exitEvent, pContext);'\
                % self.mkFunc('RunStateEvent')]
        txt += ['            if (smi->reportFunc)']
        txt += ['                (*smi->reportFunc)(smi,']
        txt += ['                    "%s ==> %s",']
        txt += ['                    smi->currentState->name,']
        txt += ['                    next_state->name);']
        txt += ['            smi->currentState = next_state;']
        txt += ['            if (smi->fsm->entryEvent)']
        txt += ['                next_state = %s(smi, smi->fsm->entryEvent, pContext);'\
                % self.mkFunc('RunStateEvent')]
        txt += ['        }']
        txt += ['        /* push current event onto empty queue */']
        txt += ['        if (smi->EmptyQueue.pHead) {']
        txt += ['            smi->EmptyQueue.pTail->next = event;']
        txt += ['            smi->EmptyQueue.pTail = event;']
        txt += ['            return;']
        txt += ['        } else {']
        txt += ['            smi->EmptyQueue.pHead = smi->EmptyQueue.pTail = event;']
        txt += ['        }']
        txt += ['        ++smi->EmptyQueue.iLength;']
        txt += ['        /* pop the current event off the event queue */']
        txt += ['        --smi->EventQueue.iLength;']
        txt += ['        smi->EventQueue.pHead = event->next;']
        txt += ['        if (smi->EventQueue.pHead == NULL)']
        txt += ['            smi->EventQueue.pTail = NULL;']
        txt += ['        /* new event is on the head of the queue */']
        txt += ['        event = smi->EventQueue.pHead;']
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
        txt += ['    if (action->index > 0 && action->index <= %s) {'\
                % self.mkName('NUM_ACTIONS')]
        txt += ['        if (smi->actionTab == NULL)']
        txt += ['            smi->actionTab = (%s *) calloc(%s + 1, sizeof(%s));'\
                % (self.mkFunc('Action'), self.mkName('NUM_ACTIONS'), self.mkFunc('Action'))]
        txt += ['        smi->actionTab[action->index] = func;']
        txt += ['    }']
        txt += ['}']
        txt += ['', '/* Report Function accessors */']
        txt += ['void %s(%s smi,'\
                % (self.mkFunc('SetReportFunc'), self.mkName())]
        txt += ['    void (*reportFunc)(%s smi, const char *fmt, ...))'\
                % (self.mkName())]
        txt += ['{']
        txt += ['    smi->reportFunc = reportFunc;']
        txt += ['}']
        txt += ['void (*%s(%s smi))(%s smi, const char *fmt, ...)'\
                % (self.mkFunc('GetReportFunc'), self.mkName(), self.mkName())]
        txt += ['{']
        txt += ['    return smi->reportFunc;']
        txt += ['}']
        txt += ['', '/* Private data accessors */']
        txt += ['void %s(%s smi, void *data, void (*pKiller)(void *))' % (self.mkFunc('SetPrivate'), self.mkName())]
        txt += ['{']
        txt += ['    smi->pPrivate = data;']
        txt += ['    smi->pKiller = pKiller;']
        txt += ['}']
        txt += ['void *%s(%s smi)' % (self.mkFunc('GetPrivate'), self.mkName())]
        txt += ['{']
        txt += ['    return smi->pPrivate;']
        txt += ['}']
        txt += ['const char *%s(%s smi)' % (self.mkFunc('GetName'), self.mkName())]
        txt += ['{']
        txt += ['    return smi->name;']
        txt += ['}']
        return txt
