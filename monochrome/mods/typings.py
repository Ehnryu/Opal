from monochrome.ast import genblin,Array


def ret():
    def Union(x,y):
        if type(x) == list:


            return [*x,*y]
        elif type(x) == dict and x.get("set",False) == True:
            if y.get("set",False) == False:
                raise RuntimeError("Set Unions can only be done with other sets")
            return {**x,**y}
        else:
            return {**x,**y}
    def set():
        x = {"set":True}

        return x
    x = {}
    x["Union"] = Union
    return x
a = {'name': 'typings', 'run': ret, 'args': [], 'description': 'get typings'}
export = a
