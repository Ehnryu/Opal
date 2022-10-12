"""
Parser
------


Top-down recursive descent parser.
"""
import sys
from monochrome import ast
from monochrome.errors import monochromeSyntaxError
import inspect
import monochrome.exts



class ParserError(monochromeSyntaxError):

    def __init__(self, message, token):
        super(ParserError, self).__init__(message, token.line, token.column)


def enter_scope(parser, name):
    class State(object):
        def __enter__(self):
            parser.scope.append(name)

        def __exit__(self, exc_type, exc_val, exc_tb):
            parser.scope.pop()

    return State()


class Subparser(object):

    PRECEDENCE = {
        'call': 10,
        'subscript': 10,
        'object': 10,

        'unary': 9,

        '*': 7,
        '/': 7,
        '%': 7,

        '+': 6,
        '-': 6,

        '>': 5,
        '>=': 5,
        '<': 5,
        '<=': 5,

        '==': 4,
        '!=': 4,

        '&&': 3,

        '||': 2,

        '..': 1,
        '...': 1,
    }

    def get_subparser(self, token, subparsers, default=None):
        cls = subparsers.get(token.name, default)
        if cls is not None:
            return cls()


class PrefixSubparser(Subparser):

    def parse(self, parser, tokens):
        raise NotImplementedError()


class InfixSubparser(Subparser):

    def parse(self, parser, tokens, left):
        raise NotImplementedError()

    def get_precedence(self, token):
        raise NotImplementedError()


# number_expr: NUMBER
class NumberExpression(PrefixSubparser):

    def parse(self, parser, tokens):
        token = tokens.consume_expected('NUMBER')
        return ast.Number(token.value)


# str_expr: STRING
class StringExpression(PrefixSubparser):

    def parse(self, parser, tokens):
        token = tokens.consume_expected('STRING')
        return ast.String(token.value)


# name_expr: NAME
class NameExpression(PrefixSubparser):

    def parse(self, parser, tokens):
        token = tokens.consume_expected('NAME')
        return ast.Identifier(token.value)


# prefix_expr: OPERATOR expr
class UnaryOperatorExpression(PrefixSubparser):

    SUPPORTED_OPERATORS = ['-', '!']

    def parse(self, parser, tokens,file):
        #print("XX")
        token = tokens.consume_expected('OPERATOR')
        if token.value not in self.SUPPORTED_OPERATORS:
            raise ParserError('Unary operator {} is not supported'.format(token.value), token)
        right = Expression().parse(parser, tokens, self.get_precedence(token),file=file)
        if right is None:
            raise ParserError('Expected expression'.format(token.value), tokens.consume())
        return ast.UnaryOperator(token.value, right)

    def get_precedence(self, token):
        return self.PRECEDENCE['unary']


# group_expr: LPAREN expr RPAREN
class GroupExpression(PrefixSubparser):

    def parse(self, parser, tokens,file):
        tokens.consume_expected('LPAREN')
        right = Expression().parse(parser, tokens,file=file)
        tokens.consume_expected('RPAREN')
        return right


# array_expr: LBRACK list_of_expr? RBRACK
class ArrayExpression(PrefixSubparser):

    def parse(self, parser, tokens,file):
        tokens.consume_expected('LBRACK')
        items = ListOfExpressions().parse(parser, tokens,file)
        tokens.consume_expected('RBRACK')
        return ast.Array(items)


# dict_expr: LCBRACK (expr COLON expr COMMA)* RCBRACK
class DictionaryExpression(PrefixSubparser):

    def _parse_keyvals(self, parser, tokens,file):
        items = []
        while not tokens.is_end():
            key = Expression().parse(parser, tokens,file=file)
            if key is not None:
                tokens.consume_expected('COLON')
                value = Expression().parse(parser, tokens,file=file)
                if value is None:
                    raise ParserError('Dictionary value expected', tokens.consume())
                items.append((key, value))
            else:
                break
            if tokens.current().name == 'COMMA':
                tokens.consume_expected('COMMA')
            else:
                break
        return items

    def parse(self, parser, tokens,file):
        tokens.consume_expected('LCBRACK')
        items = self._parse_keyvals(parser, tokens,file)
        tokens.consume_expected('RCBRACK')
        return ast.Dictionary(items)


