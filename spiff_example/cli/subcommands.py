import sys, logging
import json

logger = logging.getLogger('spiff_engine')
logger.setLevel(logging.INFO)

def add(engine, args):
    if args.process is not None:
        engine.add_spec(args.process, args.bpmn, args.dmn)
    else:
        engine.add_collaboration(args.collaboration, args.bpmn, args.dmn)

def show_library(engine, args):
    for spec_id, name, filename in engine.list_specs():
        sys.stdout.write(f'{spec_id}  {name:<20s} {filename}\n')

def run(engine, args):
    wf_id = engine.start_workflow(args.spec_id)
    wf = engine.get_workflow(wf_id)
    engine.run_until_user_input_required(wf)
    engine.update_workflow(wf, wf_id)
    if not args.active and not wf.is_completed():
        raise Exception('Expected the workflow to complete')
    sys.stdout.write(json.dumps(wf.data, indent=2, separators=[', ', ': ']))
    sys.stdout.write('\n')


def add_subparsers(subparsers):

    add_spec = subparsers.add_parser('add', help='Add a worfklow spec')
    group = add_spec.add_mutually_exclusive_group(required=True)
    group.add_argument('-p', '--process', dest='process', metavar='BPMN ID', help='The top-level BPMN Process ID')
    group.add_argument('-c', '--collabortion', dest='collaboration', metavar='BPMN ID',  help='The ID of the collaboration')
    add_spec.add_argument('-b', '--bpmn', dest='bpmn', nargs='+', metavar='FILE', help='BPMN files to load')
    add_spec.add_argument('-d', '--dmn', dest='dmn', nargs='*', metavar='FILE', help='DMN files to load')
    add_spec.set_defaults(func=add)

    list_specs = subparsers.add_parser('list', help='List available specs')
    list_specs.set_defaults(func=show_library)

    run_wf = subparsers.add_parser('run', help='Run a workflow')
    run_wf.add_argument('-s', '--spec-id', dest='spec_id', metavar='SPEC ID', help='The ID of the spec to run')
    run_wf.add_argument('-a', '--active-ok', dest='active', action='store_true', help='Suppress exception if the workflow does not complete')
    run_wf.set_defaults(func=run)


