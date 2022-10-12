
import copy
import imp
import sys
from importlib import reload
import monochrome.interpreter
import monochrome.stdlib
startwith = monochrome.stdlib.startwith
monochromet = __import__("monochrome")

class eval:
    eval = monochrome.interpreter.eval_statement
    exec = monochrome.interpreter.evaluate
Eval = monochrome.interpreter.eval_statement
Exec = monochrome.interpreter.evaluate

def execf(path, verbose=False,env=None):
    import monochrome.env
    if "-e" in sys.argv or "--env" in sys.argv:
        print(f"Env -> {env}")
    if "-te" in sys.argv or "--tracexec" in sys.argv:
        print(f"Executing {path}")

    x=  reload(monochromet)






    with open(path) as f:

        if path == monochrome.env.root:
            env = monochrome.environ.get_env(monochrome.env.root)
        if env == None:
            monochrome.environ.new_env(path)
            env = monochrome.environ.get_env(path)

        line = []
        ex = False
        prev = []
        out = None
        fx = f.readlines()
        fx = [*startwith.split("\n"),*fx]
        #exit()
        for l in fx:
            #print(env)
            #print(str([l]) + str(l.startswith(" ") == True or l.startswith("\t") == True or l.endswith(":\n") == True or l.startswith("@") == True))



            if l.startswith(" ") == True or l.startswith("\t") == True or l.endswith(":\n") == True or l.startswith("@") == True:

                prev.append(l)


                ex = True


            else:
                if ex == True:
                    if "-li" in sys.argv or "--lines" in sys.argv:
                        print("".join(prev))

                    out = copy.deepcopy(monochrome.interpreter.envy)("".join(prev),env,file=path)
                    if env == "launch":
                        monochrome.env[str(monochrome.os)] = out.env

                    line.append(monochromet.lib.objects.object(inp=l,env=out.env,out=out.out))
                if l not in prev:
                    if "-li" in sys.argv or "--lines" in sys.argv:
                        print(l)


                    out = copy.deepcopy(monochromet.interpreter.envy)(l,env,file=path)
                    if env == "launch":
                        monochrome.env[str(monochrome.os)] = out.env

                    line.append(monochromet.lib.objects.object(inp=l,env=out.env,out=out.out))
                    ex = False
                prev = []





    if ex == True:

        out = copy.deepcopy(monochromet.interpreter.envy)("".join(prev),env,file=path)
        if env == "launch":
            monochrome.env[str(monochrome.os)] = out.env
        line.append(monochromet.lib.objects.object(inp=l,env=out.env,out=out.out))
    if "-te" in sys.argv or "--traceexec" in sys.argv:
        print(f"Executed {path} ({len(line)} lines)")

    return line
Execfile = execf
