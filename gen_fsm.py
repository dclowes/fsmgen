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

Statemachine = None
lexer = None
yaccer = None
Verbose = None
args = None

states = (
    ('tcl', 'exclusive'),
    )

def FormatEvent(event):
    if len(event) > 1:
        txt = "%s(%s)" % (event[0], ", ".join(event[1]))
    else:
        txt = "%s" % (event[0])
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
    txt += ['  node [shape=record];']
    txt += ['']
    if len(sm['Events']) > 0:
        print "Events:", ", ".join([FormatEvent(e) for e in sorted(sm['Events'])])
    if len(sm['States']) > 0:
        print "States:", ", ".join(sorted(sm['States']))
        for state in sorted(sm['States']):
            print "    %s" % state
            if state in sm['Blocks'] and len(sm['Blocks'][state]) > 0:
                label = ['<f0> %s' % state, '{']
                for idx, event in enumerate(sm['Blocks'][state]):
                    label += ['<f%d> %s' % (idx + 1, FormatEvent(event[0]))]
                label += ['}']
                txt += ['  %s[shape=record, label="%s"];' % (state, '|'.join(label))]
                for idx, event in enumerate(sm['Blocks'][state]):
                    print "        %s ->"  % FormatEvent(event[0]),
                    if len(event[1]) > 1:
                        print "%s" % ", ".join(event[1]),
                    else:
                        print "%s" % event[1][0],
                    if len(event) > 2:
                        if len(event[2]) > 1:
                            print "=> %s" % ", ".join(event[2]),
                        else:
                            print "=> %s" % event[2][0],
                        for e in event[2]:
                            txt += ['    %s:f%d -> %s:f0;' % (state, idx + 1, e)]
                    print
    txt += ['}']
    text = open("prog.dot", "w")
    text.write('\n'.join(txt))
    text.close()
    dot_cmd = "%s -Tsvg -o prog.svg prog.dot" % args.dot
    print dot_cmd
    os.system(dot_cmd)

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
        p[0] = [p[1]]

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
    state_code : event_type DISPATCH id_list
               | event_type DISPATCH id_list TRANSITION state_list
    '''
    ReportP(p, "state_code")
    if len(p) > 5:
        p[0] = [p[1], p[3], p[5]]
    elif len(p) > 2:
        p[0] = [p[1], p[3]]
    else:
        p[0] = []

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
    PrintStateMachine(Statemachine)

def main():
    global lexer, yaccer
    global Verbose
    global args
    import argparse

    graphviz = ['dot', 'circo', 'neato', 'fdp', 'sfdp', 'twopi', 'osage', 'patchwork']
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dot", default="sfdp", choices=graphviz, help="graphviz layout tool to use")
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
