import glob
import os

def clean(file):
    TOCLEAN = []
    try:
        with open(file, "r") as f:
            for l in f:
                l = l.strip()
                if l[:5] == "!glob":
                    files = glob.glob(l[6:].lstrip())
                    for path in files:
                        TOCLEAN.append(os.path.basename(path))
                elif l[:6] == "!rglob":
                    files = glob.glob(l[7:].lstrip(), recursive=True)
                    for path in files:
                        TOCLEAN.append(os.path.basename(path))
                else:
                    TOCLEAN.append(l)
        i = 1
        items = len(TOCLEAN)
        for path in TOCLEAN:
            try:
                print(f"{i}/{items} {path}", end="\r")
                os.remove(path)
                i += 1
            except OSError as e:
                print(f"error while deleting {path}: {e}")
    except FileNotFoundError:
        print(f"file {file} not found")
