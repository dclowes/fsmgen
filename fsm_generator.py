#!/usr/bin/env python3
"""
This program compiles a domain-specific state machine
language into a YAML structure. It then uses Jinja2
templates to generate documentation and code.

Author: Douglas Clowes (douglas.clowes@ansto.gov.au) Aug 2015
"""
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
import re
import sys
import argparse
import json
import yaml
import jinja2
import ply.lex as lex
import ply.yacc as yacc

ACTIONS = 'actions'
CODE = 'Code'
DEST = 'dest_file'
COMMENTS = 'comment'
EVENTS = 'events'
FLAGS = 'flags'
FILENAME = 'filename'
INITIAL = 'initial'
NAME = 'statemachine'
OUTPUTS = 'outputs'
STATES = 'states'
TESTS = 'tests'
TRANSACTIONS = 'transactions'

Statemachine = None
lexer = None
yaccer = None
Verbose = None
args = None

states = (
    ('code', 'exclusive'),
    )

def PrintParseError(message):
    print(message)
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
        print(locn)
        if p:
            print(repr(p))
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
    'AT_CODE',
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

def t_AT_CODE(t):
    r'@(CODE=)?[A-Za-z0-9_]+'
    if t.value.startswith('@CODE='):
        lang = t.value[6:].upper()
    else:
        lang = t.value[1:].upper()
    if lang in ['GCC', 'C']:
        t.type = 'AT_CODE'
        t.value = lang
    elif lang in ['PYTHON']:
        t.type = 'AT_PYTHON'
        t.value = 'PYTHON'
    elif lang in ['TCL']:
        t.type = 'AT_TCL'
        t.value = 'TCL'
    else:
        t.type = 'AT_CODE'
        t.value = lang
    t.lexer.begin('code')
    return t

def t_code_AT_END(t):
    r'[ \t]*@END'
    if Verbose:
        print('AT_END')
    t.lexer.begin('INITIAL')
    t.value = "@END"
    return t


t_code_ignore = ""

def t_code_CODE_STRING(t):
    r'.+'
    if t.value[0] == '@':
        t.value = t.value[1:]
    if Verbose:
        print('CODE:'+ t.value)
    return t

def t_code_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_code_error(t):
    message = "Illegal code character '%s'" % t.value[0]
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
    fsm : STATEMACHINE fsm_head fsm_block
    '''
    p[0] = [{'Statemachine' : {p[2] : p[3]}}]
    if Verbose:
        print("Statemachine:"+ p[0])
    Statemachine[NAME] = p[2]

def p_fsm_head(p):
    '''
    fsm_head : id_or_str
             | fsm_head text_string
    '''
    p[0] = p[1]
    if len(p) > 2:
        Statemachine[COMMENTS].append(p[2])

def p_fsm_block(p):
    '''
    fsm_block : equal LBRACE fsm_statement_list RBRACE
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
        if outp.upper() not in Statemachine[OUTPUTS]:
            Statemachine[OUTPUTS].append(outp.upper())
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
               | id_or_str LPAREN flag_list RPAREN
               | state_type text_string
    '''
    p[0] = p[1]
    if p[0] not in Statemachine[STATES]:
        Statemachine[STATES][p[0]] = {}
    if len(p) == 5:
        # with flags
        if FLAGS not in Statemachine[STATES][p[0]]:
            Statemachine[STATES][p[0]][FLAGS] = []
        Statemachine[STATES][p[0]][FLAGS] += p[3]
    if len(p) == 3:
        # with comment
        if COMMENTS not in Statemachine[STATES][p[0]]:
            Statemachine[STATES][p[0]][COMMENTS] = []
        Statemachine[STATES][p[0]][COMMENTS] += [p[2]]

def p_flag_list(p):
    '''
    flag_list : id_or_str
               | flag_list comma id_or_str
    '''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

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
    p[0] = p[1]
    if p[0] not in Statemachine[EVENTS]:
        Statemachine[EVENTS][p[0]] = {}
    if len(p) == 5:
        pass # TODO list
    if len(p) == 3:
        if COMMENTS not in Statemachine[EVENTS][p[0]]:
            Statemachine[EVENTS][p[0]][COMMENTS] = []
        Statemachine[EVENTS][p[0]][COMMENTS] += [p[2]]

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
                | id_or_str LPAREN event_list RPAREN
                | action_type text_string
    '''
    p[0] = p[1]
    if p[0] not in Statemachine[ACTIONS]:
        Statemachine[ACTIONS][p[0]] = {}
    if len(p) == 3:
        # with comment
        if COMMENTS not in Statemachine[ACTIONS][p[0]]:
            Statemachine[ACTIONS][p[0]][COMMENTS] = []
        Statemachine[ACTIONS][p[0]][COMMENTS] += [p[2]]
    if len(p) == 5:
        # with events
        if EVENTS not in Statemachine[ACTIONS][p[0]]:
            Statemachine[ACTIONS][p[0]][EVENTS] = []
        Statemachine[ACTIONS][p[0]][EVENTS] += [p[3]]


