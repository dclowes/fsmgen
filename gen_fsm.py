#!/usr/bin/env python
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
# pylint: disable=missing-docstring
# pylint: disable=global-statement
# pylint: disable=unused-argument
#
import os
#import re
import ply.lex as lex
import ply.yacc as yacc
import statemachine
from generate_gcc import StateMachine_GCC2, StateMachine_GCC3

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
    new_sm = statemachine.StateMachine(sm['Name'])
    the_states = sorted(sm['States'])
    the_bases = sorted(sm['Inherits'])
    new_sm.outputs = sorted(sm['Outputs'])
    if Verbose:
        print '**The States:', the_states
        print '**The Bases:', the_bases
    for s in the_states:
        if s in sm['Inherits']:
            state = statemachine.State(s, sm['Inherits'][s])
        else:
            state = statemachine.State(s)
        new_sm.addState(state)
    the_events = []
    for b in sm['Blocks']:
        if Verbose:
            print "**The Block:", b
        for t in sm['Blocks'][b]:
            if Verbose:
                print "**The Transit:", t
            if t[1] not in the_events:
                the_events.append(t[1])
                if len(t[1]) > 1:
                    the_args = t[1][1]
                else:
                    the_args = []
                new_sm.addEvent(statemachine.Event(t[1][0], the_args))
            if t[0] == 1:
                new_sm.addClassifier(statemachine.Classifier(b, t[1][0], t[2], [x[0] for x in t[3]]))
                for e in t[3]:
                    if Verbose:
                        print "**Classified:", e
                    if e not in the_events:
                        the_events.append(e)
                        if len(e) > 1:
                            the_args = e[1]
                        else:
                            the_args = []
                        new_sm.addEvent(statemachine.Event(e[0], the_args))
            else:
                new_sm.addTransition(statemachine.Transition(b, t[1][0], t[2], t[3]))
    for a in sorted(sm['Actions']):
        action = statemachine.Action(a)
        new_sm.addAction(action)
        if a in sm['Code']:
            code = sm['Code'][a]
            if Verbose:
                print "**The Code:", a, code
            for text_block in code['text']:
                action.code_text[text_block[0]] = text_block[1]

    for t in sm['Tests']:
        new_sm.addTest(statemachine.Test(t))

    the_events = sorted(the_events)
    if Verbose:
        print '**The Events:', [FormatEvent(e) for e in the_events]
    for s in new_sm.states:
        if s.name in sm['State_Comments']:
            s.comments += sm['State_Comments'][s.name]
    for e in new_sm.events:
        if e.name in sm['Event_Comments']:
            e.comments += sm['Event_Comments'][e.name]
    for a in new_sm.actions:
        if a.name in sm['Action_Comments']:
            a.comments += sm['Action_Comments'][a.name]
    if Verbose:
        print '***The Actions:', sm['Actions']
        print '***The Actions:', sm['Action_Comments']
    if Verbose:
        print "PRINTIT**"
        new_sm.printit()
    return new_sm

def PrintParseError(message):
    print message
#
# Reserved words (keywords) in the form reserved['KEYWORD'] = 'TOKEN'
#

