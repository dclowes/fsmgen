#include "statemachine.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

fsmActionTab *fsmMakeActionTab(int numActions) {
    fsmActionTab *act;
    act = (fsmActionTab *) calloc(numActions + 1, sizeof(fsmActionFunc));
    return act;
}

void fsmKillActionTab(fsmActionTab *act) {
    free(act);
}

fsmInstance *fsmMakeInstance(fsmStateMachine *fsm, fsmState initial) {
    fsmInstance *smi;
    smi = (fsmInstance *) calloc(1, sizeof(fsmInstance));
    smi->fsm = fsm;
    smi->currentState = initial;
    return smi;
}

void fsmPrintInstance(fsmInstance *smi) {
    printf("StateMachine Instance %s of type %s in state %s\n",
            smi->name,
            smi->fsm->name,
            smi->fsm->stateNames[smi->currentState]);
}

void fsmPrintStateMachine(fsmStateMachine *fsm) {
    int i, j, slen, elen, alen, zlen;
    printf("StateMachine: %s\n", fsm->name);
    printf("  numStates:  %d\n", fsm->numStates);
    printf("  numEvents:  %d\n", fsm->numEvents);
    printf("  numTrans:   %d\n", fsm->numTrans);
    printf("  numActions: %d\n", fsm->numActions);
    printf("  maxActions: %d\n", fsm->maxActions);

    slen = 0;
    for (i = 0; i < fsm->numStates; ++i)
        if ((zlen = strlen(fsm->stateNames[i + 1])) > slen)
            slen = zlen;
    elen = 0;
    for (i = 0; i < fsm->numEvents; ++i)
        if ((zlen = strlen(fsm->eventNames[i + 1])) > elen)
            elen = zlen;
    alen = 0;
    for (i = 0; i < fsm->numActions; ++i)
        if ((zlen = strlen(fsm->actionNames[i + 1])) > alen)
            alen = zlen;
    zlen = slen;
    if (elen > zlen) zlen = elen;
    if (alen > zlen) zlen = alen;

    printf("\n  States:");
    for (i = 0; i < fsm->numStates; ++i)
        printf("%s%-*s", (i%5 == 0) ? "\n    " : ", ", zlen, fsm->stateNames[i + 1]);

    printf("\n  Events:");
    for (i = 0; i < fsm->numEvents; ++i)
        printf("%s%-*s", (i%5 == 0) ? "\n    " : ", ", zlen, fsm->eventNames[i + 1]);

    printf("\n  Actions:");
    for (i = 0; i < fsm->numActions; ++i)
        printf("%s%-*s", (i%5 == 0) ? "\n    " : ", ", zlen, fsm->actionNames[i + 1]);

    printf("\n  Transitions:\n");
    for (i = 0; i < fsm->numTrans; ++i) {
        printf("    %-*s(%-*s)", slen, fsm->stateNames[fsm->transTab[i].si],
                elen, fsm->eventNames[fsm->transTab[i].ei]);
            for (j = 0; j < fsm->transTab[i].ac_count; ++j) {
                int act = fsm->transTab[i].ac_start + j;
                char *action = fsm->actionNames[fsm->actTab[act]];
                printf("%s%-*s", j == 0 ? ": " : ", ", alen, action);
            }
        if (fsm->transTab[i].so) {
            printf(" => %s", fsm->stateNames[fsm->transTab[i].so]);
        }
        printf("\n");
    }
}

int fsmRunStateMachine(fsmInstance *smi, fsmEvent ev) {
    int i, j;
    fsmEvent next_event = 0;
    fsmState next_state = smi->currentState;
    fsmStateMachine *fsm = smi->fsm;
    do {
        next_event = 0;
        if (ev < 1 || ev > fsm->numEvents) {
            return -1;
        }
        for (i = fsm->mapTab[smi->currentState]; i < fsm->mapTab[smi->currentState + 1]; ++i) {
            if (fsm->transTab[i].ei == ev) {
                fsmTransTab *tab = &fsm->transTab[i];
                fsmActionType actionType = tab->ac_type;
                if (tab->so)
                    next_state = tab->so;
                for (j = 0; j < tab->ac_count; ++ j) {
                    int k = fsm->actTab[tab->ac_start + j];
                    fsmActionFunc fn = fsm->actionTab[k];
                    switch (actionType) {
                        case fsmActionClass:
                            next_event = (*fn)(smi, smi->currentState, ev);
                            ev = next_event;
                            break;
                        case fsmActionTrans:
                            (void) (*fn)(smi, smi->currentState, ev);
                            break;
                    }
                }
                break;
            }
        }
    } while (next_event > 0);
    smi->currentState = next_state;
    return 0;
}

void fsmSetActionFunction(fsmStateMachine *t, fsmAction action, fsmActionFunc func) {
    if (action > 0 && action <= t->numActions)
        t->actionTab[action] = func;
}

/*
 * vim: ts=8 sts=4 sw=4 ai cindent
 */