# infix_expr: expr OPERATOR expr
class BinaryOperatorExpression(InfixSubparser):

    def parse(self, parser, tokens, left,file):
        #print("YY")
        token = tokens.consume_expected('OPERATOR')

        if token.value + tokens.current().value == "+=":
            print("OPP")
        right = Expression().parse(parser, tokens, self.get_precedence(token),file=file)
        if right is None:
            raise ParserError('Expected expression'.format(token.value), tokens.consume())
        return ast.BinaryOperator(token.value, left, right)

    def get_precedence(self, token):
        return self.PRECEDENCE[token.value]


# call_expr: NAME LPAREN list_of_expr? RPAREN
class CallExpression(InfixSubparser):

    def parse(self, parser, tokens, left,file):
        if "-t" in sys.argv or "--trace" in sys.argv:
            print("-|CallExpression")
        tokens.consume_expected('LPAREN')
        arguments = ListOfExpressions().parse(parser, tokens,file)
        tokens.consume_expected('RPAREN')
        return ast.Call(left, arguments)

    def get_precedence(self, token):
        return self.PRECEDENCE['call']


# subscript_expr: NAME LBRACK expr RBRACK
class SubscriptOperatorExpression(InfixSubparser):

    def parse(self, parser, tokens, left,file):
        tokens.consume_expected('LBRACK')
        key = Expression().parse(parser, tokens,file=file)
        if key is None:
            raise ParserError('Subscript operator key is required', tokens.current())
        tokens.consume_expected('RBRACK')
        return ast.SubscriptOperator(left, key)

    def get_precedence(self, token):
        return self.PRECEDENCE['subscript']


# expr: number_expr | str_expr | name_expr | group_expr | array_expr | dict_expr | prefix_expr | infix_expr | call_expr
#     | subscript_expr
class Expression(Subparser):


    def get_prefix_subparser(self, token):
        return self.get_subparser(token, {
            'NUMBER': NumberExpression,
            'STRING': StringExpression,
            'NAME': NameExpression,
            'LPAREN': GroupExpression,
            'LBRACK': ArrayExpression,
            'LCBRACK': DictionaryExpression,
            'OPERATOR': UnaryOperatorExpression,
        })

    def get_infix_subparser(self, token):
        return self.get_subparser(token, {
            'OPERATOR': BinaryOperatorExpression,
            'LPAREN': CallExpression,
            'LBRACK': SubscriptOperatorExpression,
            'OBJECT': objectStatement,})

    def get_next_precedence(self, tokens):
        if not tokens.is_end():
            token = tokens.current()

            parser = self.get_infix_subparser(token)
            if parser is not None:
                return parser.get_precedence(token)
        return 0

    def parse(self, parser, tokens, precedence=0,file=None):
        if file== None:
            raise RuntimeError("FILE NEEDED :(")
        if "-t" in sys.argv or "--trace" in sys.argv:
                print("-|Expression")
        subparser = self.get_prefix_subparser(tokens.current())
        if subparser is not None:
            left = None
            if "file" in inspect.getfullargspec(subparser.parse).args:
                left = subparser.parse(parser,tokens,file)
            else:
                left = subparser.parse(parser, tokens)
            if left is not None:
                while precedence < self.get_next_precedence(tokens):
                    op = self.get_infix_subparser(tokens.current())
                    if "-f" in sys.argv or "--file" in sys.argv:
                        print("+++++")
                        print(f"FILE: {file}")
                        print("file" in inspect.getfullargspec(op.parse).args)
                        print(op)
                        print("+++++")

                    if "file" in inspect.getfullargspec(op.parse).args:

                        op = op.parse(parser, tokens, left,file=file)
                    else:
                        op = op.parse(parser, tokens,left)

                    if op is not None:
                        left = op
                return left


