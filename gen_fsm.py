#!/usr/bin/env python
# Author: Douglas Clowes (douglas.clowes@ansto.gov.au) Aug 2015
# vim: ft=python ts=8 sts=4 sw=4 expandtab autoindent smartindent
#

# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=missing-docstring
# pylint: disable=global-statement
#
import os
import re
import ply.lex as lex
import ply.yacc as yacc
import statemachine

Statemachine = None
Statemachines = []
lexer = None
yaccer = None
Verbose = None
args = None

states = (
    ('tcl', 'exclusive'),
    )

def FormatEvent(event):
    if len(event) > 1 and len(event[1]) > 0:
        txt = "%s(%s)" % (event[0], ", ".join(event[1]))
    else:
        txt = "%s" % (event[0])
    return txt

def Build_StateMachine(sm):
    action_list = []
    classifier_list = []
    test_list = []
    new_sm = statemachine.StateMachine(sm['Name'])
    the_states = sorted(sm['States'])
    print '**The States:', the_states
    for s in the_states:
        new_sm.addState(statemachine.State(s))
    the_events = []
    for b in sm['Blocks']:
        print "**The Block:", b
        for t in sm['Blocks'][b]:
            print "**The Transit:", t
            if t[1] not in the_events:
                the_events.append(t[1])
                if len(t[1]) > 1:
                    the_args = t[1][1]
                else:
                    the_args = []
                new_sm.addEvent(statemachine.Event(t[1][0], the_args))
            if t[0] == 1:
                new_sm.addClassifier(statemachine.Classifier(b, t[1][0], t[2], t[3]))
            else:
                new_sm.addTransition(statemachine.Transition(b, t[1][0], t[2], t[3]))

    the_events = sorted(the_events)
    print '**The Events:', [FormatEvent(e) for e in the_events]

    new_sm.printit()
    return new_sm

def Generate_Python(sm):
    action_list = []
    classifier_list = []
    test_list = []
    func_name = 'StateSwitch_%s'  % sm['Name']
    txt = ['def %s(state, event):' % func_name]
    txt += ['    next_state = state']
    txt += ['    next_event = None']
    the_states = sorted(sm['States'])
    print '**The States:', the_states
    the_events = []
    for b in sm['Blocks']:
        for t in sm['Blocks'][b]:
            if t[1] not in the_events:
                the_events.append(t[1])
    the_events = sorted(the_events)
    print '**The Events:', [FormatEvent(e) for e in the_events]
    for s in the_states:
        txt += ['    if state == "%s":' % s]
        for e in the_events:
            for block in sm['Blocks'][s]:
                #print "Block:", block
                if e == block[1]:
                    #txt += ['<TD VALIGN="top"><B>%s</B></TD>' % s]
                    txt += ['        if event == "%s":' % FormatEvent(e)]
                    for action in block[2]:
                        if block[0] in [1]:
                            txt += ['            next_event = %s(state, event)' % (action)]
                            if action not in [c[0] for c in classifier_list]:
                                classifier_list.append((action, block[3]))
                        else:
                            txt += ['            %s(state, event)' % (action)]
                            if action not in action_list:
                                action_list.append(action)
                    if block[0] in [3, 4]:
                        txt += ['            next_state = "%s"' % (block[3][0])]
                        test_list.append((s, e, block[3][0]))
                    else:
                        test_list.append((s, e, s))
                    txt += ['            return (next_state, next_event)']
    txt += ['    return (next_state, next_event)']
    txt += ['']
    slen = max([len(s) for s in the_states])
    elen = max([len(FormatEvent(e)) for e in the_events])
    txt += ['if __name__ == "__main__":']
    print "Classifiers:", classifier_list
    for action in classifier_list:
        txt += ['    def %s(state, event):' % action[0]]
        line = '"State %%-%ds event %%-%ds: %s" %% (state, event)' % (slen, elen, action[0])
        txt += ['        print %s' % line]
        txt += ['        return "%s"' % action[1][0][0]]
    print "Actions:", action_list
    for action in action_list:
        txt += ['    def %s(state, event):' % action]
        line = '"State %%-%ds event %%-%ds: %s" %% (state, event)' % (slen, elen, action)
        txt += ['        print %s' % line]
    print "Tests:", test_list
    for test in test_list:
        s1 = test[0]
        ev = FormatEvent(test[1])
        s2 = test[2]
        txt += ['    assert %s("%s", "%s")[0] == "%s"' % (func_name, s1, ev, s2)]
    return txt

