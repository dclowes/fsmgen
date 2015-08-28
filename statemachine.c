#include "statemachine.h"
#include <stdlib.h>
#include <stdio.h>

fsmActionTab *fsmMakeActionTab(int numActions) {
  fsmActionTab *act;
  act = (fsmActionTab *) calloc(numActions + 1, sizeof(fsmActionFunc));
  return act;
}

void fsmKillActionTab(fsmActionTab *act) {
  free(act);
}

fsmInstance *fsmMakeInstance(fsmStateMachine *fsm, fsmState initial) {
  fsmInstance *sm;
  sm = (fsmInstance *) calloc(1, sizeof(fsmInstance));
  sm->fsm = fsm;
  sm->currentState = initial;
  return sm;
}

void fsmPrintInstance(fsmInstance *sm) {
  printf("StateMachine Instance %s of %s in state %s\n",
      sm->name,
      sm->fsm->name,
      sm->fsm->stateNames[sm->currentState]);
}

int fsmRunStateMachine(fsmInstance *sm, fsmEvent ev) {
  int i, j;
  fsmStateMachine *fsm = sm->fsm;
  while (ev) {
    if (ev < 1 || ev > fsm->numStates) {
      return -1;
    }
    for (i = fsm->mapTab[sm->currentState]; i < fsm->mapTab[sm->currentState + 1]; ++i) {
      if (fsm->transTab[i].ei == ev) {
        fsmTransTab *tab = &fsm->transTab[i];
        fsmActionType actionType = tab->ac_type;
        for (j = 0; j < tab->ac_count; ++ j) {
          int k = fsm->actTab[tab->ac_start + j];
          fsmActionFunc *fn = fsm->actionTab[k];
          switch (actionType) {
            case fsmActionClass:
              ev = (*fn)(sm, sm->currentState, ev);
              break;
            case fsmActionTrans:
              (void) (*fn)(sm, sm->currentState, ev);
              break;
          }
        }
        break;
      }
    }
  }
  return 0;
}

void fsmSetActionFunction(fsmStateMachine *t, fsmAction action, fsmActionFunc *func) {
  if (action > 0 && action <= t->numActions)
    t->actionTab[action] = func;
}

