from collections import namedtuple
from opal.eval import eval

def getfunc(obj):
    
    x = eval.exec(f"func hi():\n    {obj}()\nhi")
    return x

def callpy(obj,args):
    tex = "("
    for item in args:
        if item != args[len(args)-1]:
            tex += f"{item},"
        else:
            tex += f"{item})"
    locel = {}
    if len(args) == 0:
        tex = "()"
    exec(f"e = t{tex}",{"t":obj},locel)
    return locel["e"]
def loadfunc(args):

    #return __import__(args["object"],fromlist=args["from"])
    x = getattr(args["object"],args["from"])
    
    
    return x
def getfrom(args):
    frem = args["from"]
    main = args["object"]
    arg = args["args"]
    func  = eval.exec(f"func {frem}():\n    x = require('{main}')\n    z = import_from(x,'{frem}')\n    callpyfunc(z,{arg})\n{frem}")
    return func
    
            
    
    