def Generate_TCL(sm):
    action_list = []
    classifier_list = []
    test_list = []
    func_name = 'StateSwitch_%s'  % sm['Name']
    txt = ['proc %s {state event} {' % func_name]
    txt += ['    set next_state ${state}']
    txt += ['    set next_event {}']
    the_states = sorted(sm['States'])
    print '**The States:', the_states
    the_events = []
    for b in sm['Blocks']:
        for t in sm['Blocks'][b]:
            if t[1] not in the_events:
                the_events.append(t[1])
    the_events = sorted(the_events)
    print '**The Events:', [FormatEvent(e) for e in the_events]
    for s in the_states:
        txt += ['    if {${state} == "%s"} {' % s]
        for e in the_events:
            for block in sm['Blocks'][s]:
                #print "Block:", block
                if e == block[1]:
                    #txt += ['<TD VALIGN="top"><B>%s</B></TD>' % s]
                    txt += ['        if {${event} == "%s"} {' % FormatEvent(e)]
                    for action in block[2]:
                        if block[0] in [1]:
                            txt += ['            set next_event [%s ${state} ${event}]' % (action)]
                            if action not in [c[0] for c in classifier_list]:
                                classifier_list.append((action, block[3]))
                        else:
                            txt += ['            %s ${state} ${event}' % (action)]
                            if action not in action_list:
                                action_list.append(action)
                    if block[0] in [3, 4]:
                        txt += ['            set next_state "%s"' % (block[3][0])]
                        test_list.append((s, e, block[3][0]))
                    else:
                        test_list.append((s, e, s))
                    txt += ['            return [list ${next_state} ${next_event}]']
                    txt += ['        }']
        txt += ['        return [list ${next_state} ${next_event}]']
        txt += ['    }']
    txt += ['    return [list ${next_state} ${next_event}]']
    txt += ['}']
    slen = max([len(s) for s in the_states])
    elen = max([len(FormatEvent(e)) for e in the_events])
    txt += ['if { "[lindex [split [info nameofexecutable] "/"] end]" == "tclsh"} {']
    print "Classifiers:", classifier_list
    for action in classifier_list:
        txt += ['    proc %s {state event} {' % action[0]]
        line = 'State [format "%%-%ds" ${state}] event [format "%%-%ds" ${event}]: %s' %\
                (slen, elen, action[0])
        txt += ['        puts "%s"' % line]
        txt += ['        return "%s"' % action[1][0][0]]
        txt += ['    }']
    print "Actions:", action_list
    for action in action_list:
        txt += ['    proc %s {state event} {' % action]
        line = 'State [format "%%-%ds" ${state}] event [format "%%-%ds" ${event}]: %s' %\
                (slen, elen, action)
        txt += ['        puts "%s"' % line]
        txt += ['    }']
    for test in test_list:
        s1 = test[0]
        ev = FormatEvent(test[1])
        s2 = test[2]
        txt += ['    if {[lindex [%s "%s" "%s"] 0] != "%s"} {error "fail!"}' % (func_name, s1, ev, s2)]
    txt += ['} else {']
    for action in action_list:
        if action in sm['Code'] and sm['Code'][action]['type'] == 'action':
            txt += ['    proc %s {state event} {' % action]
            txt += ['        ' + s for s in sm['Code'][action]['text']]
            txt += ['    }']
    txt += ['}']
    return txt

