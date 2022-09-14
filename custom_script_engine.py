from gc import get_count
import subprocess, time

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.util.deep_merge import DeepMerge

from engine.custom_script import lookup_product_info, lookup_shipping_cost, dumps, loads
from engine.celery import evaluate, execute

additions = {
    'lookup_product_info': lookup_product_info,
    'lookup_shipping_cost': lookup_shipping_cost
}
CustomScriptEngine = PythonScriptEngine(scripting_additions=additions)


class _CeleryScriptEngine(PythonScriptEngine):

    def _evaluate(self, expression, context, external_methods=None):
        return evaluate(expression, context, external_methods or {})

    def _execute(self, script, context, external_methods=None):
        result = execute(script, context, external_methods)
        DeepMerge.merge(context, result)

    def _execute_async(self, script, context, external_methods=None):
        result = execute.delay(script, context, external_methods or {})
        return self.update_context(result, context)

    def _is_complete(self, result, context):
        return self.update_context(result, context)

    def update_context(self, result, context):
        if result.state == 'SUCCESS':
            DeepMerge.merge(context, result.get())
        else:
            return result

CeleryScriptEngine = _CeleryScriptEngine()


class _DockerScriptEngine(PythonScriptEngine):

    def _evaluate(self, expression, context, external_methods=None):
        sp = self.run([ 'eval', '-e', expression ], context, external_methods)
        return self.get_output(sp)

    def _execute(self, script, context, external_methods=None):
        sp = self.run([ 'exec', '-s', script ], context, external_methods)
        while self.update_context(sp, context) is not None:
            time.sleep(1)

    def _execute_async(self, script, context, external_methods=None):
        sp = self.run([ 'exec', '-s', script ], context, external_methods)
        self.update_context(sp, context)

    def _is_completed(self, sp, context):
        if sp.poll() is None:
            return False
        else:
            result = self.get_output(sp)
            context.update(result)

    def run(self, method, context, external_methods=None):
        cmd = [ 'docker', 'run', 'engine', 'python', 'docker.py' ]
        ctx = [ '-c', dumps(context), '-x', dumps(external_methods or {}) ] 
        return subprocess.Popen(cmd + method + ctx,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def get_output(self, sp):
        return loads(sp.stdout.read().decode('utf-8'))

    def update_context(self, sp, context):
        if sp.poll() is not None:
            DeepMerge.merge(context, self.get_output(sp))
        else:
            return sp

DockerScriptEngine = _DockerScriptEngine()