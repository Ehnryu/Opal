import os
def getglobals(gbl):
    globaldict = {"$path":os.getcwd()}
    return globaldict[gbl]