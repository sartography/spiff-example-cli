import sys
import json
import logging

def configure_logging():
    spiff_logger = logging.getLogger('spiff')
    spiff_handler = logging.StreamHandler()
    spiff_handler.setFormatter(logging.Formatter('%(asctime)s [%(name)s:%(levelname)s] (%(workflow_spec)s:%(task_spec)s) %(message)s'))
    spiff_logger.addHandler(spiff_handler)

    metrics_logger = logging.getLogger('spiff.metrics')
    metrics_handler = logging.StreamHandler()
    metrics_handler.setFormatter('%(asctime)s [%(name)s:%(levelname)s] (%(workflow_spec)s:%(task_spec)s) %(elasped)s')
    metrics_logger.addHandler(metrics_handler)

def add(engine, args):
    if args.process is not None:
        engine.add_spec(args.process, args.bpmn, args.dmn)
    else:
        engine.add_collaboration(args.collaboration, args.bpmn, args.dmn)

def show_library(engine, args):
    for spec_id, name, filename in engine.list_specs():
        sys.stdout.write(f'{spec_id}  {name:<20s} {filename}\n')

def run(engine, args):
    instance = engine.start_workflow(args.spec_id)
    instance.run_until_user_input_required()
    instance.save()
    if not args.active and not instance.workflow.is_completed():
        raise Exception('Expected the workflow to complete')
    sys.stdout.write(json.dumps(instance.data, indent=2, separators=[', ', ': ']))
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


