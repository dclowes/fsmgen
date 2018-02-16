# Statemachine
The statemachine has:
* states - a statemachine starts in a state and transitions between states based on *events* received
* actions - are performed by the statemachine in processing an *event*
* events - may cause the statemachine to invoke *actions* or change *states*
* special_events - which are synthesised by the statemachine;
* transactions - the processing of an event in the context of a state;
* tests - sequences of states joined by one or more events that describe an expected transition. sequence

The statemachine has a finite number of states. The statemachine is started in a state, the initial state. Any state may be an initial state, determined at creation of the statemachine. The statemachine may transition between states but is only ever in one state.

The statemachine processes one event at a time. Events may be queued to the statemachine while the statemachine is processing an event, until the statemachine is able to process the event.

The statemachine may have private data such as counters, timers and buffers. The private data may vary depending on the state.

## States
A state is simply the state that the statemachine is in. Events will be processed by the statemachine in the context of the state that the statemachine is in. The same event may produce different effects in different states.

A state may inherit transactions from a base state and override only those events that require a different transaction.
## Events
A statemachine processes an event is the context of the state it is in. It may cause actions to be executed. It may cause other events to be produced. It may cause a change of state.

An event may be a command message from the program or a signal message from another statemachine or a message from an external source.

## Special Events
Special events don't actually exist but are processed by the statemachine like a normal event.

These include:
* Entry - is produced by the transition between states and is executed in the context of the new state,
* Exit - is produced by the transition between states and is executed in the context of the old state,
* Default - is executed in the context of the state when an event is not handled.

## Actions
An action is something that a statemachine does in response to an event. It may change the statemachines private data, or produce a new event for the same, or another statemachine. It may cause external changes such as opening or closing a file.

## Transactions
A transaction is the processing that happens for an event in a particular state. The same event, when the statemachine is in the same state, will be processed by the same transaction.

A transaction is an ordered sequence of actions and, optionally, a transfer state. When a statemachine is processing an event, it processes the sequence of actions of the transaction in order. When all of the actions have been processed, if the transaction specifies a transfer state then the state transfer is processed.

Each action may return a new event or not. If an action returns a new event, it will terminate the current sequence of actions and start a new transaction.

In normal operation, the processing of the sequence of actions proceeds in order. However if a new event is produced by any action, the sequence of actions is terminated, and that event is queued to the statemachine at the head of the event queue. This causes the new event to be processed next.

A transaction may specify a target state which will be processed after all actions have been processed, if no action has produced a new event. If no target state is specified for the transaction then the statemachine remains in the current state.

This mechanism allows an action to "classify" an event, or to produce an exception. Any further actions or a transfer state specified for the transaction is ignored. The new event is processed immediately in the context of the current state.

# Syntax
````
STATEMACHINE statemachine_name
{
  OUTPUT output_1[,...];
  STATES state_1["comment"][,...];
  EVENTS event_1["comment"][,...];
  ACTIONS action_1["comment"][,...];
  STATE state_in
  {
    event_in [-> action_1[, ...]] [--> event_out_1[,...]] [=> state_out];
    [...]
  }
  TEST state_1,event_1[,...],state_N;
  CODE action_1
  {
    @[CODE=]C|TCL|GCC|PYTHON
    text
    @END
    [...]
  }
}
````