# list_of_expr: (expr COMMA)*
class ListOfExpressions(Subparser):

    def parse(self, parser, tokens,file):
        if "-t" in sys.argv or "--trace" in sys.argv:
            print("-|ListOfExp")
        items = []

        while not tokens.is_end():
            exp = Expression().parse(parser, tokens,file=file)
            if exp is not None:
                items.append(exp)
            else:
                break
            if tokens.current().name == 'COMMA':
                tokens.consume_expected('COMMA')
            else:
                break
        return items


# block: NEWLINE INDENT stmnts DEDENT
class Block(Subparser):

    def parse(self, parser, tokens,file):
        tokens.consume_expected('NEWLINE', 'INDENT')
        if "-t" in sys.argv or "--trace" in sys.argv:
            print("-|Block")
        statements = Statements().parse(parser, tokens,file)
        tokens.consume_expected('DEDENT')
        return statements



class importStatement(Subparser):
    def _parse_params(self, tokens):
        exit = False
        params = []

        if tokens.current().name == 'NAME':
            while exit == False:
                id_token = tokens.consume_expected('NAME')
                params.append(id_token.value)
                if tokens.current().name == 'COMMA':
                    tokens.consume_expected('COMMA')
                else:
                    break
        return params
    def parse(self,parser,tokens,file):
        if "-t" in sys.argv or "--trace" in sys.argv:
            print("-|importStatement")
        try:
            stf = False
            #monochrome(tokens)
            tokens.consume_expected('IMPORT')
            #id_token = tokens.consume_expected('NAME')
            #pkg = id_token.value
            if tokens.current().name != "STRING":

                pkgs = self._parse_params(tokens)
            else:
                stf = True
                pkgs = [tokens.consume_expected("STRING")]
            #pkgs.append(pkg)

            #... import pkgs ...
            from monochrome.eval import execf
            import monochrome
            import os
            from monochrome.mods import getslash
            for pk in pkgs:

                path = "/"
                if stf == False:
                    path = str(os.getcwd()) + getslash(str(os.getcwd())) + pk + ".mce"
                if stf == True:
                    pk = pk.value
                    path = pk
                l = []
                try:

                    l = execf(path)
                except FileNotFoundError:
                    try:
                        l = execf(str(monochrome.lib.path) + getslash(str(monochrome.lib.path)) + pk + getslash(str(monochrome.lib.path)) + "__init__.mce")
                    except FileNotFoundError:
                        raise ParserError(f"Import not found - '{pk}'",tokens.current())

                #x = {}
                if "-i" in sys.argv or "--imports" in sys.argv:
                    print(f"+ Imported {pk}")



                ta = {}

                tx = l[-1].env._values
                if tx.get("module",{}).get("exports",None) == None:


                    for v in tx:


                            ta[v] = tx[v]



                    monochrome.environ.get_env(file).set(pk,ta)
                else:
                    monochrome.environ.get_env(file).set(pk,tx["module"]["exports"])

            tokens.consume_expected("NEWLINE")

        except RecursionError:
            cur = tokens.current()
            raise RuntimeError(f"Circular import found in: {pkgs}")
            exit()
        return ast.Identifier(pkgs[0])

class pyimportStatement(Subparser):
    def _parse_params(self, tokens):
        exit = False
        params = []

        if tokens.current().name == 'NAME':
            while exit == False:
                id_token = tokens.consume_expected('NAME')
                params.append(id_token.value)
                if tokens.current().name == 'COMMA':
                    tokens.consume_expected('COMMA')
                else:
                    break
        return params
    def parse(self,parser,tokens,file):
        if "-t" in sys.argv or "--trace" in sys.argv:
            print("-|pyimportStatement")
        try:
            #monochrome(tokens)
            tokens.consume_expected('PYIMPORT')
            #id_token = tokens.consume_expected('NAME')
            #pkg = id_token.value

            pkgs = self._parse_params(tokens)
            #pkgs.append(pkg)
            lvl = 0

            #... import pkgs ...
            if tokens.current() == "NUMBER":
                lvl = tokens.consume_expected("NUMBER")
                lvl = lvl.value
            from monochrome.eval import execf
            import monochrome
            import os
            from monochrome.mods import getslash

            for pk in pkgs:
                ta = {}

                x = __import__(pk)
                td = None
                def gettd(x):
                    td = ""
                    if type(x) == type(getslash):
                        td = getslash
                    elif type(x) == type(importStatement):
                        td = importStatement
                    return td
                d = x.__dict__

                for i in d:
                    if i not in dir(gettd(x)):
                        ta[i] = d[i]

                monochrome.environ.get_env(file).set(pk,ta)
                if "-i" in sys.argv or "--imports" in sys.argv:
                    print(f"+ Imported {pk} (python)")
            tokens.consume_expected("NEWLINE")
        except RecursionError:
            cur = tokens.current()
            raise RuntimeError(f"Circular import found in: {pkgs}")
            exit()
        return ast.Identifier(pkgs[0])

