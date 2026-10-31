import os
import glob

def search(name):
    path = os.environ.get("PATH", "").split(os.pathsep)
    found = []
    for dir in path:
        search = os.path.join(dir, name)
        match = glob.glob(search)
        found.extend(match)

    for i in found:
        found[found.index(i)] = os.path.basename(found[found.index(i)])

    return found
