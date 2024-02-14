#!/usr/bin/env python

import argparse
import json

from .custom_exec import (
    lookup_product_info,
    lookup_shipping_cost,
    registry,
)

if __name__ == '__main__':

    parent = argparse.ArgumentParser()
    subparsers = parent.add_subparsers(dest='method')

    shared = argparse.ArgumentParser('Context', add_help=False)
    shared.add_argument('-g', '--globals', dest='globals')
    shared.add_argument('-l', '--locals', dest='locals', required=True)

    eval_args = subparsers.add_parser('eval', parents=[shared])
    eval_args.add_argument('-e', '--expr', dest='expr', type=str, required=True)

    exec_args = subparsers.add_parser('exec', parents=[shared])
    exec_args.add_argument('-s', '--script', dest='script', type=str, required=True)

    args = parent.parse_args()
    global_ctx = globals()
    if args.globals is not None:
        global_ctx.update(registry.restore(json.loads(args.globals)))
    local_ctx = registry.restore(json.loads(args.locals))
    if args.method == 'eval':
        result = eval(args.expr, global_ctx, local_ctx)
    elif args.method == 'exec':
        exec(args.script, global_ctx, local_ctx)
        result = local_ctx
    print(json.dumps(registry.convert(result)))
