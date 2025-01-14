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
    shared.add_argument('-c', '--context', dest='context', required=True)
    shared.add_argument('-x', '--external-context', dest='external')

    eval_args = subparsers.add_parser('eval', parents=[shared])
    eval_args.add_argument('expr', type=str)

    exec_args = subparsers.add_parser('exec', parents=[shared])
    exec_args.add_argument('script', type=str)

    args = parent.parse_args()
    local_ctx = registry.restore(json.loads(args.context))
    global_ctx = globals()
    global_ctx.update(local_ctx)
    if args.external is not None:
        global_ctx.update(registry.restore(json.loads(args.external)))
    if args.method == 'eval':
        result = eval(args.expr, global_ctx, local_ctx)
    elif args.method == 'exec':
        exec(args.script, global_ctx, local_ctx)
        result = local_ctx
    print(json.dumps(registry.convert(result)))
