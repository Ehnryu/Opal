"""
Utils
-----

Utility functions.
"""
from typing import Iterable

def get_all_values(d):
    if isinstance(d, dict):
        for v in d.values():
            yield from get_all_values(v)
    elif isinstance(d, Iterable): # or list, set, ... only
        for v in d:
            yield from get_all_values(v)
    else:
        yield d 
import pprint

_pp = pprint.PrettyPrinter(indent=2)

def execute(c,s=True):


    import subprocess
    from monochrome import lib
    process = None
    try:
        bashCommand = c
        bc = bashCommand.split()
        nc = []
        for item in bc:
            item = item.replace("%20"," ")
            nc.append(item)
        process = subprocess.run(c,text=True,capture_output=True)

        #try:
        o = process.stdout

        if o == "" and process.stderr != "":
            o = process.stderr
        if s == False:
            print(o)


        if o != None:


            return lib.objects.object(output=o,text=o,command=c,silent=s,is_error=False,error=process.stderr,process=process,view=o)
    except Exception as e:

        if str(e).endswith("1.") == False:
            if s == False:

              return lib.objects.object(output="",text="",command=c,silent=s,is_error=True,error=e,process=process,view=e)
    return None
def _print_node(node, indent, indent_symbol):
    if isinstance(node, list):
        for child in node:
            for p in _print_node(child, indent, indent_symbol):
                yield p
    elif isinstance(node, int) or isinstance(node, float) or isinstance(node, str) or node is None:
        yield ' {}'.format(node)
    elif hasattr(node, '_fields'):
        yield '\n{}{}'.format(indent_symbol * indent, type(node).__name__)
        for field in node._fields:
            yield '\n{}{}:'.format(indent_symbol * (indent + 1), field, ':')
            for p in _print_node(getattr(node, field), indent + 2, indent_symbol):
                yield p
    else:
        yield '\nError! Unable to print {}'.format(node)


def print_ast(node, indent=0, indent_symbol=' ' * 4):
    print(''.join(_print_node(node, indent, indent_symbol)))


def print_tokens(tokens):
    _pp.pprint(tokens)


def print_env(env):
    _pp.pprint(env.asdict())
