from monochrome import ast

py = {
 str: lambda node, env: ast.String(node),
 int: lambda node, env: ast.Number(node),
 list:lambda node, env: ast.Array(node),
 #dict: lambda node,env: 
}

ki = {
ast.String: lambda node, env: node.value,
ast.Number: lambda node, env: node.value,
ast.Array: lambda node, env: monochromel(node,env)
}
def monochromel(l,env):
    tr = []
    for i in l:
        if type(i) in ki:
            tr.append(ki[type(i)](i,env))
    return tr

def converter(node,env,to="monochrome"):
    import monochrome
    evaluators = monochrome.interpreter.evaluators

    tp = type(node)
    if to == "monochrome":
        if tp in py:
            return py[tp](node,env)
    if to == "py":
        if tp in ki:
            return ki[tp](node, env)
    return node
def convert(node,env,to="monochrome"):
    if type(node) == list:
        x = []
        for i in node:
            x.append(converter(i,env,to))
        return converter(x,env,to)
    elif type(node) == dict:
        pass
    return converter(node,env,to)
