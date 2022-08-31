from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.util.deep_merge import DeepMerge

from engine.custom_script import lookup_product_info, lookup_shipping_cost

from engine import tasks

additions = {
    'lookup_product_info': lookup_product_info,
    'lookup_shipping_cost': lookup_shipping_cost
}
CustomScriptEngine = PythonScriptEngine(scripting_additions=additions)


class _CeleryScriptEngine(PythonScriptEngine):

    def _evaluate(self, expression, context, external_methods=None):
        return tasks.evaluate(expression, context, external_methods or {})

    def _execute(self, script, context, external_methods=None):
        result = tasks.execute.delay(script, context, external_methods or {})
        return self.update_context(result, context)

    def _is_complete(self, result, context):
        return self.update_context(result, context)

    def update_context(self, result, context):
        if result.state == 'SUCCESS':
            DeepMerge.merge(context, result.get())
        else:
            return result


CeleryScriptEngine = _CeleryScriptEngine()