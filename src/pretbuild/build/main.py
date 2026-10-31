import pretbuild.build.parser as prs
import sys

def help():
    return "builds a project"

def build_main(file=None):
    if file == None:
        if len(sys.argv) < 2:
            file = "pret.build"
        else:
            file = sys.argv[1]
    try:
        with open(file, "r") as f:
            ast = prs.dsl(f.read())
            prs.eval(ast)
    except SyntaxError as e:
        print(f"error {e} occured while parsing file")
    except FileNotFoundError:
        print(f"file {file} doesn't exist")

if __name__ == "__main__":
    build_main()