class methodStatement(Subparser):


    # func_params: (NAME COMMA)*
    def _parse_params(self, tokens):
        params = []
        if tokens.current().name != 'RPAREN':
            while not tokens.is_end():
                id_token = tokens.consume_expected(tokens.current().name)
                params.append(id_token.value)
                if tokens.current().name == 'COMMA':
                    tokens.consume_expected('COMMA')
                else:
                    break
        return params

    def parse(self, parser, tokens,file):
        import monochrome
        import sys
        if "-t" in sys.argv or "--trace" in sys.argv:
            print("-|methodStatement")
        tokens.consume_expected('METHOD')
        func = tokens.consume_expected('NAME')


        tfunc = monochrome.environ.get_env(file).get(func.value)
        if tfunc == None:
            raise NameError(f"Method not found: {func.value}")

        if tokens.current().name == "OBJECT":
            x = objectStatement().parse(parser,tokens,method=True,file=file)
            tfunc = x
        tokens.consume_expected("LPAREN")
        preargs = self._parse_params(tokens)

        tokens.consume_expected("RPAREN")
        tokens.consume_expected("NEWLINE")



        subfunc = FunctionStatement().parse(parser,tokens,file)

        preargs.append(subfunc)
        try:

            tr = monochrome.interpreter.eval_call("",monochrome.environ.get_env(file),f=tfunc,args=preargs)
        except Exception as e:
            raise Exception(f"Return type does not have an associated converter.\n{e}")
        monochrome.environ.get_env(file).set(subfunc.name,tr)

        return ast.Identifier(subfunc.name)
class objectStatement(Subparser):
    def _parse_params(self,tokens):
        keys = []
        while tokens.current().name == "OBJECT":
            tokens.consume_expected("OBJECT")
            keys.append(tokens.consume_expected("NAME").value)
        return keys
    def _parse_params2(self, tokens):
        params = []
        if tokens.current().name != 'RPAREN':
            while not tokens.is_end():
                id_token = tokens.consume_expected(tokens.current().name)
                params.append(id_token.value)
                if tokens.current().name == 'COMMA':
                    tokens.consume_expected('COMMA')
                else:
                    break
        return params
    def parse(self,parser,tokens,left=None,method=False,file=None):
        if file == "/":
            raise RuntimeError("FNF")

        import monochrome.env
        if file == None:
            raise RuntimeError("FILE NEEDED :(")

        import sys
        if "-t" in sys.argv or "--trace" in sys.argv:
            print("-|objectStatement")
        v = ""
        if left == None:
            v = tokens.previous(1)
        else:
            v = left
        import monochrome

        vo = monochrome.environ.get_env(file).get(v.value)
        if vo == None:
            raise NameError(f"Object/Dict not found: {v.value}")
        dictkeys = self._parse_params(tokens)
        x = vo
        y = x
        if type(vo) != dict and type(vo) != ast.Dictionary:
            raise RuntimeError(f"Type of object must be a dict: {v.value} - {type(vo)}")






        if tokens.current().name == "ASSIGN":
            tokens.consume_expected('ASSIGN')
            right = Expression().parse(parser, tokens,file=file)
            if type(right) == ast.Identifier:
                right = monochrome.environ.get_env(file).get(right.value)
            x = right
            try:
                x = x.value
            except Exception as e:
                if "-e" in sys.argv or "--errors" in sys.argv:
                    print(f"ObjectError: {e}")
                x = x

            pyxec = exec
            te = "x"
            for i in dictkeys:
                te += f"['{i}']"
            locel = {"x":y,"r":x}
            exec(f"{te} = r",globals(),locel)
            monochrome.environ.get_env(file).set(v.value,locel["x"])
            return right
        te = "x"
        for i in dictkeys:
            te += f"['{i}']"
        locel = {"x":y,"r":x}
        exec(f"db = {te}",globals(),locel)
        x = locel["db"]
        if tokens.current().name == "LPAREN" and method == False:
            #raise ParserError("Called @",tokens.current())

            tokens.consume_expected("LPAREN")

            nargs = self._parse_params2(tokens)

            tokens.consume_expected("RPAREN")
            tr = monochrome.interpreter.eval_call("",monochrome.environ.get_env(file),f=x,args=nargs)

            if type(tr) not in monochrome.interpreter.evaluators:
                if type(tr) in monochrome.interpreter.converters:
                    tr = monochrome.interpreter.converters[type(tr)](tr,env=monochrome.environ.get_env(file))
            return tr







        if tokens.current().name == "NEWLINE":
            tokens.consume_expected("NEWLINE")
        if type(x) not in monochrome.interpreter.evaluators:
            if type(x) in monochrome.interpreter.converters:
                x = monochrome.interpreter.converters[type(x)](x,env=monochrome.environ.get_env(file))


        return x
    def get_precedence(self, token):
        return self.PRECEDENCE["object"]


