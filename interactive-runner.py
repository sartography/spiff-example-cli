#!/usr/bin/env python

import curses
import importlib
from argparse import ArgumentParser

from spiff_example.curses_ui import CursesUI

if __name__ == '__main__':

    parser = ArgumentParser('Simple BPMN App')
    parser.add_argument('-e', '--engine', dest='engine', required=True, metavar='MODULE', help='load engine from %(metavar)s')
    args = parser.parse_args()

    config = importlib.import_module(args.engine)

    app = curses.wrapper(CursesUI, config.engine)

