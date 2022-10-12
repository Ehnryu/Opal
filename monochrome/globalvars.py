import os
gbl = {"path":os.getcwd()}
gbl["True"] = True
gbl["False"] = False
def setglobals(env):
    for i in gbl:
        env.set(i,gbl[i])
