import subprocess
import pretbuild.clean.main as clean
import pretbuild.build.main as build
import pretbuild.path
import sys

def entry(args):
    cmds = pretbuild.path.search("pret-*")
    if "pret-" + args.tool not in cmds:
        print(f"tool not found: {args.tool}")
        print("Available tools:")
        for i in cmds:
            print(i)
        sys.exit(1)
    else:
        subprocess.run(["pret-" + args.tool])

