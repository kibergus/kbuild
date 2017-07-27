import os
import fnmatch

class MissingEnvironmentalVariableException(Exception):
    pass

def env(name, default=None):
    if default is None and name not in os.environ:
        raise MissingEnvironmentalVariableException(name)

    return os.environ.get(name, default)

def find_files(root, ext):
    matches = []
    for root, dirnames, filenames in os.walk(root):
        for filename in fnmatch.filter(filenames, '*.' + ext):
            matches.append(os.path.join(root, filename))
    return matches