class FunctionStatement(Subparser):


    # func_params: (NAME COMMA)*
    def _parse_params(self, tokens):
        params = []
        if tokens.current().name == 'NAME':
            while not tokens.is_end():
                id_token = tokens.consume_expected('NAME')
                params.append(id_token.value)
                if tokens.current().name == 'COMMA':
                    tokens.consume_expected('COMMA')
                else:
                    break
        return params

    def parse(self, parser, tokens,file):
        tokens.consume_expected('FUNCTION')
        id_token = tokens.consume_expected('NAME')
        tokens.consume_expected('LPAREN')

        arguments = self._parse_params(tokens)
        import sys
        if "-t" in sys.argv or "--trace" in sys.argv:
            print("-|FunctionStatement")

        tokens.consume_expected('RPAREN', 'COLON')
        with enter_scope(parser, 'function'):
            block = Block().parse(parser, tokens,file=file)
        if block is None:
            raise ParserError('Expected function body', tokens.current())
        return ast.Function(id_token.value, arguments, block)


# cond_stmnt: IF expr COLON block (ELIF COLON block)* (ELSE COLON block)?
class ConditionalStatement(Subparser):

    def _parse_elif_conditions(self, parser, tokens,file):
        conditions = []
        while not tokens.is_end() and tokens.current().name == 'ELIF':
            tokens.consume_expected('ELIF')
            test = Expression().parse(parser, tokens,file=file)
            if test is None:
                raise ParserError('Expected `elif` condition', tokens.current())
            tokens.consume_expected('COLON')
            block = Block().parse(parser, tokens)
            if block is None:
                raise ParserError('Expected `elif` body', tokens.current())
            conditions.append(ast.ConditionElif(test, block))
        return conditions

    def _parse_else(self, parser, tokens,file):
        if "-t" in sys.argv or "--trace" in sys.argv:
            print("-|ConditionalStatement")
        else_block = None
        if not tokens.is_end() and tokens.current().name == 'ELSE':
            tokens.consume_expected('ELSE', 'COLON')
            else_block = Block().parse(parser, tokens,file)
            if else_block is None:
                raise ParserError('Expected `else` body', tokens.current())
        return else_block

    def parse(self, parser, tokens,file):
        tokens.consume_expected('IF')
        test = Expression().parse(parser, tokens,file=file)
        #print(test)
        if test is None:
            raise ParserError('Expected `if` condition', tokens.current())
        #print("XX")
        tokens.consume_expected('COLON')
        if_block = Block().parse(parser, tokens,file)
        if if_block is None:
            raise ParserError('Expected if body', tokens.current())
        elif_conditions = self._parse_elif_conditions(parser, tokens,file=file)
        else_block = self._parse_else(parser, tokens,file)
        return ast.Condition(test, if_block, elif_conditions, else_block)


