import monochrome
root = "XX"
#from monochrome.parser import Subparser
class imp(monochrome.parser.Subparser):
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
    def parse(self,parser,tokens):
        mo = []
        if "-t" in sys.argv or "--trace" in sys.argv:
            print("-|importStatement")
        try:
            #monochrome(tokens)
            tokens.consume_expected('IMPORT')
            #id_token = tokens.consume_expected('NAME')
            #pkg = id_token.value

            pkgs = self._parse_params(tokens)
            #pkgs.append(pkg)

            #... import pkgs ...
            from monochrome.eval import execf
            import monochrome
            import os
            from monochrome.mods import getslash
            for pk in pkgs:
                l = []
                try:

                    l = execf(str(os.getcwd()) + getslash(str(os.getcwd())) + pk + ".monochrome")
                except FileNotFoundError:
                    try:
                        l = execf(str(monochrome.lib.path) + getslash(str(monochrome.lib.path)) + pk + getslash(str(monochrome.lib.path)) + "__init__.monochrome")
                    except FileNotFoundError:
                        raise ParserError(f"Import not found - '{pk}'",tokens.current())

                #x = {}
                if "-i" in sys.argv or "--imports" in sys.argv:
                    print(f"+ Imported {pk}")




                ta = {}

                tx = l[-1].env
                mo.append(monochrome.lib.objects.object(pkg=pk,env=tx))




            tokens.consume_expected("NEWLINE")

        except RecursionError:
            cur = tokens.current()
            raise RuntimeError(f"Circular import found in: {pkgs}")
            exit()
        return

class pyimp(monochrome.parser.Subparser):
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
    def parse(self,parser,tokens):
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

                monochrome.current_env.set(pk,ta)
                if "-i" in sys.argv or "--imports" in sys.argv:
                    print(f"+ Imported {pk} (python)")
            tokens.consume_expected("NEWLINE")
        except RecursionError:
            cur = tokens.current()
            raise RuntimeError(f"Circular import found in: {pkgs}")
            exit()
        return ast.Identifier(pkgs[0])

class envy(object):

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
class env:
    def __init__(self):
        self.files = {}
        self.got = {}
    def gen_root(self):
        self.root = root
        self.files[root] = self.gen_env()
        self.files[root].set("__file__",root)
        self.files[root].set("__root__",True)
    def get_env(self,f,g=False):
        tr = self.files.get(f,None)
        if g == True:
            if tr == None:
                self.new_env(f)
        return tr


    def get_pkg(self,obj,v):
        for i in obj:
            if i.pkg == v:
                return i
    def gen_env(self):
        x = monochrome.interpreter.create_global_env()

        return x
    def new_env(self,f):

        self.files[f] = self.gen_env()
        self.files[f].set("__file__",f)
        if f != self.root:
            self.files[f].set("__root__",False)
    def monochromemport(self,f,parser,tokens):


        e = monochrome.env.imp().parse(parser,tokens)
        self.files[f] = e
    def env(self,f=0):
        if f == 0:
            f = self.root
        data = self.files.get(f,None)
        if data == None:
            self.files[f] = monochrome.interpreter.create_global_env()
        return self.files[f]
    def pyimport(self,f,parser,tokens):
        monochrome.env.pyimp().parse(parser,tokens)
environ = env()
