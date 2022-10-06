from copy import copy

import subprocess, time

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.util.deep_merge import DeepMerge

from RestrictedPython import safe_globals

from engine.custom_script import lookup_product_info, lookup_shipping_cost, dumps, loads
from engine.celery import evaluate, execute

additions = {
    'lookup_product_info': lookup_product_info,
    'lookup_shipping_cost': lookup_shipping_cost
}
CustomScriptEngine = PythonScriptEngine(scripting_additions=additions)

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