def p_state_block(p):
    '''
    state_block : id_or_str LBRACE state_code_list RBRACE
                | id_or_str equal LBRACE state_code_list RBRACE
                | id_or_str LPAREN state_list RPAREN LBRACE state_code_list RBRACE
    '''
    ReportP(p, "state_block")
    seq = []
    state = p[1]
    if state not in Statemachine[STATES]:
        Statemachine[STATES][state] = {}
    if state not in Statemachine[TRANSACTIONS]:
        Statemachine[TRANSACTIONS][state] = {}
    if len(p) == 5:
        # simple
        seq = p[3]
    if len(p) == 6:
        # simple equals
        seq = p[4]
    elif len(p) == 8:
        # Inheritance
        seq = p[6]
        if 'Inherits' not in Statemachine[STATES][state]:
            Statemachine[STATES][state]['Inherits'] = []
        Statemachine[STATES][state]['Inherits'] += p[3]

    for item in seq:
        Statemachine[TRANSACTIONS][state][item[1]] = {
            'actions': item[2],
            'events': item[3],
            'states': item[4]
        }

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
               | state_code_5
    '''
    p[0] = p[1]

def p_state_code_1(p): # Classifier
    '''
    state_code_1 : event_type DISPATCH action_list CLASSIFIER event_list
    '''
    p[0] = [1, p[1], p[3], p[5], []]

def p_state_code_2(p): # Action only
    '''
    state_code_2 : event_type DISPATCH action_list
    '''
    p[0] = [2, p[1], p[3], [], []]

def p_state_code_3(p): # Transition only
    '''
    state_code_3 : event_type TRANSITION state_list
    '''
    p[0] = [3, p[1], [], [], p[3]]

def p_state_code_4(p): # Action and Transition
    '''
    state_code_4 : event_type DISPATCH action_list TRANSITION state_list
    '''
    ReportP(p, "state_code")
    p[0] = [4, p[1], p[3], [], p[5]]

def p_state_code_5(p): # Everything
    '''
    state_code_5 : event_type DISPATCH action_list CLASSIFIER event_list TRANSITION state_list
    '''
    p[0] = [5, p[1], p[3], p[5], p[7]]

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
    Statemachine[TESTS].append(p[1])

#
# The CODE block
#
def p_code(p):
    '''
    code : code_type id_or_str equal LBRACE code_block RBRACE
    '''
    if len(p) > 6: # it has the EQUALS in there
        Statemachine[CODE][p[2]] = {'name' : p[2], 'type' : p[1], 'text' : p[5]}
        p[0] = {CODE : {'name' : p[2], 'type' : p[1], 'text' : p[5]}}
    else:
        Statemachine[CODE][p[2]] = {'name' : p[2], 'type' : p[1], 'text' : p[4]}
        p[0] = {CODE : {'name' : p[2], 'type' : p[1], 'text' : p[4]}}

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
    c_code_block : AT_CODE code_list AT_END
    '''
    ReportP(p, "c_code_block")
    p[0] = [p[1], p[2]]

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

