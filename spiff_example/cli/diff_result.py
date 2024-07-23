import sys

from SpiffWorkflow import TaskState

def get_name_and_start(spec_diff):
    for ts in spec_diff.alignment:
        if ts == ts._wf_spec.start:
            return ts._wf_spec.name, ts

def show_spec_diff(spec_diff):

    name, start = get_name_and_start(spec_diff)
    updates, checked = [], []

    # This determines what needs to be be displayed (omits specs with exact mappings)
    def order_specs(ts):
        for output in [s for s in ts.outputs if s not in checked]:
            checked.append(output)
            if output in spec_diff.changed or spec_diff.alignment[output] is None:
                updates.append(output)
            order_specs(output)

    order_specs(start)

    sys.stdout.write(f'\nResults for {name}\n\n')
    sys.stdout.write('Changed or Removed\n')

    for ts in updates:
        # Ignore tasks that don't appear in diagrams
        detail = ''
        if ts.bpmn_id is not None:
            if spec_diff.alignment[ts] is None:
                detail = 'removed'
            elif ts in spec_diff.changed:
                detail = ', '.join(spec_diff.changed[ts])
        if detail:
            label = f'{ts.bpmn_name or '-'} [{ts.name}]'
            sys.stdout.write(f'{label:<50s} {detail}\n')

    if len(spec_diff.added) > 0:
        sys.stdout.write('\nAdded\n')
        for ts in spec_diff.added:
            if ts.bpmn_id is not None:
                sys.stdout.write(f'{ts.bpmn_name or '-'} [{ts.name}]\n')


def show_workflow_diff(wf_diff, task_id=None):

    duplicates = []
    if task_id is not None:
        sys.stdout.write(f'\nResults for {task_id}\n\n')
    else:
        sys.stdout.write('Results\n\n')

    sys.stdout.write('Removed\n')
    for task in wf_diff.removed:
        if task.task_spec not in duplicates:
            duplicates.append(task.task_spec)
            label = f'{task.task_spec.bpmn_name or '-'} [{task.task_spec.name}]'
            sys.stdout.write(f'{label:<50s} {TaskState.get_name(task.state)}\n')

    sys.stdout.write('Changed\n')
    for task in wf_diff.changed:
        if task.task_spec not in duplicates:
            duplicates.append(task.task_spec)
            label = f'{task.task_spec.bpmn_name or '-'} [{task.task_spec.name}]'
            sys.stdout.write(f'{label:<50s} {TaskState.get_name(task.state)}\n')

