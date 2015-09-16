#!/usr/bin/python

import sys
from icopy import ImageCopy


def main(args):
    for arg in args:
        print(arg)
    ic = ImageCopy(args[0], args[1])
    ic.copy_files()


if __name__ == "__main__":
    main(sys.argv[1:])