reserved = {
    'STATEMACHINE': 'STATEMACHINE',
    'ACTIONS': 'ACTIONS',
    'OUTPUT': 'OUTPUT',
    'STATES': 'STATES',
    'EVENTS': 'EVENTS',
    'ACTION': 'ACTION',
    'STATE': 'STATE',
    'EVENT': 'EVENT',
    'CODE' : 'CODE',
    'TEST' : 'TEST',
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
    'AT_C',
    'AT_PYTHON',
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

def t_AT_C(t):
    r'@C'
    if Verbose:
        print 'AT_C'
    t.lexer.begin('tcl')
    t.value = "@C"
    return t

def t_AT_PYTHON(t):
    r'@PYTHON'
    if Verbose:
        print 'AT_PYTHON'
    t.lexer.begin('tcl')
    t.value = "@PYTHON"
    return t

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
    '''
    fsm : STATEMACHINE id_or_str fsm_block
    '''
    p[0] = [{'Statemachine' : {p[2] : p[3]}}]
    if Verbose:
        print "Statemachine:", p[0]
    Statemachine['Name'] = p[2]
    new_sm = Build_StateMachine(Statemachine)
    Statemachines.append(new_sm)

def p_fsm_block(p):
    '''
    fsm_block : LBRACE fsm_statement_list RBRACE
              | EQUALS LBRACE fsm_statement_list RBRACE
    '''
    if len(p) > 4: # it has the EQUALS in there
        p[0] = p[3]
    else:
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
                 | TEST test_list
                 | ACTIONS action_list
                 | OUTPUT output_list
    '''
    p[0] = [p[1], p[2]]

def p_output_list(p):
    '''
    output_list : id_list
    '''
    p[0] = p[1]
    for outp in p[1]:
        if outp.upper() not in Statemachine['Outputs']:
            Statemachine['Outputs'].append(outp.upper())
def p_state_list(p):
    '''
    state_list : state_type
          | state_list comma state_type
    '''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_state_type(p):
    '''
    state_type : id_or_str
               | state_type text_string
    '''
    p[0] = p[1]
    if p[0] not in Statemachine['States']:
        Statemachine['States'].append(p[0])
    if len(p) == 3:
        if p[1] not in Statemachine['State_Comments']:
            Statemachine['State_Comments'][p[1]] = []
        Statemachine['State_Comments'][p[1]].append(p[2])

def p_event_list(p):
    '''
    event_list : event_type
               | event_list comma event_type
    '''
    ReportP(p, "event_list")
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_event_type(p):
    '''
    event_type : id_or_str
               | id_or_str LPAREN id_list RPAREN
               | event_type text_string
    '''
    if len(p) == 2:
        p[0] = [p[1], []]
    elif len(p) == 5:
        p[0] = [p[1], p[3]]
    elif len(p) == 3:
        p[0] = p[1]
        if p[0][0] not in Statemachine['Event_Comments']:
            Statemachine['Event_Comments'][p[0][0]] = []
        Statemachine['Event_Comments'][p[0][0]].append(p[2])
    if p[0][0] not in Statemachine['Events']:
        Statemachine['Events'].append(p[0][0])

def p_action_list(p):
    '''
    action_list : action_type
                | action_list comma action_type
    '''
    ReportP(p, "action_list")
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_action_type(p):
    '''
    action_type : id_or_str
                | action_type text_string
    '''
    p[0] = p[1]
    if p[0] not in Statemachine['Actions']:
        Statemachine['Actions'].append(p[0])
    if len(p) == 3:
        if p[0] not in Statemachine['Action_Comments']:
            Statemachine['Action_Comments'][p[0]] = []
        Statemachine['Action_Comments'][p[0]].append(p[2])

def p_state_block(p):
    '''
    state_block : id_or_str LBRACE state_code_list RBRACE
                | id_or_str EQUALS LBRACE state_code_list RBRACE
                | id_or_str LPAREN state_list RPAREN LBRACE state_code_list RBRACE
    '''
    ReportP(p, "state_block")
    if len(p) == 5: # simple
        Statemachine['Blocks'][p[1]] = p[3]
        p[0] = [p[1]] + p[3]
    elif len(p) == 6: # it has the EQUALS in there
        Statemachine['Blocks'][p[1]] = p[4]
        p[0] = [p[1]] + p[4]
    elif len(p) == 8:
        Statemachine['Blocks'][p[1]] = p[6]
        Statemachine['Inherits'][p[1]] = p[3]

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
    state_code_1 : event_type CLASSIFIER action_type TRANSITION event_list
                 | event_type DISPATCH action_type CLASSIFIER event_list
    '''
    p[0] = [1, p[1], [p[3]], p[5]]

def p_state_code_2(p): # Action only
    '''
    state_code_2 : event_type DISPATCH action_list
    '''
    p[0] = [2, p[1], p[3], []]

def p_state_code_3(p): # Transition only
    '''
    state_code_3 : event_type TRANSITION state_list
    '''
    p[0] = [3, p[1], [], p[3]]

def p_state_code_4(p): # Action and Transition
    '''
    state_code_4 : event_type DISPATCH action_list TRANSITION state_list
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

def p_test_list(p):
    '''
    test_list : id_list
    '''
    p[0] = ['Test', p[1]]
    Statemachine['Tests'].append(p[1])

#
# The CODE block
#
def p_code(p):
    '''
    code : code_type id_or_str LBRACE code_block RBRACE
         | code_type id_or_str EQUALS LBRACE code_block RBRACE
    '''
    if len(p) > 6: # it has the EQUALS in there
        Statemachine['Code'][p[2]] = {'name' : p[2], 'type' : p[1], 'text' : p[5]}
        p[0] = {'Code' : {'name' : p[2], 'type' : p[1], 'text' : p[5]}}
    else:
        Statemachine['Code'][p[2]] = {'name' : p[2], 'type' : p[1], 'text' : p[4]}
        p[0] = {'Code' : {'name' : p[2], 'type' : p[1], 'text' : p[4]}}

def p_code_type(p):
    '''
    code_type : id_or_str
    '''
    p[0] = p[1]

def p_code_block(p):
    '''
    code_block : empty
               | code_block c_code_block
               | code_block python_code_block
               | code_block tcl_code_block
    '''
    ReportP(p, "code_block")
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = p[1] + [p[2]]

def p_c_code_block(p):
    '''
    c_code_block : AT_C code_list AT_END
    '''
    ReportP(p, "tcl_code_block")
    p[0] = ['C', p[2]]

def p_python_code_block(p):
    '''
    python_code_block : AT_PYTHON code_list AT_END
    '''
    ReportP(p, "tcl_code_block")
    p[0] = ['PYTHON', p[2]]

def p_tcl_code_block(p):
    '''
    tcl_code_block : AT_TCL code_list AT_END
    '''
    ReportP(p, "tcl_code_block")
    p[0] = ['TCL', p[2]]

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

def p_comma(p):
    '''
    comma : empty
          | COMMA
    '''
    pass

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

def load_file(source_file):
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
    Statemachine['Outputs'] = []
    Statemachine['States'] = []
    Statemachine['State_Comments'] = {}
    Statemachine['Events'] = []
    Statemachine['Event_Comments'] = {}
    Statemachine['Actions'] = []
    Statemachine['Action_Comments'] = {}
    Statemachine['Inherits'] = {}
    Statemachine['Blocks'] = {}
    Statemachine['Tests'] = []
    Statemachine['Code'] = {}
    SourceData = load_file(source_file)
    if args.yaccdebug:
        yaccer.parse('\n'.join(SourceData), debug=True)
    else:
        yaccer.parse('\n'.join(SourceData))
    if Verbose:
        print "Statemachine:", Statemachine
        for idx, sm in enumerate(Statemachines):
            print "Statemachine[%d]:" % idx, sm
    generate_source(Statemachines[0], SourceData, source_file)

def generate_source(the_fsm, SourceData, source_file):
    from xml.sax.saxutils import escape
    dest_file = os.path.join(os.path.dirname(source_file),\
                             the_fsm.name + ".fsm")
    the_fsm.dest_file = dest_file
    basename = os.path.basename(dest_file)

    #
    # Generate the SQL
    #
    fsm_sql = statemachine.StateMachine_SQL(the_fsm)
    fsm_sql.Generate()

    #
    # Generate the Reformatted State Machine text
    #
    fsm_text = statemachine.StateMachine_Text(the_fsm)
    txt_text = fsm_text.TextStateMachine()
    # print txt_text
    with open('%s.txt' % dest_file, 'w') as fdo:
        fdo.write('\n'.join(txt_text))

    #
    # Generate the UML
    #
    fsm_uml = statemachine.StateMachine_UML(the_fsm)
    with open("%s.uml" % dest_file, "w") as fdo:
        fdo.write('\n'.join(fsm_uml.Generate()))
    uml_cmd = "plantuml %s.uml" % dest_file
    print uml_cmd
    os.system(uml_cmd)

    #
    # Generate the Graphviz
    #
    fsm_html = statemachine.StateMachine_HTML(the_fsm)
    txt_dot = fsm_html.DotStateMachine3()
    with open("%s.dot" % dest_file, "w") as fdo:
        fdo.write('\n'.join(txt_dot))
    dot_cmd = "%s -Tsvg -o %s.svg %s.dot" % (args.dot, dest_file, dest_file)
    print dot_cmd
    os.system(dot_cmd)

    #
    # Generate the HTML
    #
    TABLE_START = '<TABLE BORDER=0 ALIGN="center">\n'
    TABLE_END = '</TABLE>\n'
    HDR_FMT = '<P style="page-break-before: always" ALIGN="center">%s</P>\n'

    text = open("%s.html" % dest_file, "w")
    text.write('<HTML>\n')
    text.write('<TITLE>Finite State Machine %s</TITLE>\n' % dest_file)

    text.write('<P ALIGN="center">%s</P>\n' % 'Source Code')

    text.write(TABLE_START)
    text.write('<TR><TD ALIGN="left">\n')
    text.write('<TABLE BORDER=1 ALIGN="center">\n')
    text.write('<TR><TH ALIGN="center">What you wrote</TH><TH ALIGN="center">What I saw</TH></TR>\n')
    text.write('<TR><TD ALIGN="left" VALIGN="top">\n')
    text.write('<PRE>\n' + '\n'.join(SourceData) + '\n</PRE>\n')
    text.write('</TD><TD ALIGN="left">\n')
    # Insert the Reformatted State Machine text
    text.write('<PRE>\n' + '\n'.join(txt_text) + '\n</PRE>\n')
    text.write('</TD></TR></TABLE>\n')
    text.write('</TD></TR>\n')

    text.write(TABLE_END + HDR_FMT % 'State Diagram' + TABLE_START)

    text.write('<TR><TD ALIGN="center">\n')
    text.write('<img src="%s.svg" alt="%s.svg"/>\n' % (basename, basename))
    text.write('</TD></TR>\n')
    text.write(TABLE_END + HDR_FMT % 'State Diagram' + TABLE_START)
    text.write('<TR><TD ALIGN="center">\n')
    text.write('<img src="%s.png" alt="%s.png"/>\n' % (basename, basename))
    text.write('</TD></TR>\n')

    text.write(TABLE_END + HDR_FMT % 'State Table 1' + TABLE_START)

    text.write('<TR><TD ALIGN="center">\n')
    txt = fsm_html.StateTable1()
    text.write('\n'.join(txt))
    text.write('</TD></TR>\n')

    text.write(TABLE_END + HDR_FMT % 'State Table 2' + TABLE_START)

    text.write('<TR><TD ALIGN="center">\n')
    txt = fsm_html.StateTable2()
    text.write('\n'.join(txt))
    text.write('</TD></TR>\n')

    text.write(TABLE_END + HDR_FMT % 'State Table 3' + TABLE_START)

    text.write('<TR><TD ALIGN="center">\n')
    txt = fsm_html.StateTable3()
    text.write('\n'.join(txt))
    text.write('</TD></TR>\n')

    text.write('</TABLE>\n')
    text.write('</HTML>\n')
    text.close()
    pdf_cmd = 'wkhtmltopdf -T 10mm -B 10mm %s.html %s.pdf' % (dest_file, dest_file)
    print pdf_cmd
    #os.system(pdf_cmd)

    #
    # Generate the TCL
    #
    if len(the_fsm.outputs) == 0 or 'TCL' in the_fsm.outputs:
        fsm_tcl = statemachine.StateMachine_TCL(the_fsm)
        txt_tcl = fsm_tcl.Generate_TCL()
        txt_tcl.insert(0, '# Generated by program')
        with open('%s.tcl' % dest_file, 'w') as fdo:
            fdo.write('\n'.join(txt_tcl))
    #
    # Generate the PYTHON
    #
    if len(the_fsm.outputs) == 0 or 'PYTHON' in the_fsm.outputs:
        fsm_python = statemachine.StateMachine_Python(the_fsm)
        txt_python = fsm_python.Generate_Python()
        txt_python.insert(0, '# Generated by program')
        with open('%s.py' % dest_file, 'w') as fdo:
            fdo.write('\n'.join(txt_python))
    #
    # Generate the GCC
    #
    if False:
        fsm_gcc = StateMachine_GCC2(the_fsm)
        hdr_gcc, txt_gcc = fsm_gcc.Generate_C()
        hdr_gcc.insert(0, '/* Generated by program */')
        txt_gcc.insert(0, '#include "%s.old.h"' % basename)
        txt_gcc.insert(0, '/* Generated by program */')
        with open('%s.old.h' % dest_file, 'w') as fdo:
            fdo.write('\n'.join(hdr_gcc))
            fdo.write('\n')
        with open('%s.old.c' % dest_file, 'w') as fdo:
            fdo.write('\n'.join(txt_gcc))
            fdo.write('\n')
        # Skeleton implementation file
        fsm_gcc.Absorb_Skel('%s.skel.old.c' % dest_file)
        hdr_skl, txt_skl = fsm_gcc.Generate_Skel()
        if len(hdr_skl) > 0:
            hdr_skl.insert(0, '/* Generated by program */')
            with open('%s.skel.old.h' % dest_file, 'w') as fdo:
                fdo.write('\n'.join(hdr_skl))
                fdo.write('\n')
            txt_skl.insert(0, '#include "%s.skel.h"' % dest_file)
        txt_skl.insert(0, '/* Generated by program */')
        with open('%s.skel.old.c' % dest_file, 'w') as fdo:
            fdo.write('\n'.join(txt_skl))
            fdo.write('\n')

    #
    # Generate GCC3
    #
    elif 'GCC' in the_fsm.outputs:
        fsm_sql2 = statemachine.StateMachine_SQL(fsm_sql.dest_file + ".sqlite")
        fsm_gcc3 = StateMachine_GCC3(fsm_sql2)
        hdr = fsm_gcc3.gen_hdr()
        with open('%s.h' % dest_file, 'w') as fdo:
            fdo.write('/* Generated by program */\n')
            fdo.write('\n'.join(hdr) + '\n')
        bdy = fsm_gcc3.gen_bdy()
        with open('%s.c' % dest_file, 'w') as fdo:
            fdo.write('/* Generated by program */\n')
            if True:
                fdo.write('\n'.join(hdr) + '\n')
            else:
                fdo.write('#include "%s.h"\n' % (fsm_gcc3.name + '.fsm'))
            fdo.write('\n'.join(bdy) + '\n')
        fsm_gcc3.Absorb_Skel('%s.skel.c' % dest_file)
        skl = fsm_gcc3.gen_skl()
        with open('%s.skel.c' % dest_file, 'w') as fdo:
            fdo.write('/* Generated by program */\n')
            fdo.write('#include "%s.h"\n' % (fsm_gcc3.name + '.fsm'))
            fdo.write('\n'.join(skl))
            fdo.write('\n')
        gcc_cmd = 'gcc -DUNIT_TEST %s.c' % (dest_file)
        print gcc_cmd

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