def PrintStateMachine(sm):
    print "Statemachine:"
    for key in sorted(sm.keys()):
        print key, sm[key]
    print
    txt = []
    txt += ['digraph G {']
    txt += ['  size="11,8";']
    txt += ['  ratio="expand";']
    txt += ['  rankdir=LR;']
    txt += ['  node [shape=plaintext];']
    txt += ['  labelloc="t";']
    txt += ['  label=<<B>%s</B>>' % sm['Filename']]
    txt += ['']
    if len(sm['Events']) > 0:
        print "Events:", ", ".join([FormatEvent(e) for e in sorted(sm['Events'])])
    if len(sm['States']) > 0:
        print "States:", ", ".join(sorted(sm['States']))
        for state in sorted(sm['States']):
            print "    %s" % state
            if state in sm['Blocks']:
                label = ['<TABLE><TR><TD PORT="f0"><B>']
                label += ['%s' % state]
                label += ['</B></TD></TR>']
                for idx, event in enumerate(sm['Blocks'][state]):
                    if len(event[2]) > 0:
                        label += ['<TR><TD><TABLE>']
                        label += ['<TR><TD PORT="f%d"><B>%s</B></TD></TR>' % (idx + 1, FormatEvent(event[1]))]
                        label += ['<TR><TD>%s</TD></TR>' % '</TD></TR><TR><TD>'.join(event[2])]
                        label += ['</TABLE></TD></TR>']
                    else:
                        label += ['<TR><TD PORT="f%d">%s</TD></TR>' % (idx + 1, FormatEvent(event[1]))]
                label += ['</TABLE>']
                txt += ['  %s[label=<%s>];' % (state, ''.join(label))]
                for idx, event in enumerate(sm['Blocks'][state]):
                    line = "        %s" % FormatEvent(event[1])
                    if event[0] in [1]:
                        line += " --> %s" % ", ".join(event[2])
                    elif event[0] in [2, 4]:
                        line += " -> %s" % ", ".join(event[2])
                    if event[0] in [3, 4]:
                        line += " => %s" % ", ".join(event[3])
                        for e in event[3]:
                            txt += ['    %s:f%d -> %s:f0;' % (state, idx + 1, e)]
                    print line
    txt += ['}']
    return txt

def PrintParseError(message):
    print message
#
# Reserved words (keywords) in the form reserved['KEYWORD'] = 'TOKEN'
#

reserved = {
    'STATEMACHINE': 'STATEMACHINE',
    'STATES': 'STATES',
    'STATE': 'STATE',
    'EVENTS': 'EVENTS',
    'EVENT': 'EVENT',
    'CODE' : 'CODE',
}

def ReportP(p, locn):
    if Verbose:
        print locn, ": {",
        for i in range(len(p)):
            if i == 0:
                print "%s" % repr(p[i]),
            else:
                print ", %s" % repr(p[i]),
        print "}"
#
# Tokens list with keyword tokens added at the end
#

tokens = [
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'SLASH',
    'COMMA',
    'COLON',
    'INTEGER',
    'FLOATER',
    'CODE_STRING',
    'TEXT_STRING1',
    'TEXT_STRING2',
    'EQUALS',
    'ID',
    'AT_TCL',
    'AT_END',
    'DISPATCH',
    'CLASSIFIER',
    'TRANSITION',
    ] + list(reserved.values())

#
# Token rules
#

t_EQUALS = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'{'
t_RBRACE = r'}'
t_SLASH = r'/'
t_COMMA = r','
t_COLON = r':'

def t_AT_TCL(t):
    r'@TCL'
    if Verbose:
        print 'AT_TCL'
    t.lexer.begin('tcl')
    t.value = "@TCL"
    return t

def t_tcl_AT_END(t):
    r'[ \t]*@END'
    if Verbose:
        print 'AT_END'
    t.lexer.begin('INITIAL')
    t.value = "@END"
    return t


t_tcl_ignore = ""

def t_tcl_CODE_STRING(t):
    r'.+'
    if t.value[0] == '@':
        t.value = t.value[1:]
    if Verbose:
        print 'TCL:', t.value
    return t

