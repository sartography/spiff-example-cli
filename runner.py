#!/usr/bin/env python

import argparse
import curses
import importlib
import os
import sys
import traceback

from app import cli


# Constant definitions
FORMS_DIRECTORY = "forms"
DATA_DIRECTORY = "data"


# Command line entry point
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
    cli.add_subparsers(subparsers)
    args = parser.parse_args()

    # Set environment variables to inject directory paths into the configuration
    # modules.
    os.environ["forms_directory"] = FORMS_DIRECTORY
    os.environ["data_directory"] = DATA_DIRECTORY

    # Convert engine file name into module name and import the engine.
    engine = args.engine.rstrip(".py").replace(os.sep, ".")
    config = importlib.import_module(engine)

    try:
        if args.subcommand is None:
            curses.wrapper(cli.CursesUI, config.engine, config.handlers)
        else:
            cli.configure_logging()
            args.func(config.engine, args)
    except Exception:
        sys.stderr.write(traceback.format_exc())
        sys.exit(1)
