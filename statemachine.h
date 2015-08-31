#ifndef STATEMACHINE_H
#define STATEMACHINE_H

typedef int fsmState;
typedef int fsmEvent;
typedef int fsmAction;
typedef enum { fsmActionClass = 1, fsmActionTrans = 2 } fsmActionType;

typedef struct fsmTransTab_t  fsmTransTab;
typedef struct fsmStateMachine_t fsmStateMachine;
typedef struct fsmInstance_t fsmInstance;

typedef int (*fsmActionFunc) (fsmInstance *smi, fsmState state, fsmEvent event);
typedef fsmActionFunc **fsmActionTab;

struct fsmTransTab_t {
    fsmState si;
    fsmEvent ei;
    fsmState so;
    fsmActionType ac_type;
    int ac_start;
    int ac_count;
};

/*
 * The State Machine Type
 *
 * This is initialised for the type of statemachine and used by all instances
 */
struct fsmStateMachine_t {
    char *name;
    int numStates;
    int numEvents;
    int numTrans;
    int numActions;
    int maxActions;
    int *mapTab;
    int *actTab;
    char **stateNames;
    char **eventNames;
    char **actionNames;
    fsmTransTab *transTab;
    fsmActionFunc *actionTab;
};
/*
 * The State Machine Instance
 *
 * Holds instance data and points to the type
 */
struct fsmInstance_t {
    char *name;
    fsmStateMachine *fsm;
    int currentState;
    void *priv; /* private */
    void (*killPriv)(void*);
};

fsmInstance *fsmMakeInstance(fsmStateMachine *fsm, fsmState initial);

int fsmRunStateMachine(fsmInstance *smi, fsmEvent ev);

void fsmSetActionFunction(fsmStateMachine *t, fsmAction action, fsmActionFunc func);

void fsmPrintInstance(fsmInstance *smi);
void fsmPrintStateMachine(fsmStateMachine *fsm);

#endif /* STATEMACHINE_H */
/*
 * vim: ts=8 sts=4 sw=4 ai cindent
 */
