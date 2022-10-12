from monochrome.ast import genblin,Array
from monochrome import ast,converters
def appender(l,v):

    l.append(v)
    return l
a = {'name': 'append', 'run': appender, 'args': ['l', 'v'], 'description': 'append item to a list'}
def remover(l,v):

    l.remove(v)
    return l
r = {'name': 'remove', 'run': remover, 'args': ['l', 'v'], 'description': 'remove item from a list'}
def inner(l,v):
    from monochrome import ast, converters

    if l in v:
        return True
    return False
i = {'name': 'lin', 'run': inner, 'args': ['l', 'v'], 'description': 'check if a value is in a list'}
export = [r,a,i]
