#!/usr/bin/env python

import argparse
import curses
import importlib
import os
import sys
import traceback

from configuration.cli import add_subparsers, configure_logging, CursesUI

if __name__ == "__main__":

    # Handle command line arguments.
    parser = argparse.ArgumentParser("Simple BPMN App")
    parser.add_argument(
        "-e",
        "--engine",
        dest="engine",
        required=True,
        metavar="MODULE",
        help="load engine from %(metavar)s",
    )
    subparsers = parser.add_subparsers(dest="subcommand")
    add_subparsers(subparsers)
    args = parser.parse_args()

    # Convert engine file name into module name and import the engine.
    engine = args.engine.rstrip('.py').replace(os.sep, '.')
    config = importlib.import_module(engine)

    try:
        if args.subcommand is None:
            curses.wrapper(CursesUI, config.engine, config.handlers)
        else:
            configure_logging()
            args.func(config.engine, args)
    except Exception:
        sys.stderr.write(traceback.format_exc())
        sys.exit(1)
