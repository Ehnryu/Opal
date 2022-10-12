def dictify(v):

    return v.__dict__
a = {'name': 'modulate', 'run': dictify, 'args': ["v"], 'description': 'Turn python module into usable dict'}
export = a
