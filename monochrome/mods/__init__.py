import os
import pathlib
from monochrome.ast import genblin
import copy
path = pathlib.Path(__file__).parent.resolve()
def execfile(p):
    loc = {}
    loc = {**locals(),**loc}
    with open(p,"r") as x:
        exec(x.read(),globals(),loc)
    return loc
def getslash(c):
    c = str(c)
    if "\\" in c:
        return "\\"
    else:
        return "/"
db = {}
for f in os.listdir(path):

    if f.endswith(".py") and f != "__init__.py":
        con = execfile(str(path) + getslash(path) + f)
        if "export" in con:

            con = con["export"]


            if type(con) == dict:
                db[con["name"]] = con
            if type(con) == list:
                for i in con:
                    db[i["name"]] = i
