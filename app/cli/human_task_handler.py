class TaskHandler:

    def __init__(self, ui):
        self.ui = ui
        self.task = None

    def set_instructions(self, task):
        pass

    def set_fields(self, task):
        pass

    def on_complete(self, results):
        instance = self.ui._states['workflow_view'].instance
        instance.run_task(self.task, results)
        self.ui._states['user_input'].clear()
        self.ui.state = 'workflow_view'

    def show(self, task):
        self.task = task
        self.set_instructions(task)
        self.set_fields(task)
        self.ui._states['user_input'].on_complete = self.on_complete
        self.ui.state = 'user_input'

