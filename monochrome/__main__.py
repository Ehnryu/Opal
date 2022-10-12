"""
Main
----

Command line interface.
"""
import argparse
from monochrome import __version__ as version, interpreter
import monochrome


try:
    input = raw_input
except NameError:
    pass


#def parse_args():
    #argparser = argparse.ArgumentParser()
    #argparser.add_argument('-v', '--verbose', action='store_true')
    #argparser.add_argument('-s', '--session', action='store_true')
    #argparser.add_argument('-l', '--loading', action='store_true')
    #argparser.add_argument('-t', '--trace', action='store_true')
    #argparser.add_argument('file', nargs='?')
    #return argparser.parse_args()


def interpret_file(path, verbose=False):
    monochrome.eval.Execfile(path,verbose,"launch")
        #interpreter.evaluate(f.read(), verbose=verbose)



def repl():
    import monochrome
    print('Monochrome - {}. Press Ctrl+C to exit.'.format(version))
    monochrome.env.root = "temp.mce"
    monochrome.environ.gen_root()
    env = monochrome.environ

    buf = ''
    try:
        while True:
            p = env.get_env(env.root).get("prefix","$")
            inp = input(f"{p} " if not buf else '')

            if inp == '':
                d = interpreter.envy(buf, env.get_env(env.root),file=env.root)




                buf = ''
            else:
                buf += '\n' + inp

    except KeyboardInterrupt:
        pass


def main():
    import sys
    args = sys.argv[1:]
    if "-v" or "--verbose":
        verb = True
    if len(args) > 0:

        if args[0].endswith(".mce"):
            monochrome.env.root = args[0]
            monochrome.environ.gen_root()

            interpret_file(args[0], verb)
        else:
            repl()
    else:
        repl()

if __name__ == '__main__':
    main()
