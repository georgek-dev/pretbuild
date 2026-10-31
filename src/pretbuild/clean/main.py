import pretbuild.clean.cleaner as clr
import sys

def help():
    return "cleans object and unneeded files"

def clean_main(file="clean.build"):
    if file == None:
        if len(sys.argv) < 2:
            print("too less arguments")
            sys.exit(1)
        file = sys.argv[1]
    try:
        with open(file, "r") as f:
            clr.clean(file)
    except FileNotFoundError:
        print(f"file {file} doesn't exist")

if __name__ == "__main__":
    clean_main()
