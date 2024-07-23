import sys
import json
import logging

from .diff_result import show_spec_diff, show_workflow_diff

def configure_logging():
    task_logger = logging.getLogger('spiff.task')
    task_handler = logging.StreamHandler()
    task_handler.setFormatter(logging.Formatter('%(asctime)s [%(name)s:%(levelname)s] (%(workflow_spec)s:%(task_spec)s) %(message)s'))
    task_logger.addHandler(task_handler)

    wf_logger = logging.getLogger('spiff.workflow')
    wf_handler = logging.StreamHandler()
    wf_handler.setFormatter(logging.Formatter('%(asctime)s [%(name)s:%(levelname)s] (%(workflow_spec)s) %(message)s'))
    wf_logger.addHandler(wf_handler)

def add(engine, args):
    if args.process is not None:
        engine.add_spec(args.process, args.bpmn, args.dmn)
    else:
        engine.add_collaboration(args.collaboration, args.bpmn, args.dmn)

def show_library(engine, args):
    for spec_id, name, filename in engine.list_specs():
        sys.stdout.write(f'{spec_id}  {name:<20s} {filename}\n')

def show_workflows(engine, args):
    for wf_id, name, filename, active, started, updated in engine.list_workflows():
        sys.stdout.write(f'{wf_id}  {name:<20s} {active} {started} {updated or ''}\n')

def run(engine, args):
    instance = engine.start_workflow(args.spec_id)
    instance.run_until_user_input_required()
    instance.save()
    if not args.active and not instance.workflow.is_completed():
        raise Exception('Expected the workflow to complete')
    sys.stdout.write(json.dumps(instance.data, indent=2, separators=[', ', ': ']))
    sys.stdout.write('\n')

def diff_spec(engine, args):
    spec_diff = engine.diff_spec(args.original, args.new)
    show_spec_diff(spec_diff)
    if args.deps:
        diffs, added = engine.diff_dependencies(args.original, args.new)
        for diff in diffs.values():
            show_spec_diff(diff)
        if len(added) > 0:
            sys.stdout.write('\nNew subprocesses\n')
            sys.stdout.write('\n'.join(added))

def diff_workflow(engine, args):
    wf_diff, sp_diffs = engine.diff_workflow(args.wf_id, args.spec_id)
    show_workflow_diff(wf_diff)
    for task_id, result in sp_diffs.items():
        show_workflow_diff(result, task_id=task_id)

def migrate(engine, args):
    engine.migrate_workflow(args.wf_id, args.spec_id, validate=not args.force)

def add_subparsers(subparsers):

    add_spec = subparsers.add_parser('add', help='Add a worfklow spec')
    group = add_spec.add_mutually_exclusive_group(required=True)
    group.add_argument('-p', '--process', dest='process', metavar='BPMN ID', help='The top-level BPMN Process ID')
    group.add_argument('-c', '--collabortion', dest='collaboration', metavar='BPMN ID',  help='The ID of the collaboration')
    add_spec.add_argument('-b', '--bpmn', dest='bpmn', nargs='+', metavar='FILE', help='BPMN files to load')
    add_spec.add_argument('-d', '--dmn', dest='dmn', nargs='*', metavar='FILE', help='DMN files to load')
    add_spec.set_defaults(func=add)

    list_specs = subparsers.add_parser('list_specs', help='List available specs')
    list_specs.set_defaults(func=show_library)

    list_wf = subparsers.add_parser('list_instances', help='List instances')
    list_wf.set_defaults(func=show_workflows)

    run_wf = subparsers.add_parser('run', help='Run a workflow')
    run_wf.add_argument('-s', '--spec-id', dest='spec_id', metavar='SPEC ID', help='The ID of the spec to run')
    run_wf.add_argument('-a', '--active-ok', dest='active', action='store_true',
                        help='Suppress exception if the workflow does not complete')
    run_wf.set_defaults(func=run)

    compare_spec = subparsers.add_parser('diff_spec', help='Compare two workflow specs')
    compare_spec.add_argument('-o', '--original', dest='original', metavar='SPEC ID', help='The ID of the original spec')
    compare_spec.add_argument('-n', '--new', dest='new', metavar='SPEC ID', help='The ID of the new spec')
    compare_spec.add_argument('-d', '--include-dependencies', action='store_true', dest='deps',
                              help='Include dependencies in the output')
    compare_spec.set_defaults(func=diff_spec)

    compare_wf = subparsers.add_parser('diff_workflow', help='Compare a workflow against a new spec')
    compare_wf.add_argument('-w', '--wf-id', dest='wf_id', metavar='WORKFLOW ID', help='The ID of the workflow')
    compare_wf.add_argument('-s', '--spec-id', dest='spec_id', metavar='SPEC ID', help='The ID of the new spec')
    compare_wf.set_defaults(func=diff_workflow)

    migrate_wf = subparsers.add_parser('migrate', help='Update a workflow spec')
    migrate_wf.add_argument('-w', '--wf-id', dest='wf_id', metavar='WORKFLOW ID', help='The ID of the workflow')
    migrate_wf.add_argument('-s', '--spec-id', dest='spec_id', metavar='SPEC ID', help='The ID of the new spec')
    migrate_wf.add_argument('-f', '--force', dest='force', action='store_true', help='Omit validation')
    migrate_wf.set_defaults(func=migrate)
