from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn.specs.mixins.events.event_types import CatchingEvent


class Instance:

    def __init__(self, wf_id, workflow, save=None):
        self.wf_id = wf_id
        self.workflow = workflow
        self.step = False
        self.task_filter = {}
        self.filtered_tasks = []
        self._save = save

    @property
    def name(self):
        return self.workflow.spec.name

    @property
    def tasks(self):
        return self.workflow.get_tasks()

    @property
    def ready_tasks(self):
        return self.workflow.get_tasks(state=TaskState.READY)

    @property
    def ready_human_tasks(self):
        return self.workflow.get_tasks(state=TaskState.READY, manual=True)

    @property
    def ready_engine_tasks(self):
        return self.workflow.get_tasks(state=TaskState.READY, manual=False)

    @property
    def waiting_tasks(self):
        return self.workflow.get_tasks(state=TaskState.WAITING)

    @property
    def finished_tasks(self):
        return self.workflow.get_tasks(state=TaskState.FINISHED_MASK)

    @property
    def running_subprocesses(self):
        return [sp for sp in self.workflow.subprocesses.values() if not sp.is_completed()]

    @property
    def subprocesses(self):
        return [sp for sp in self.workflow.subprocesses.values()]

    @property
    def data(self):
        return self.workflow.data

    def get_task_display_info(self, task):
        return {
            'depth': task.depth,
            'state': TaskState.get_name(task.state),
            'name': task.task_spec.bpmn_name or task.task_spec.name,
            'lane': task.task_spec.lane,
        }

    def update_task_filter(self, task_filter=None):
        if task_filter is not None:
            self.task_filter.update(task_filter)
        self.filtered_tasks = [t for t in self.workflow.get_tasks(**self.task_filter)]

    def run_task(self, task, data=None):
        if data is not None:
            task.set_data(**data)
        task.run()
        if not self.step:
            self.run_until_user_input_required()
        else:
            self.update_task_filter()

    def run_until_user_input_required(self):
        task = self.workflow.get_next_task(state=TaskState.READY, manual=False)
        while task is not None:
            task.run()
            self.run_ready_events()
            task = self.workflow.get_next_task(state=TaskState.READY, manual=False)
        self.update_task_filter()

    def run_ready_events(self):
        self.workflow.refresh_waiting_tasks()
        task = self.workflow.get_next_task(state=TaskState.READY, spec_class=CatchingEvent)
        while task is not None:
            task.run()
            task = self.workflow.get_next_task(state=TaskState.READY, spec_class=CatchingEvent)
        self.update_task_filter()

    def save(self):
        self._save(self)

