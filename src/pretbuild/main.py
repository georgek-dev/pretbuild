import pretbuild.cli
import argparse
import sys

parser = argparse.ArgumentParser(
    prog=sys.argv[0],
    description='A build and setup tool and runner'
)

parser.add_argument(
    'tool'
)

args = parser.parse_args()

def main():
    pretbuild.cli.entry(args)
