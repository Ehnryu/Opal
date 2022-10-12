"""
Interpreter
-----------

AST-walking interpreter.
"""

from __future__ import print_function
import monochrome.converters as monochromec
import time
import os
from monochrome import modules
from monochrome.globalvars import gbl as getglobals
import operator
from collections import namedtuple
from monochrome import ast
from monochrome.lexer import Lexer, TokenStream
from monochrome.parser import Parser
from monochrome.errors import monochromeSyntaxError, report_syntax_error
from monochrome.utils import print_ast, print_tokens, print_env


BuiltinFunction = namedtuple('BuiltinFunction', ['params', 'body'])


class Break(Exception):
    pass


class Continue(Exception):
    pass


class Return(Exception):
    def __init__(self, value):
        self.value = value


class Environment(object):

    def __init__(self, parent=None, args=None):
        self._parent = parent
        self._values = {}
        if args is not None:
            self._from_dict(args)

    def _from_dict(self, args):
        for key, value in args.items():
            self.set(key, value)

    def set(self, key, val):
        self._values[key] = val

    def get(self, key,op=None):
        val = self._values.get(key, op)
        if val is op and self._parent is not None:
            return self._parent.get(key)
        else:
            return val

    def asdict(self):
        return self._values

    def __repr__(self):
        return 'Environment({})'.format(str(self._values))


def eval_binary_operator(node, env):
    simple_operations = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '%': operator.mod,
        '>': operator.gt,
        '>=': operator.ge,
        '<': operator.lt,
        '<=': operator.le,
        '==': operator.eq,
        '!=': operator.ne,
        '..': range,
        '...': lambda start, end: range(start, end + 1),
    }
    lazy_operations = {
        '&&': lambda lnode, lenv: bool(eval_expression(lnode.left, lenv)) and bool(eval_expression(lnode.right, lenv)),
        '||': lambda lnode, lenv: bool(eval_expression(lnode.left, lenv)) or bool(eval_expression(lnode.right, lenv)),
    }
    if node.operator in simple_operations:
        return simple_operations[node.operator](eval_expression(node.left, env), eval_expression(node.right, env))
    elif node.operator in lazy_operations:
        return lazy_operations[node.operator](node, env)
    else:
        raise Exception('Invalid operator {}'.format(node.operator))


def eval_unary_operator(node, env):
    operations = {
        '-': operator.neg,
        '!': operator.not_,
    }
    return operations[node.operator](eval_expression(node.right, env))


def eval_assignment(node, env):
    print("ASSIGN")
    if isinstance(node.left, ast.SubscriptOperator):

        return eval_setitem(node, env)
    else:
        return env.set(node.left.value, eval_expression(node.right, env))


def eval_condition(node, env):
    if eval_expression(node.test, env):
        return eval_statements(node.if_body, env)

    for cond in node.elifs:
        if eval_expression(cond.test, env):
            return eval_statements(cond.body, env)

    if node.else_body is not None:
        return eval_statements(node.else_body, env)


def eval_match(node, env):
    test = eval_expression(node.test, env)
    for pattern in node.patterns:
        if eval_expression(pattern.pattern, env) == test:
            return eval_statements(pattern.body, env)
    if node.else_body is not None:
        return eval_statements(node.else_body, env)


def eval_while_loop(node, env):
    while eval_expression(node.test, env):
        try:
            eval_statements(node.body, env)
        except Break:
            break
        except Continue:
            pass


def eval_for_loop(node, env):
    var_name = node.var_name
    collection = eval_expression(node.collection, env)
    for val in collection:
        env.set(var_name, val)
        try:
            eval_statements(node.body, env)
        except Break:
            break
        except Continue:
            pass


def eval_function_declaration(node, env):
    return env.set(node.name, node)