def t_tcl_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_tcl_error(t):
    message = "Illegal tcl character '%s'" % t.value[0]
    PrintParseError(message)
    t.lexer.skip(1)

def t_TEXT_STRING1(t):
    r'\'[^\']*\''
    t.value = t.value[1:-1]
    return t

def t_TEXT_STRING2(t):
    r"\"[^\"]*\""
    t.value = t.value[1:-1]
    return t


def t_CLASSIFIER(t):
    r'-->'
    return t

def t_DISPATCH(t):
    r'->'
    return t

def t_TRANSITION(t):
    r'=>'
    return t

def t_COMMENT(t):
    r'\#.*'
    pass
    # No Return Value. Token discarded

def t_FLOATER(t):
    r'-?\d+\.\d*([eE]\d+)?'
    try:
        t.value = float(t.value)
    except ValueError:
        message = "Floating value invalid: " + repr(t.value)
        PrintParseError(message)
        t.value = 0.0
    return t

def t_INTEGER(t):
    r'-?\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        message = "Integer value too large: " + repr(t.value)
        PrintParseError(message)
        t.value = 0
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value.upper(), 'ID')    # Check for reserved words
    # Force reserved words to lower case for map lookup and comparisson
    if t.value.upper() in reserved:
        t.type = reserved[t.value.upper()]
        t.value = t.value.lower()
    return t

# Ignored characters
t_ignore = " \t;"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    message = "Illegal character '%s' at line %d" % \
          (t.value[0], t.lexer.lineno)
    PrintParseError(message)
    t.lexer.skip(1)

#
# Parser
#

#
# Parsing rules
#

#
# We don't yet have a need for precedence so leave it empty here
#
precedence = (
    #('left','PLUS','MINUS'),
    #('left','TIMES','DIVIDE'),
    #('right','UMINUS'),
    )

#
# The head token - it all reduces to this
#
def p_fsm(p):
    'fsm : STATEMACHINE id_or_str fsm_block'
    p[0] = [{'Statemachine' : {p[2] : p[3]}}]
    if Verbose:
        print "Statemachine:", p[0]
    Statemachine['Name'] = p[2]
    new_sm = Build_StateMachine(Statemachine)
    Statemachines.append(new_sm)

def p_fsm_block(p):
    'fsm_block : LBRACE fsm_statement_list RBRACE'
    p[0] = p[2]