# match_stmnt: MATCH expr COLON NEWLINE INDENT match_when+ (ELSE COLON block)? DEDENT
class MatchStatement(Subparser):

    # match_when: WHEN expr COLON block
    def _parse_when(self, parser, tokens):
        tokens.consume_expected('WHEN')
        pattern = Expression().parse(parser, tokens)
        if pattern is None:
            raise ParserError('Pattern expression expected', tokens.current())
        tokens.consume_expected('COLON')
        block = Block().parse(parser, tokens)
        return ast.MatchPattern(pattern, block)

    def parse(self, parser, tokens):
        if "-t" in sys.argv or "--trace" in sys.argv:
            print("-|MatchStatement")
        tokens.consume_expected('MATCH')
        test = Expression().parse(parser, tokens)
        tokens.consume_expected('COLON', 'NEWLINE', 'INDENT')
        patterns = []
        while not tokens.is_end() and tokens.current().name == 'WHEN':
            patterns.append(self._parse_when(parser, tokens))
        if not patterns:
            raise ParserError('One or more `when` pattern excepted', tokens.current())
        else_block = None
        if not tokens.is_end() and tokens.current().name == 'ELSE':
            tokens.consume_expected('ELSE', 'COLON')
            else_block = Block().parse(parser, tokens)
            if else_block is None:
                raise ParserError('Expected `else` body', tokens.current())
        tokens.consume_expected('DEDENT')
        return ast.Match(test, patterns, else_block)


# loop_while_stmnt: WHILE expr COLON block
class WhileLoopStatement(Subparser):

    def parse(self, parser, tokens):
        if "-t" in sys.argv or "--trace" in sys.argv:
            print("-|WhileLoopStatement")
        tokens.consume_expected('WHILE')
        test = Expression().parse(parser, tokens)
        if test is None:
            raise ParserError('While condition expected', tokens.current())
        tokens.consume_expected('COLON')
        with enter_scope(parser, 'loop'):
            block = Block().parse(parser, tokens)
        if block is None:
            raise ParserError('Expected loop body', tokens.current())
        return ast.WhileLoop(test, block)


# loop_for_stmnt: FOR NAME expr COLON block
class ForLoopStatement(Subparser):

    def parse(self, parser, tokens):
        if "-t" in sys.argv or "--trace" in sys.argv:
            print("-|ForLoopStatement")
        tokens.consume_expected('FOR')
        id_token = tokens.consume_expected('NAME')
        tokens.consume_expected('IN')
        collection = Expression().parse(parser, tokens)
        tokens.consume_expected('COLON')
        with enter_scope(parser, 'loop'):
            block = Block().parse(parser, tokens)
        if block is None:
            raise ParserError('Expected loop body', tokens.current())
        return ast.ForLoop(id_token.value, collection, block)


# return_stmnt: RETURN expr?
class ReturnStatement(Subparser):

    def parse(self, parser, tokens,file):
        if "-t" in sys.argv or "--trace" in sys.argv:
            print("-|ReturnStatement")
        if not parser.scope or 'function' not in parser.scope:
            raise ParserError('Return outside of function', tokens.current())
        tokens.consume_expected('RETURN')
        value = Expression().parse(parser, tokens,file=file)
        tokens.consume_expected('NEWLINE')
        return ast.Return(value)


# break_stmnt: BREAK
class BreakStatement(Subparser):

    def parse(self, parser, tokens):
        if "-t" in sys.argv or "--trace" in sys.argv:
            print("-|BreakStatement")
        if not parser.scope or parser.scope[-1] != 'loop':
            raise ParserError('Break outside of loop', tokens.current())
        tokens.consume_expected('BREAK', 'NEWLINE')
        return ast.Break()


