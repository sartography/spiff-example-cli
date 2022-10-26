#!/usr/bin/env python

import argparse
from copy import deepcopy

from custom_script import loads, dumps, get_globals

if __name__ == '__main__':

    parent = argparse.ArgumentParser()
    subparsers = parent.add_subparsers(dest='method')

    shared = argparse.ArgumentParser('Context', add_help=False)
    shared.add_argument('-c', '--context', dest='context', required=True)
    shared.add_argument('-x', '--extra', dest='extra')

    eval_args = subparsers.add_parser('eval', parents=[shared])
    eval_args.add_argument('-e', '--expr', dest='expr', type=str, required=True)

    exec_args = subparsers.add_parser('exec', parents=[shared])
    exec_args.add_argument('-s', '--script', dest='script', type=str, required=True)

    args = parent.parse_args()
    context = loads(args.context)
    extra = loads(args.extra) if args.extra is not None else {}
    if args.method == 'eval':
        result = eval(args.expr, get_globals(context, extra))
    elif args.method == 'exec':
        exec(args.script, get_globals(context, extra), context)
        result = context
    print(dumps(result))
