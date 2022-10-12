import __main__
import inspect
import monochrome.ast
import monochrome.errors
import monochrome.eval
import monochrome.mods
import monochrome.globalvars
import monochrome.modules
import monochrome.parser
import monochrome.ttt
import monochrome.utils
import monochrome.interpreter
import monochrome.lexer
import monochrome.converters
import monochrome.lib
import monochrome.env
from monochrome.env import environ
import monochrome.exts
import monochrome.stdlib
import random
import sys
def randlen(l):
  r = ""
  for i in range(l):
    r += str(random.randint(0,9))
  return r
__version__ = '2.0.0'
ver = {}
ver["1.0.0"] = {"v":"1.0.0","name":"Genesis","changes": "Monochrome v1.0.0 - Genesis\nChangelog:\nThe start of project Monochrome.\n+ ast\n+ interpreter\n+ errors\n+ lexer\n+ parser\n+ repl\n+ utils\n+ ttt\n+ executing files"}
ver["2.0.0"] = {"v":"2.0.0","name":"Neo Noir","changes":f"Monochrome v2.0.0 - Neo Noir\nChangelog:\n+ import\n+ pyimport (import py modules)\n+ objects as dicts\n+ new flags\n+ improved enviornment\n+ standard library (stdlib)\n+ exec & eval & execf\n+ mods to add python functions to every file\n+ converters py <-> mce\n+ methods\n+ extending values into keywords\n- a lot of clutter\n- cleaning up files\n- monochrome.env[mce.os]\n- evalutaors -> sep converters.py\n> Optimised file system using a root file & supporting files\n> tracing executions as well as other handy flags\n> -f --file\n> -i --imports\n> -te --tracexec\n> -vr --version\n> -li --lines\n> -t --trace\n> -e --errors\n> -l --load\n> -e --env\n> -vs --versions"}
if "--versions" in sys.argv or "-vs" in sys.argv:
    for i in ver:
        if "names" in sys.argv:
            na = ver[i]["name"]
            print(f"> {i} - {na}")
        else:
            print(f"> {i}")
    if "names" not in sys.argv:
        print("Include '--versions names' to get the version names")
    exit()
if "-vr" in sys.argv or "--version" in sys.argv:
    xi = ver[__version__]
    for i in ver:
        if i in sys.argv:
            xi = ver.get(i)

    vee = xi["v"]
    na = xi["name"]
    if "changes" in sys.argv:
        y = sys.argv.index("changes")
        tv = ver[sys.argv[y-1]]
        print(tv["changes"])
        exit()


    print(f"Monochrome v{vee} - {na}\nInclude '--version {vee} changes' to get the changelog")
    exit()
root = ""