def eval_call(node, env,f=None,args={}):
    import monochrome
    if args != {}:
        pargs = args
    import sys


    function = f
    if f == None:
        function = eval_expression(node.left, env)
    if function == None:
        function = node.left
    import sys
    if "-t" in sys.argv or "--trace" in sys.argv:
        print(f"+|Call -> {type(function)}({function})")
    import random
    import os
    try:
        n_expected_args = len(function.params)
        n_actual_args = len(node.arguments)
    #print(n_expected_args)
        if n_expected_args != n_actual_args:
            raise TypeError('Expected {} arguments, got {}'.format(n_expected_args, n_actual_args))
        args = dict(zip(function.params, [eval_expression(node, env) for node in node.arguments]))
    except:
        try:
            if args == {}:
                args = dict(zip([eval_expression(node, env) for node in node.arguments]))
            else:
                args = dict(zip(function.params,args))

        except:
            try:
                args = dict(zip(function.params,args))
            except:
                try:
                    args = node.arguments
                except:
                    args = pargs



    if isinstance(function, BuiltinFunction):
        k = args
        k["env"] = env
        return function.body(args, env)
    elif isinstance(function,modules.BuiltinFunction):
        k = args

        if env in function.params:
            k["env"] = env
        tr = ""
        for i in k:

            k[i] = monochrome.converters.convert(i,env,to="py")

        try:
            return function.body(**k)

        except TypeError:
            args = [eval_expression(node, env) for node in node.arguments]
            a = []
            for i in args:
                a.append(monochrome.converters.convert(i,env,to="py"))
            return function.body(*a)

        return function.body(**k)
    elif type(function) == type(eval_call):
        a = []
        for i in args:
            a.append(monochrome.converters.convert(i,env))




        return function(*a)

    elif type(function) == type(os.getcwd):
        a = []
        for i in args:
            a.append(monochrome.converters.convert(i,env))



        return function(*a)



    elif type(function) == type(Return):


        return function(*args)
    elif type(function) == type(random.randint):
        a = []
        for i in args:
            a.append(monochrome.converters.convert(i,env,to="py"))



        return function(*a)
    elif type(function) != ast.Function:
        a = []
        for i in args:
            a.append(monochrome.converters.convert(i,env,to="py"))



        return function(*a)
    else:

        call_env = Environment(env, args)
        try:
            return eval_statements(function.body, call_env)
        except Return as ret:
            return ret.value


def eval_identifier(node, env):
    print("IDENFITY")
    name = node.value
    import monochrome


    val = env.get(name)

    if val is None:

        raise NameError('Name "{}" is not defined'.format(name))
    #print("NODER:")
    #print(node)

    return val


def eval_getitem(node, env):
    collection = eval_expression(node.left, env)
    key = eval_expression(node.key, env)
    return collection[key]


def eval_setitem(node, env):
    collection = eval_expression(node.left.left, env)
    key = eval_expression(node.left.key, env)
    collection[key] = eval_expression(node.right, env)


def eval_array(node, env):
    return [eval_expression(item, env) for item in node.items]


def eval_dict(node, env):
    print("DICTT")
    d = {eval_expression(key, env): eval_expression(value, env) for key, value in node.items}


    return d


def eval_return(node, env):
    return eval_expression(node.value, env) if node.value is not None else None
def get():
    import monochrome.converters as monochromec
    return monochromec
monochromec = get()
converters = monochromec.py
evaluators = {
    ast.Number: lambda node, env: node.value,
    ast.String: lambda node, env: node.value,
    ast.Array: eval_array,
    ast.Dictionary: eval_dict,
    ast.Identifier: eval_identifier,
    ast.BinaryOperator: eval_binary_operator,
    ast.UnaryOperator: eval_unary_operator,
    ast.SubscriptOperator: eval_getitem,
    ast.Assignment: eval_assignment,
    ast.Condition: eval_condition,
    ast.Match: eval_match,
    ast.WhileLoop: eval_while_loop,
    ast.ForLoop: eval_for_loop,
    ast.Function: eval_function_declaration,
    ast.Call: eval_call,
    ast.Return: eval_return,
}
nodes = []

def eval_node(node, env):

    import sys
    nodes.append(node)
    print("--")

    print(nodes[-1])
    print("--")


    tp = type(node)
    if "-v" in sys.argv:
        print(node)
        print(tp)

    if tp in evaluators:
        return evaluators[tp](node, env)
    elif tp in converters:
        return converters[tp](node,env)
    elif tp == dict:
        return node
    else:
        raise Exception('Unknown node {} {}'.format(tp.__name__, node))


def eval_expression(node, env):
    return eval_node(node, env)


def eval_statement(node, env):
    return eval_node(node, env)