def p_equal(p):
    '''
    equal : empty
          | EQUALS
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
    Statemachine[FILENAME] = source_file
    Statemachine[COMMENTS] = []
    Statemachine[OUTPUTS] = []
    Statemachine[INITIAL] = []
    Statemachine[STATES] = {}
    Statemachine[EVENTS] = {}
    Statemachine[ACTIONS] = {}
    Statemachine[TRANSACTIONS] = {}
    Statemachine[TESTS] = []
    Statemachine[CODE] = {}
    SourceData = load_file(source_file)
    if args.yaccdebug:
        yaccer.parse('\n'.join(SourceData), debug=True)
    else:
        yaccer.parse('\n'.join(SourceData))

    #
    if not "Default" in Statemachine[EVENTS]:
        Statemachine[EVENTS]["Default"] = {"comment": ["State Default"]}
    if not "Entry" in Statemachine[EVENTS]:
        Statemachine[EVENTS]["Entry"] = {"comment": ["State Entry"]}
    if not "Exit" in Statemachine[EVENTS]:
        Statemachine[EVENTS]["Exit"] = {"comment": ["State Exit"]}
    for state in sorted(Statemachine[STATES]):
        if FLAGS in Statemachine[STATES][state]:
            if "INITIAL" in Statemachine[STATES][state][FLAGS]:
                if not state in Statemachine[INITIAL]:
                    Statemachine[INITIAL].append(state)

    if Verbose:
        print(Statemachine)
        print("Statemachine:")
        for key in sorted(Statemachine):
            if key in [ACTIONS, EVENTS, STATES]:
                print("  %s:" % key)
                for item in sorted(Statemachine[key]):
                    print("    %s: %s" % (item, Statemachine[key][item]))
            elif key in [CODE]:
                #print(Statemachine[key])
                for item in sorted(Statemachine[key]):
                    print("    %s.%s:" % (key, item))
                    for iitem in sorted(Statemachine[key][item]):
                        print("      %s" % (Statemachine[key][item][iitem]))
            elif key in [TRANSACTIONS]:
                #print(Statemachine[key])
                print("  %s:" % key)
                for state in sorted(Statemachine[key]):
                    print("    State.%s:" % state)
                    for event in Statemachine[key][state]:
                        print("      Event:%s = %s" % (event, repr(Statemachine[key][state][event])))
            else:
                print("  %s: %s"%(key, Statemachine[key]))
    generate_source(Statemachine, SourceData, source_file)

def generate_source(the_fsm, SourceData, source_file):
    default_outputs = ['FSM', 'UML']
    optional_outputs = ['GCC', 'PYTHON', 'TCL']
    dest_file = os.path.join(os.path.dirname(source_file),\
                             the_fsm[NAME] + ".fsm")
    the_fsm[DEST] = dest_file
    basename = os.path.basename(dest_file)
    if Verbose:
        print("Basename:%s" % basename)
        print("Destname:%s" % dest_file)

    #
    # Generate the YML and JSON
    #
    if Verbose:
        print(yaml.dump(the_fsm))
    with open("%s.yml" % dest_file, "w") as fdo:
        fdo.write(yaml.dump(the_fsm, indent=4))
    with open("%s.json" % dest_file, "w") as fdo:
        fdo.write(json.dumps(the_fsm, indent=4))

    #
    # Generate the SQL
    #

    #
    # Generate the Reformatted State Machine text
    #
    Load(the_fsm, 'FSM')

    #
    # Generate the UML
    #
    Load(the_fsm, 'UML')

    #
    # Generate the Graphviz
    #

    #
    # Generate the HTML
    #
#   Load(the_fsm, 'HTML')

    #
    # Generate the TCL
    #
    if 'TCL' in the_fsm[OUTPUTS]:
        Load(the_fsm, 'TCL')

    #
    # Generate the PYTHON
    #
    if 'GCC' in the_fsm[OUTPUTS]:
        Load(the_fsm, 'PYTHON')

    #
    # Generate GCC3
    #
    if 'GCC' in the_fsm[OUTPUTS]:
        Load(the_fsm, 'GCC')

    #
    # Generate the requested outputs
    #
    for item in the_fsm[OUTPUTS]:
        if item in default_outputs:
            continue
        if item in optional_outputs:
            continue
        Load(the_fsm, item)

def Load(my_vars, template):
    template_base = os.path.realpath(
        os.path.abspath(
            os.path.dirname(sys.argv[0])
        )
    )
    templateLoader = jinja2.FileSystemLoader(searchpath=template_base)
    templateEnv = jinja2.Environment(loader=templateLoader)

    try:
        template_name = "config_%s.yml" % template.lower()
        template = templateEnv.get_template(template_name)
    except jinja2.exceptions.TemplateNotFound:
        print("Template %s not found" % template_name)
        return

    configText = template.render(my_vars)
    config = yaml.load(configText)
    if Verbose:
        print(config)
    my_vars['config'] = config
    #print(yaml.dump(my_vars, indent=4))
    for file in config['template']['files']:
        dest_file = file['output']
        my_vars['code_blocks'] = {}
        if 'preload' in file:
            my_vars['code_blocks'] = Preload(file['preload'])
            #print(yaml.dump(my_vars['code_blocks'], indent=4))
        template = templateEnv.get_template(file['input'])
        outputText = template.render(my_vars)
        with open(dest_file, 'w') as fdo:
            fdo.write(outputText)
        if 'echo' in file:
            for item in file['echo']:
                print(item)
        if 'post' in file:
            for item in file['post']:
                print(item)
                os.system(item)



def Preload(filename):
    '''
    This method reads an existing skeleton file and loads code_blocks
    with the code between custom code markers in the skeleton file.

    This code can later be emitted in place of the boilerplate to preserve
    custom code development if the state machine is later regenerated.
    '''
    target = None
    code_blocks = {}
    try:
        with open(filename, "r") as fd:
            lines = fd.read().splitlines()
    except IOError:
        lines = []
    for line in lines:
        if " BEGIN CUSTOM: " in line:
            target = re.sub(r'.*BEGIN CUSTOM: ([ _a-zA-Z0-9]+) +[^ _a-zA-Z0-9].*', r'\1', line)
            code_blocks[target] = []
            continue
        if " END CUSTOM: " in line:
            if not code_blocks[target]:
                del code_blocks[target]
            target = None
            continue
        if target:
            code_blocks[target].append(line)
#   for target in code_blocks:
#       print "Target:", target, len(code_blocks[target])
    return code_blocks

def main():
    global lexer, yaccer
    global Verbose
    global args

    graphviz = ['dot', 'circo', 'neato', 'fdp', 'sfdp', 'twopi', 'osage', 'patchwork']
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dot", default="dot", choices=graphviz, help="graphviz layout tool to use")
    parser.add_argument("-l", "--lexdebug", help="lex debug output",
                        action="store_true")
    parser.add_argument("-y", "--yaccdebug", help="yacc debug output",
                        action="store_true")
    parser.add_argument("-v", "--verbose", help="verbose output",
                        action="store_true")
    parser.add_argument("driver_source", help="source file", nargs="*")
    args = parser.parse_args()
    if args.verbose:
        Verbose = True
        print(args)
    else:
        Verbose = False
    source_files = args.driver_source    #
    if source_files:
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