# cont_stmnt: CONTINUE
class ContinueStatement(Subparser):

    def parse(self, parser, tokens):
        if "-t" in sys.argv or "--trace" in sys.argv:
            print("-|ContinueStatement")
        if not parser.scope or parser.scope[-1] != 'loop':
            raise ParserError('Continue outside of loop', tokens.current())
        tokens.consume_expected('CONTINUE', 'NEWLINE')
        return ast.Continue()


# assing_stmnt: expr ASSIGN expr NEWLINE
class AssignmentStatement(Subparser):

    def parse(self, parser, tokens, left,file):
        if "-t" in sys.argv or "--trace" in sys.argv:
            print("-|AssignStatement")
        tokens.consume_expected('ASSIGN')
        right = Expression().parse(parser, tokens,file=file)
        tokens.consume_expected('NEWLINE')
        return ast.Assignment(left, right)
class extendStatement(Subparser):

    def parse(self, parser, tokens, file):
        if "-t" in sys.argv or "--trace" in sys.argv:
            print("-|extendStatement")
        tokens.consume_expected('EXTEND')
        n = tokens.consume_expected("STRING")
        p = tokens.consume_expected("STRING")
        with open(p.value) as f:
            locel = {"environ":monochrome.environ,"ast":monochrome.ast,"Subparser":Subparser}
            exec(f.read(),{},locel)
            #ext_data = locel["ext_data"]
            monochrome.exts.exts[n.value.upper()] = locel["parse"]
            monochrome.exts.lexts[n.value] = n.value.upper()
        tokens.consume_expected("NEWLINE")
        return monochrome.ast.String(value=n.value)

# expr_stmnt: assing_stmnt
#           | expr NEWLINE
class ExpressionStatement(Subparser):

    def parse(self, parser, tokens,file):
        if "-t" in sys.argv or "--trace" in sys.argv:
            print("-|ExpressionStatement")
        exp = Expression().parse(parser, tokens,file=file)
        if exp is not None:
            if tokens.current().name == 'ASSIGN':
                return AssignmentStatement().parse(parser, tokens, exp,file)
            elif tokens.current().name == "OBJECT":
                return objectStatement().parse(parser,tokens,file)


            else:
                tokens.consume_expected('NEWLINE')
                return exp


# stmnts: stmnt*
class Statements(Subparser):

    def get_statement_subparser(self, token):

        return self.get_subparser(token, {
            'IMPORT': importStatement,
            'PYIMPORT': pyimportStatement,
            'FUNCTION': FunctionStatement,
            'METHOD': methodStatement,
            'IF': ConditionalStatement,
            'MATCH': MatchStatement,
            'WHILE': WhileLoopStatement,
            'FOR': ForLoopStatement,
            'RETURN': ReturnStatement,
            'BREAK': BreakStatement,
            'CONTINUE': ContinueStatement,
            'OBJECT': objectStatement,
            'EXTEND': extendStatement,
        **monochrome.exts.exts}, ExpressionStatement)

    def parse(self, parser, tokens,file):
        import sys
        if "-t" in sys.argv or "--trace" in sys.argv:
            print("-|Statement")
        statements = []
        while not tokens.is_end():
            statement = self.get_statement_subparser(tokens.current())
            if "file" in inspect.getfullargspec(statement.parse).args:
                statement = statement.parse(parser,tokens,file)
            else:
                statement = statement.parse(parser,tokens)
            if statement is not None:
                statements.append(statement)
            else:
                break
        return statements


# prog: stmnts
class Program(Subparser):

    def parse(self, parser, tokens,file):
        import sys
        if "-t" in sys.argv or "--trace" in sys.argv:
            print("-|Program")
        statements = Statements().parse(parser, tokens,file)


        tokens.expect_end()

        return ast.Program(statements)


class Parser(object):

    def __init__(self):
        self.scope = None

    def parse(self, tokens,file):
        import sys
        if "-t" in sys.argv or "--trace" in sys.argv:
            print("-|Parser")
        self.scope = []
        return Program().parse(self, tokens,file)