def p_fsm_statement_list(p):
    '''fsm_statement_list : fsm_statement
                      | fsm_statement_list fsm_statement
                      '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_fsm_statement(p):
    '''fsm_statement : EVENTS event_list
                 | STATES state_list
                 | STATE state_block
                 | CODE code
    '''
    p[0] = p[1]

def p_state_list(p):
    '''
    state_list : state_type
          | state_list COMMA state_type
    '''
    if len(p) > 3:
        if p[3] not in Statemachine['States']:
            Statemachine['States'].append(p[3])
        p[0] = p[1] + [p[3]]
    else:
        if p[1] not in Statemachine['States']:
            Statemachine['States'].append(p[1])
        p[0] = [p[1]]

def p_state_type(p):
    '''
    state_type : id_or_str
    '''
    p[0] = p[1]

def p_event_list(p):
    '''
    event_list : event_type
               | event_list COMMA event_type
    '''
    ReportP(p, "event_list")
    if len(p) > 3:
        if p[3] not in Statemachine['Events']:
            Statemachine['Events'].append(p[3])
        p[0] = p[1] + [p[3]]
    else:
        if p[1] not in Statemachine['Events']:
            Statemachine['Events'].append(p[1])
        p[0] = [p[1]]

def p_event_type(p):
    '''
    event_type : id_or_str
               | id_or_str LPAREN id_list RPAREN
    '''
    if len(p) > 2:
        p[0] = [p[1], p[3]]
    else:
        p[0] = [p[1], []]

def p_state_block(p):
    '''
    state_block : id_or_str EQUALS LBRACE state_code_list RBRACE
    '''
    ReportP(p, "state_block")
    Statemachine['Blocks'][p[1]] = p[4]
    p[0] = [p[1]] + p[4]

def p_state_code_list(p):
    '''
    state_code_list : empty
                    | state_code_list state_code
    '''
    if len(p) > 2:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_state_code(p):
    '''
    state_code : state_code_1
               | state_code_2
               | state_code_3
               | state_code_4
    '''
    p[0] = p[1]

def p_state_code_1(p): # Classifier
    '''
    state_code_1 : event_type CLASSIFIER id_or_str TRANSITION event_list
    '''
    p[0] = [1, p[1], [p[3]], p[5]]

def p_state_code_2(p): # Action only
    '''
    state_code_2 : event_type DISPATCH id_list
    '''
    p[0] = [2, p[1], p[3], []]

def p_state_code_3(p): # Transition only
    '''
    state_code_3 : event_type TRANSITION state_list
    '''
    p[0] = [3, p[1], [], p[3]]

def p_state_code_4(p): # Action and Transition
    '''
    state_code_4 : event_type DISPATCH id_list TRANSITION state_list
    '''
    ReportP(p, "state_code")
    p[0] = [4, p[1], p[3], p[5]]

def p_id_list(p):
    '''
    id_list : id_or_str
            | id_list COMMA id_or_str
    '''
    ReportP(p, "id_list")
    if len(p) > 2:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

#
# The CODE block
#
def p_code(p):
    '''
    code : code_type id_or_str EQUALS LBRACE code_block RBRACE
    '''
    Statemachine['Code'][p[2]] = {'name' : p[2], 'type' : p[1], 'text' : p[5]}
    p[0] = {'Code' : {'name' : p[2], 'type' : p[1], 'text' : p[5]}}

def p_code_type(p):
    '''
    code_type : id_or_str
    '''
    p[0] = p[1]

def p_code_block(p):
    '''
    code_block : tcl_code_block
    '''
    ReportP(p, "code_block")
    p[0] = p[1]

def p_tcl_code_block(p):
    '''
    tcl_code_block : AT_TCL code_list AT_END
    '''
    ReportP(p, "tcl_code_block")
    p[0] = p[2]

def p_code_list(p):
    '''
    code_list : empty
              | code_list CODE_STRING
    '''
    ReportP(p, "code_list")
    if len(p) > 2:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_id_or_str(p):
    '''
    id_or_str : ID
              | text_string
    '''
    p[0] = p[1]

def p_text_string(p):
    '''
    text_string : TEXT_STRING1
                | TEXT_STRING2
    '''
    p[0] = p[1]

def p_empty(p):
    '''
    empty :
    '''
    pass

def p_error(t):
    message = "Syntax error at line %d" % lexer.lineno
    message += " " + repr(t)
    message += " " + repr(t.value)
    PrintParseError(message)

def load_file(source_file, depth_list):
    SourceFile = os.path.realpath(os.path.abspath(source_file))
    fd = open(SourceFile, 'r')
    LocalData = []
    for line in fd:
        line = line.rstrip('\n')
        LocalData.append(line)
    fd.close()
    return LocalData

def process_source(source_file):
    global Statemachine
    Statemachine = {}
    Statemachine['Filename'] = source_file
    Statemachine['States'] = []
    Statemachine['Events'] = []
    Statemachine['Blocks'] = {}
    Statemachine['Code'] = {}
    SourceData = load_file(source_file, [])
    if args.yaccdebug:
        yaccer.parse('\n'.join(SourceData), debug=True)
    else:
        yaccer.parse('\n'.join(SourceData))
    if Verbose:
        print "Statemachine:", Statemachine
    new_sm = statemachine.StateMachine_Text(Statemachines[0])

    txt = PrintStateMachine(Statemachine)
    text = open("%s.dot" % source_file, "w")
    text.write('\n'.join(txt))
    text.close()
    dot_cmd = "%s -Tsvg -o %s.svg %s.dot" % (args.dot, source_file, source_file)
    print dot_cmd
    os.system(dot_cmd)

    txt = new_sm.DotStateMachine()
    text = open("%s.new.dot" % source_file, "w")
    text.write('\n'.join(txt))
    text.close()
    dot_cmd = "%s -Tsvg -o %s.new.svg %s.new.dot" % (args.dot, source_file, source_file)
    print dot_cmd
    os.system(dot_cmd)

    text = open("%s.html" % source_file, "w")
    text.write('<HTML>\n')
    text.write('<TITLE>Finite State Machine %s</TITLE>\n' % source_file)
    text.write('<TABLE BORDER=8 ALIGN="center">\n')
    text.write('<TR><TD><TABLE BORDER=0 ALIGN="center">\n')
    text.write('<TR><TD ALIGN="left">\n')
    text.write('<PRE>' + '\n'.join(SourceData) + '</PRE>')
    text.write('</TD><TD>\n')
    text.write('<PRE>' + '\n'.join(new_sm.TextStateMachine()) + '</PRE>')
    text.write('</TD></TR></TABLE>\n')
    text.write('<TR><TD ALIGN="center">State Table 1<BR/>\n')
    txt = new_sm.StateTable1()
    text.write('\n'.join(txt))
    text.write('</TD></TR>\n')
    text.write('<TR><TD ALIGN="center">State Table 2<BR/>\n')
    txt = new_sm.StateTable2()
    text.write('\n'.join(txt))
    text.write('</TD></TR>\n')
    text.write('<TR><TD ALIGN="center">State Table 3<BR/>\n')
    txt = new_sm.StateTable3()
    text.write('\n'.join(txt))
    text.write('</TD></TR>\n')
    text.write('<TR><TD ALIGN="left">\n')
    txt = Generate_Python(Statemachine)
    with open('%s.py' % source_file, 'w') as fdo:
        fdo.write('\n'.join(txt))
    text.write('<PRE>' + '\n'.join(txt) + '</PRE>')
    text.write('<TR><TD ALIGN="left">\n')
    txt = Generate_TCL(Statemachine)
    text.write('<PRE>' + '\n'.join(txt) + '</PRE>')
    with open('%s.tcl' % source_file, 'w') as fdo:
        fdo.write('\n'.join(txt))
    text.write('</TD></TR>\n')
    text.write('<TR><TD ALIGN="center">State Diagram New 1<BR/>\n')
    text.write('<img src="%s.new.svg" alt="%s.new.svg"/>\n' % (source_file, source_file))
    text.write('</TD></TR>\n')
    text.write('<TR><TD ALIGN="center">State Diagram 1<BR/>\n')
    text.write('<img src="%s.svg" alt="%s.svg"/>\n' % (source_file, source_file))
    text.write('</TD></TR>\n')
    text.write('</TABLE>\n')
    text.write('</HTML>\n')
    text.close()

def main():
    global lexer, yaccer
    global Verbose
    global args
    import argparse

    graphviz = ['dot', 'circo', 'neato', 'fdp', 'sfdp', 'twopi', 'osage', 'patchwork']
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dot", default="dot", choices=graphviz, help="graphviz layout tool to use")
    parser.add_argument("-l", "--lexdebug", help="lex debug output",
                        action="store_true")
    parser.add_argument("-y", "--yaccdebug", help="yacc debug output",
                        action="store_true")
    parser.add_argument("-v", "--verbose", help="verbose output",
                        action="store_true")
    parser.add_argument("driver_source", help="driver source file", nargs="*")
    args = parser.parse_args()
    if args.verbose:
        Verbose = True
        print args
    else:
        Verbose = False
    source_files = args.driver_source    #
    if source_files and len(source_files) > 0:
        # Build the lexer
        #
        if args.lexdebug:
            lexer = lex.lex(debug=1)
        else:
            lexer = lex.lex()


        #
        # Build the parser
        #
        #yaccer = yacc.yacc(tabmodule="gen_sct",outputdir="/tmp",write_tables=0,debug=0)
        yaccer = yacc.yacc(debug=0)

        for source_file in source_files:
            process_source(source_file)

if __name__ == "__main__":
    main()
