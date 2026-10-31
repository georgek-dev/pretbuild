import pretbuild.pybuild.backend as backend
import os
import sys

def help():
    return "builds a python sdist and wheel"

def prog(done, count, name):
    print(f"{done}/{count} {name}".ljust(80), end="\r", flush=True)

def cli_main(outdir=None):
    if outdir == None:
        if len(sys.argv) < 2:
            outdir = "dist"
        else:
            outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    sdist = backend.build_sdist(outdir, progress=prog)
    print(f"{sdist}".ljust(80))
    wheel = backend.build_wheel(outdir, progress=prog)
    print(f"{wheel}".ljust(80))

if __name__ == "__main__":
    cli_main()
