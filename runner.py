#!/usr/bin/env python

import curses
import importlib
import sys, traceback
from argparse import ArgumentParser

from spiff_example.curses_ui import CursesUI, CursesUIError
from spiff_example.cli import add_subparsers, configure_logging

if __name__ == '__main__':

    parser = ArgumentParser('Simple BPMN App')
    parser.add_argument('-e', '--engine', dest='engine', required=True, metavar='MODULE', help='load engine from %(metavar)s')
    subparsers = parser.add_subparsers(dest='subcommand')
    add_subparsers(subparsers)

    args = parser.parse_args()
    config = importlib.import_module(args.engine)

    try:
        if args.subcommand is None:
            curses.wrapper(CursesUI, config.engine, config.handlers)
        else:
            configure_logging()
            args.func(config.engine, args)
    except Exception as exc:
        sys.stderr.write(traceback.format_exc())
        sys.exit(1)
