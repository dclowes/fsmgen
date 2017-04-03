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

from statemachine import StateMachine_Text
from statemachine import Classifier, Transition
import statemachine

class StateMachine_GCC(StateMachine_Text):
    def __init__(self, other):
        StateMachine_Text.__init__(self, other)
        self.Inheritance()
        self.prefix = 'FSM_'
        self.prefix = ''
        self.code_blocks = {}
        self.done_blocks = []

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

    def mkAction(self, that=None):
        txt = ''
        if that:
            if isinstance(that, statemachine.Action):
                txt = that.name
            else:
                txt = that
            return  self.prefix + '%s_ACTION_%s' % (self.uname, txt)
        return  self.prefix + '%s_ACTION' % (self.uname)

    def mkActionFunc(self, action):
        txt = []
        txt += ['static %s %s(' % (self.mkEvent(), action)]
        txt += ['    %s smi,' % self.mkName()]
        txt += ['    %s state,' % self.mkState()]
        txt += ['    %s event,' % self.mkEvent()]
        txt += ['    void *pContext,']
        txt += ['    void *pPrivate)']
        return txt

    def mkTrans(self, state, event):
        return "%s_TRANS_%s_%s" % (self.uname, state, event)

    def Generate_Hdr(self, stts, evts, acts):
        '''
        Generate the FSM header filer
        '''
        hdr = []
        hdr += ['#ifndef %s_FSM_H' % self.uname]
        hdr += ['#define %s_FSM_H' % self.uname]
        # States
        hdr += ['', '/* States */']
        hdr += ['typedef const struct %s_t *%s;'\
                % (self.mkState(), self.mkState())]
        for item in stts:
            hdr += ['extern const %s %s;'\
                    % (self.mkState(), self.mkState(item[0]))]
        # Events
        hdr += ['', '/* Events */']
        hdr += ['typedef const struct %s_t *%s;'\
                % (self.mkEvent(), self.mkEvent())]
        for item in evts:
            hdr += ['extern const %s %s;'\
                    % (self.mkEvent(), self.mkEvent(item[0]))]
        # Actions
        hdr += ['', '/* Actions */']
        hdr += ['typedef const struct %s_t *%s;'\
                % (self.mkAction(), self.mkAction())]
        for item in acts:
            hdr += ['extern const %s %s;'\
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

        hdr += ['', '#endif /* %s_FSM_H */' % self.uname]
        return hdr

    def Absorb_Skel(self, file_name):
        '''
        This method reads an existing skeleton file and loads self.code_blocks
        with the code between custom code markers in the skeleton file.

        This code can later be emitted in place of the boilerplate to preserve
        custom code development if the state machine is later regenerated.
        '''
        import re
        target = None
        self.code_blocks = {}
        try:
            with open(file_name, "r") as fd:
                lines = fd.read().splitlines()
        except IOError:
            lines = []
        for line in lines:
            if "BEGIN CUSTOM:" in line:
                target = re.sub(r'.*BEGIN CUSTOM: (.*) {.*', r'\1', line)
                self.code_blocks[target] = []
                continue
            if "END CUSTOM:" in line:
                if len(self.code_blocks[target]) == 1:
                    if self.code_blocks[target][0] == "    return NULL;":
                        del self.code_blocks[target]
                target = None
                continue
            if target:
                self.code_blocks[target].append(line)
#       for target in self.code_blocks:
#           print "Target:", target, len(self.code_blocks[target])

    def Generate_Skel(self):
        hdr = []
        txt = []
        code_blocks = self.code_blocks
        txt += ['#include "%s.fsm.h"' % self.name]
        txt += ['#include <stdlib.h>']
        txt += ['/* BEGIN CUSTOM: include files {{{*/']
        if 'include files' in self.code_blocks:
            txt += self.code_blocks['include files']
            del self.code_blocks['include files']
        txt += ['/* END CUSTOM: include files }}}*/']
        txt += ['']
        the_blocks = [b for b in self.classifiers + self.transitions]
        the_actions = []
        for block in the_blocks:
            for action in block.actions:
                if action not in the_actions:
                    the_actions.append(action)
        the_actions = sorted(the_actions)
#        for action in the_actions:
#            code = self.mkActionFunc(action)
#            code[-1] += ';'
#            txt += code
#        txt += ['']
        txt += ['/* @brief private data type used in action routines */']
        txt += ['typedef %s_PRIVATE_DATA *pPRIVATE_DATA;' % self.mkName()]
        txt += ['']
        txt += ['/* BEGIN CUSTOM: forward declarations {{{*/']
        if 'forward declarations' in self.code_blocks:
            txt += self.code_blocks['forward declarations']
            del self.code_blocks['forward declarations']
        else:
            txt += ['/* Place forward declarations, used in the action code, here */']
        txt += ['/* END CUSTOM: forward declarations }}}*/']
        txt += ['']
        for action in the_actions:
            if self.isClassifier(action):
                txt += ['/* Classifier returns: */']
                for target in self.getTargets(action):
                    txt += ['/*    %s */' % self.mkEvent(target)]
            else:
                txt += ['/* Transition: returns NULL */']
            a = self.getAction(action)
            if a and len(a.comments) > 0:
                txt += ['/* Comments: */']
                for line in a.comments:
                    txt += ['/*    %s */' % line]
            txt += self.mkActionFunc(action)
            txt += ['{']
            txt += ['    pPRIVATE_DATA self = (pPRIVATE_DATA) pPrivate;']
            txt += ['    /* BEGIN CUSTOM: %s action code {{{*/' % action]
            if '%s action code' % action in self.code_blocks:
                txt += self.code_blocks['%s action code' % action]
                del self.code_blocks['%s action code' % action]
            else:
                txt += ['    return NULL;']
            txt += ['    /* END CUSTOM: %s action code }}}*/' % action]
            txt += ['}']
            txt += ['']
        txt += ['/*']
        txt += [' * Initialize the Class to use these functions']
        txt += [' */']
        txt += ['void %s(void)' % self.mkFunc('ClassInit')]
        txt += ['{']
        for action in the_actions:
            txt += ['    %s(%s, %s);' % (self.mkFunc('ClassSetAction'), self.mkAction(action), action)]
        txt += ['}']
        txt += ['']
        txt += ['/*']
        txt += [' * Example function to construct the instance']
        txt += [' * Aslo sets the private data and private destructor (or NULL)']
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
        txt += ['/* BEGIN CUSTOM: control code {{{*/']
        if 'control code' in self.code_blocks:
            txt += self.code_blocks['control code']
            del self.code_blocks['control code']
        else:
            txt += ['/* Place function definitions, used in the action code, here */']
            txt += ['']
            txt += ['#ifdef UNIT_TEST']
            txt += ['/* Place unit test code here */']
            txt += ['']
            txt += ['/* Place unit test code main code here */']
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
            txt += ['    /* TODO: test something */']
            txt += ['    %s(smi);' % self.mkFunc('InstanceKill')]
            txt += ['    return EXIT_SUCCESS;']
            txt += ['}']
            txt += ['']
            txt += ['#endif /* UNIT_TEST */']
            txt += ['']
            txt += ['/*']
            txt += [' * vim: ft=c ts=8 sts=4 sw=4 et cindent']
            txt += [' */']
        txt += ['/* END CUSTOM: control code }}}*/']
        lines_parked = 0
        if len(self.code_blocks) > 0:
            txt += ['#if 0 /* BEGIN PARKING LOT {{{*/']
            for block in self.code_blocks.keys():
                txt += ['/* BEGIN CUSTOM: %s {{{*/' % block]
                lines_parked += len(self.code_blocks[block])
                txt += self.code_blocks[block]
                txt += ['/* END CUSTOM: %s }}}*/' % block]
                del self.code_blocks[block]
            txt += ['#endif /* END PARKING LOT }}}*/']
            print "Lines parked:", lines_parked
        print "Custom Lines:", sum([len(code_blocks[block]) for block in code_blocks])
        return (hdr, txt)

    def Generate_Code(self):
        hdr = []
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
        txt += ['                ++nTrans;']
        txt += ['                switch (actionType) {']
        txt += ['                    case fsmActionClass:']
        txt += ['                        k = tab->u.c.ac_class;']
        txt += ['                        fn = fsm->actionTab[k];']
        txt += ['                        if (smi->actionTab && smi->actionTab[k])']
        txt += ['                            fn = smi->actionTab[k];']
        txt += ['                        if (smi->reportFunc)']
        txt += ['                            (*smi->reportFunc)(smi,']
        txt += ['                                "%s(%s) -> %s",']
        txt += ['                                smi->currentState->name,']
        txt += ['                                ev->name,']
        txt += ['                                action_pointers[k].name);']
        txt += ['                        next_event = (*fn)(smi, smi->currentState, ev, pContext, smi->pPrivate);']
        txt += ['                        ev = next_event;']
        txt += ['                        break;']
        txt += ['                    case fsmActionTrans:']
        txt += ['                        if (tab->u.t.so)']
        txt += ['                            next_state = tab->u.t.so;']
        txt += ['                        nActns = 0;']
        txt += ['                        for (j = 0; j < tab->u.t.ac_count; ++ j) {']
        txt += ['                            ++nActns;']
        txt += ['                            k = fsm->actTab[tab->u.t.ac_start + j]->index;']
        txt += ['                            fn = fsm->actionTab[k];']
        txt += ['                            if (smi->actionTab && smi->actionTab[k])']
        txt += ['                                fn = smi->actionTab[k];']
        txt += ['                            if (smi->reportFunc)']
        txt += ['                                (*smi->reportFunc)(smi,']
        txt += ['                                    "%s(%s) [%s]",']
        txt += ['                                    smi->currentState->name,']
        txt += ['                                    ev->name,']
        txt += ['                                    action_pointers[k].name);']
        txt += ['                            (void) (*fn)(smi, smi->currentState, ev, pContext, smi->pPrivate);']
        txt += ['                        }']
        txt += ['                        if (nActns == 0) /* no actions reported */']
        txt += ['                            if (smi->reportFunc)']
        txt += ['                                (*smi->reportFunc)(smi,']
        txt += ['                                    "%s(%s) [<no actions>]",']
        txt += ['                                    smi->currentState->name,']
        txt += ['                                    ev->name);']
        txt += ['                        break;']
        txt += ['                }']
        txt += ['                break;']
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
        return (hdr, txt)

    def Generate_Actions(self, acts):
        txt = ['']
        txt += ['/* Actions */']
        txt += ['struct %s_t {' % self.mkAction()]
        txt += ['    char *name;']
        txt += ['    int  index;']
        txt += ['};']
        txt += ['enum {']
        for item in acts:
            txt += ['    e%s = %s,' % (self.mkAction(item[0]), item[1])]
        txt += ['};']
        txt += ['']
        txt += ['static const struct %s_t action_pointers [] = {' % self.mkAction()]
        txt += ['    { NULL, %s },' % self.mkName('NUM_ACTIONS')]
        for item in acts:
            txt += ['    { "%s", %d },'\
                    % (item[0], item[1])]
        txt += ['    { NULL, 0 }']
        txt += ['};']
        txt += ['']
        for item in acts:
            txt += ['const %s %s = &action_pointers[%d];'\
                    % (self.mkAction(), self.mkAction(item[0]), item[1])]
        txt += ['']
        txt += ['static char *action_names[] = {']
        txt += ['    0,']
        for item in acts:
            txt += ['    "%s",' % (item[0])]
        txt += ['    0', '};', '']
        return txt

    def Generate_Events(self, evts):
        txt = ['']
        txt += ['/* Events */']
        txt += ['struct %s_t {' % self.mkEvent()]
        txt += ['    char *name;']
        txt += ['    int  index;']
        txt += ['};']
        txt += ['']
        txt += ['enum {']
        for item in evts:
            txt += ['    e%s = %s,' % (self.mkEvent(item[0]), item[1])]
        txt += ['};']
        txt += ['']
        txt += ['static const struct %s_t event_pointers [] = {' % self.mkEvent()]
        txt += ['    { NULL, %s },' % self.mkName('NUM_EVENTS')]
        for item in evts:
            txt += ['    { "%s", %d },'\
                    % (item[0], item[1])]
        txt += ['    { NULL, 0 }']
        txt += ['};']
        txt += ['']
        for item in evts:
            txt += ['const %s %s = &event_pointers[%d];'\
                    % (self.mkEvent(), self.mkEvent(item[0]), item[1])]
        txt += ['']
        txt += ['static char *event_names[] = {']
        txt += ['    0,']
        for item in evts:
            txt += ['    "%s",' % (item[0])]
        txt += ['    0', '};', '']
        return txt

    def Generate_States(self, stts):
        txt = ['']
        txt += ['/* States */']
        txt += ['struct %s_t {' % self.mkState()]
        txt += ['    char *name;']
        txt += ['    int  index;']
        txt += ['};']
        txt += ['']
        txt += ['enum {']
        for item in stts:
            txt += ['    e%s = %s,' % (self.mkState(item[0]), item[1])]
        txt += ['};']
        txt += ['']
        txt += ['static const struct %s_t state_pointers [] = {' % self.mkState()]
        txt += ['    { NULL, %s },' % self.mkName('NUM_STATES')]
        for item in stts:
            txt += ['    { "%s", %d },'\
                    % (item[0], item[1])]
        txt += ['    { NULL, 0 }']
        txt += ['};']
        txt += ['']
        for item in stts:
            txt += ['const %s %s = &state_pointers[%d];'\
                    % (self.mkState(), self.mkState(item[0]), item[1])]
        txt += ['']
        txt += ['static char *state_names[] = {', '    0,']
        for item in stts:
            txt += ['    "%s",' % (item[0])]
        txt += ['    0', '};', '']
        return txt

    def Generate_Trans(self, the_states, the_events, the_blocks, classifier_list):
        txt = []
        txt += ['', '/* Transition Table Structures */']
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
        txt += ['        } c;']
        txt += ['        struct { /* Transition Action Entry */']
        txt += ['            %s so;        /* Output State */' % self.mkState()]
        txt += ['            int ac_start; /* First Action */']
        txt += ['            int ac_count; /* Number of Actions */']
        txt += ['        } t;']
        txt += ['    } u;']
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
                            line += '        .u.t.so=&state_pointers[e%s],\n' % self.mkState(target)
                            line += '        .u.t.ac_start=%d,\n' % act_idx
                            line += '        .u.t.ac_count=%d,\n' % act_cnt
                        else:
                            evt_cnt = len(block.targets)
                            for item in block.targets:
                                evt_txt += ['    &event_pointers[e%s],' % self.mkEvent(item)]
                            line += '        .ac_type=fsmActionClass,\n'
                            line += '        .u.c.ac_class=e%s,\n' % self.mkAction(block.actions[0])
                            line += '        .u.c.ev_start=%d,\n' % evt_idx
                            evt_idx += evt_cnt
                            line += '        .u.c.ev_count=%s,\n' % evt_cnt
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
        # print "tkns:", tkns
        # print "stts:", stts
        # print "evts:", evts
        # print "acts:", acts

        hdr = self.Generate_Hdr(stts, evts, acts)

        txt = []
        txt += ['#include <stdlib.h>']
        txt += ['#include <stdio.h>']
        txt += ['#include <string.h>']
        txt += ['']
        for item in tkns:
            txt += ['#define %s %d'\
                    % (self.mkName(item[0]), item[1])]

        # Actions
        txt += self.Generate_Actions(acts)
        # Events
        txt += self.Generate_Events(evts)
        # States
        txt += self.Generate_States(stts)
        # Transition Table Structures
        txt += self.Generate_Trans(the_states, the_events, the_blocks, classifier_list)
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
        code = self.Generate_Code()
        hdr += code[0]
        txt += code[1]
        txt += ['', '#ifdef UNIT_TEST']
        # txt += ['', '#ifdef SKELETON']
        # txt += ['/* Start Skeleton */']
        # code = self.Generate_Skel()
        # hdr += code[0]
        # txt += code[1]
        # txt += ['/* End Skeleton */']
        # txt += ['#endif /* SKELETON */', '']
        for action in the_actions:
            txt += ['static %s %s_test(' % (self.mkEvent(), self.mkAction(action))]
            txt += ['        %s smi,' % self.mkName()]
            txt += ['        %s state,' % self.mkState()]
            txt += ['        %s event,' % self.mkEvent()]
            txt += ['        void *pContext,']
            txt += ['        void *pPrivate)']
            txt += ['{']
            if action in classifier_list:
                next_event = classifier_list[action]
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
        txt += ['                    %s(smi, &event_pointers[event], NULL);' % self.mkFunc('InstanceRun')]
        txt += ['                    if (smi->currentState->index != state)']
        txt += ['                        printf("       %s ===> %s\\n", state_names[state], smi->currentState->name);']
        txt += ['                }']
        txt += ['            }']
        for test in self.tests:
            # print "Test::", test
            txt += ['    do {']
            txt += ['        smi->currentState = %s;' % self.mkState(test.tests[0])]
            for t in test.tests:
                if t in the_states:
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
        return (hdr, txt)
