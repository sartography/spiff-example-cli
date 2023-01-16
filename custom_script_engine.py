from copy import copy

import subprocess, time
from datetime import timedelta

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.util.deep_merge import DeepMerge

from RestrictedPython import safe_globals

from engine.custom_script import lookup_product_info, lookup_shipping_cost, dumps, loads
from engine.celery import evaluate, execute

additions = {
    'lookup_product_info': lookup_product_info,
    'lookup_shipping_cost': lookup_shipping_cost,
    'timedelta': timedelta,
}
CustomScriptEngine = PythonScriptEngine(scripting_additions=additions)

class PlanSdkScriptEngine(PythonScriptEngine):
    """
    """
    # logger = logging.getLogger(SPIFF_WF_TASK_LOGGER_NAME)

    def create_task_exec_exception(self, task, err):
        current_app.logger.info("in that bad boy")

        if isinstance(err, WorkflowTaskExecException):
            return err

        detail = err.__class__.__name__
        if len(err.args) > 0:
            detail += ":" + str(err.args[0])
        line_number = 0
        error_line = ''
        cl, exc, tb = sys.exc_info()
        # Loop back through the stack trace to find the file called
        # 'string' - which is the script we are executing, then use that
        # to parse and pull out the offending line.
        for frame_summary in traceback.extract_tb(tb):
            if frame_summary.filename == '<string>':
                line_number = frame_summary.lineno
        return WorkflowTaskExecException(task, detail, err, line_number,
                                         error_line)

    def execute(self, task, script, external_methods=None, failure_method=None):
        try:
            current_app.logger.info("HOLLER")
            current_app.logger.info("HOLLER")
            current_app.logger.info("HOLLER")
            current_app.logger.info("HOLLER")
            current_app.logger.info("HOLLER")
            current_app.logger.info("HOLLER")
            current_app.logger.info("HOLLER about to _execute")
            self._execute(script, task.data, external_methods or {})
        except Exception as exc:
            current_app.logger.warn("=====> got exception. now in except. GLOBALS: " + str(self.globals))
            # if self.globals.get(FAILURE_TASK_METHOD_KEY):
            #     self.globals[FAILURE_TASK_METHOD_KEY](task, exc)
            # else:
            raise exc


RestrictedScriptEngine = PythonScriptEngine(default_globals=safe_globals, scripting_additions=additions)

class _CeleryScriptEngine(PythonScriptEngine):

    def _evaluate(self, expression, context, external_methods=None):
        return evaluate(expression, context, external_methods or {})

    def _execute(self, script, context, external_methods=None):
        result = execute(script, context, external_methods)
        while result.state != 'SUCCESS':
            time.sleep(1)
        DeepMerge.merge(context, result)

CeleryScriptEngine = _CeleryScriptEngine()


class _DockerScriptEngine(PythonScriptEngine):

    def _evaluate(self, expression, context, external_methods=None):
        sp = self.run([ 'eval', '-e', expression ], context, external_methods)
        return self.get_output(sp)

    def _execute(self, script, context, external_methods=None):
        sp = self.run([ 'exec', '-s', script ], context, external_methods)
        while sp.poll() is None:
            time.sleep(1)
        DeepMerge.merge(context, self.get_output(sp))

    def run(self, method, context, external_methods=None):
        cmd = [ 'docker', 'run', 'engine', 'python', 'docker.py' ]
        ctx = [ '-c', dumps(context), '-x', dumps(external_methods or {}) ] 
        return subprocess.Popen(cmd + method + ctx,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def get_output(self, sp):
        return loads(sp.stdout.read().decode('utf-8'))

DockerScriptEngine = _DockerScriptEngine()

