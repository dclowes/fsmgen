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

class StateMachine_GCC2(StateMachine_GCC):
    def __init__(self, other):
        StateMachine_GCC.__init__(self, other)

    def Generate_Trans(self, the_states, the_events, the_blocks, classifier_list):
        txt = StateMachine_GCC.Generate_Trans(self, the_states, the_events, the_blocks, classifier_list)
#       return txt
        txt += ['#if 0']
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
        txt += ['struct fsmTransEvent {']
        txt += ['  fsmTransTab tab[];']
        txt += ['};']
        txt += ['struct fsmTransState {']
        txt += ['  fsmTransEvent event[%s + 1];' % self.mkName('NUM_EVENTS')]
        txt += ['};']
        trans = {}
        for state in the_states:
            for event in the_events:
                this_block = [b for b in the_blocks if b.source == state and b.event == event]
                if len(this_block) == 1:
                    txt += ['static fsmTransTab %s = {' % self.mkTrans(state, event)]
                    trans[self.mkTrans(state, event)] = True
                    txt += ['};']
                elif len(this_block) == 0:
                    pass
                else:
                    print "Error: multiple blocks", this_block
        txt += self.GenStates()
        txt += ['#endif /* 0 */']
        return txt

    def GenStates(self):
        the_states = sorted([s.name for s in self.states])
        the_events = sorted([e.name for e in self.events])
        the_blocks = [b for b in self.classifiers + self.transitions]
        txt = ['']
        txt += ['struct fsmState_t {']
        txt += ['    int index;']
        txt += ['    char *name;']
        txt += ['    struct fsmStateEvent *trans[%s + 1];' % self.mkName('NUM_EVENTS')]
        txt += ['};', '']
        for state in the_states:
            txt += ['']
            txt += ['struct fsmState_t %s = {' % self.mkState(state)]
            txt += ['    e%s,' % self.mkState(state)]
            txt += ['    "%s",' % state]
            txt += ['    {']
            txt += ['        NULL, /* Dummy */']
            for event in the_events:
                this_block = [b for b in the_blocks if b.source == state and b.event == event]
                if this_block:
                    txt += ['        &%s,' % self.mkTrans(state, event)]
                else:
                    txt += ['        NULL, /* %s */' % self.mkTrans(state, event)]
            txt += ['    }']
            txt += ['};', '']
        return txt

    def Generate_Code(self):
        print "Generating Code ..."
        hdr, txt = StateMachine_GCC.Generate_Code(self)
        return (hdr, txt)
