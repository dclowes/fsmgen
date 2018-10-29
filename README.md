# State Machine Generator
This program takes a state machine description file and produces source code
and documentation to give effect to the state machine.

# The Input File
The definition of the state machine is in
a bespoke domain specific language
intended to make the description
easy to understand and easy to code.
It is free format and most syntactical sugar is optional.

# The Output File
The primary output file is a YAML description of the state machine. This is basically just a reordering of the input information.

# Downstream Processing
The secondary output is a set of files produced by
Jinja2 template processing against the YAML data.
This can happen within the program or completely independently.
You could write the state machine description directly in YAML
and process the same Jinja2 templates to produce the same outputs.

Internal template processing is controlled by template description files.
These are YAML files that describe the inputs, outputs and options
for the processing of the Jinja2 template and the disposition of the output.

There are a number of template files for the production of documentation.

## UML Diagram Generator
There is a template to convert the YAML description of the state machine
into a "*plantUML*" input file for a state machine diagram.

## HTML Tables Generator
There are a number of templates to generate several HTML tables for inclusion into a web page.

## TCL Code Generator
There is a template to produce an executable TCL state machine.

## Python Code Generator
There is a template to produce an executable Pyhon state machine.

## C Code Generator
There is a template to produce an executable C state machine.

## Reformatted Source Generator
There is a template to produce a 'reformatted' version of the original input.
The output is indented and sorted.

## Contributors

* [Australian Centre for Neutron Scattering](https://www.ansto.gov.au/research/facilities/australian-centre-for-neutron-scattering)

## Acknowledgements

Sponsored by the [Australian Nuclear Science and Technology Organisation (ANSTO)](http://www.ansto.gov.au "ANSTO").