def eval_statements(statements, env):
    ret = None


    for statement in statements:
        if isinstance(statement, ast.Break):
            raise Break(ret)
        elif isinstance(statement, ast.Continue):
            raise Continue(ret)
        ret = eval_statement(statement, env)
        if isinstance(statement, ast.Return):
            raise Return(ret)
    return ret


def add_builtins(env):
    from monochrome.modules import loadfunc,callpy,getfrom

    builtins = {
        'print': (['value'], lambda args, e: print(args['value'])),
        'len': (['iter'], lambda args, e: len(args['iter'])),
        'slice': (['iter', 'start', 'stop'], lambda args, e: list(args['iter'][args['start']:args['stop']])),
        'str': (['in'], lambda args, e: str(args['in'])),
        'int': (['in'], lambda args, e: int(args['in'])),
        'list': (['obj'], lambda args, e: list(args['obj'])),
        'dict': (['obj'], lambda args, e: dict(args['obj'])),
        'type': (['object'], lambda args, e: type(args['object'])),
        'globals': (["global"], lambda args, e: getglobals(args["global"])),

        'require': (['pkg'], lambda args, e: __import__(args['pkg'],globals(), locals(),[])),
        'getattr': (['object',"from"], lambda args, e: getattr(args['object'],args["from"])),
        'require_from': (['object',"from"], lambda args, e: loadfunc(args)),
        'callpyfunc': (['obj',"args"], lambda args, e: callpy(args["obj"],args["args"])),
        'frequire': (['object',"from","args"], lambda args, e: getfrom(args)),
        'pause': (['seconds'], lambda args, e: time.sleep(args['seconds'])),
        'input': (["prompt"], lambda args, e: input(args["prompt"])),
        'prompt': (["prompt"], lambda args, e: input(args["prompt"])),
        'exit': ([], lambda args, e: exit())

    }


    for key in builtins:
        import sys
        params = builtins[key][0]
        func = builtins[key][1]

        if "-l" in sys.argv or "--load" in sys.argv:
            print(f"set {key} -> {func}({params})")

        env.set(key, BuiltinFunction(params, func))


def create_global_env():
    env = Environment()
    add_builtins(env)
    from monochrome.modules import add_mods
    add_mods(env)
    from monochrome.globalvars import setglobals
    setglobals(env)
    return env


def evaluate_env(s, env, verbose=False,file=None):

    print("EXER")
    import monochrome
    env = monochrome.env[str(monochrome.os)]
    import monochrome


    lexer = Lexer()
    try:
        tokens = lexer.tokenize(s)
    except monochromeSyntaxError as err:
        report_syntax_error(lexer, err)
        if verbose:
            raise
        else:
            return

    if verbose:
        print('Tokens')
        print_tokens(tokens)
        print()

    token_stream = TokenStream(tokens)



    try:
        program = Parser().parse(token_stream,file)
    except monochromeSyntaxError as err:
        report_syntax_error(lexer, err)
        if verbose:
            raise
        else:
            return

    if verbose:
        print('AST')
        print_ast(program.body)
        print()






    ret = eval_statements(program.body, env)




    if verbose:
        print('Environment')
        print_env(env)
        print()





    return ret
def envy(s, env, verbose=False,file=None):
    import monochrome
    if file == None:
        raise RuntimeError("FILE NEEDED :(")


    lexer = Lexer()
    try:
        tokens = lexer.tokenize(s)
    except monochromeSyntaxError as err:
        report_syntax_error(lexer, err)
        if verbose:
            raise
        else:
            return

    if verbose:
        print('Tokens')
        print_tokens(tokens)
        print()

    token_stream = TokenStream(tokens)



    try:
        program = Parser().parse(token_stream,file=file) # file
    except monochromeSyntaxError as err:
        report_syntax_error(lexer, err)
        if verbose:
            raise
        else:
            return

    if verbose:
        print('AST')
        print_ast(program.body)
        print()






    ret = eval_statements(program.body, env)




    if verbose:
        print('Environment')
        print_env(env)
        print()





    return monochrome.lib.objects.object(out=ret,env=env)


def evaluate(s,verbose=False,e=create_global_env()):
    return evaluate_env(s, e, verbose)
def eval(s, verbose=False):

    import copy
    from monochrome.lib import objects
    env = create_global_env()
    sen = s
    out = copy.deepcopy(evaluate_env)(s, env, verbose)
    return objects.object(env=env,inp=sen,out=out)
