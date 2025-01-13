import sqlite3, json
import os
import logging
from uuid import uuid4, UUID

from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer
from SpiffWorkflow.bpmn.serializer.default.workflow import BpmnWorkflowConverter, BpmnSubWorkflowConverter
from SpiffWorkflow.bpmn.serializer.default.process_spec import BpmnProcessSpecConverter
from SpiffWorkflow.bpmn.specs.mixins.subworkflow_task import SubWorkflowTask

logger = logging.getLogger(__name__)

class WorkflowConverter(BpmnWorkflowConverter):

    def to_dict(self, workflow):
        dct = super(BpmnWorkflowConverter, self).to_dict(workflow)
        dct['bpmn_events'] = self.registry.convert(workflow.bpmn_events)
        dct['subprocesses'] = {}
        dct['tasks'] = list(dct['tasks'].values())
        return dct

class SubworkflowConverter(BpmnSubWorkflowConverter):

    def to_dict(self, workflow):
        dct = super().to_dict(workflow)
        dct['tasks'] = list(dct['tasks'].values())
        return dct

class WorkflowSpecConverter(BpmnProcessSpecConverter):

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['task_specs'] = list(dct['task_specs'].values())
        return dct


class SqliteSerializer(BpmnWorkflowSerializer):

    @staticmethod
    def initialize(db):
        with open(os.path.join(os.path.dirname(__file__), 'schema-sqlite.sql')) as fh:
            db.executescript(fh.read())
            db.commit()

    def __init__(self, dbname, **kwargs):
        super().__init__(**kwargs)
        self.dbname = dbname

    def create_workflow_spec(self, spec, dependencies):
        spec_id, new = self.execute(self._create_workflow_spec, spec)
        if new and len(dependencies) > 0:
            pairs = self.get_spec_dependencies(spec_id, spec, dependencies)
            # This handles the case where the participant requires an event to be kicked off
            added = list(map(lambda p: p[1], pairs))
            for name, child in dependencies.items():
                child_id, new_child = self.execute(self._create_workflow_spec, child)
                if new_child:
                    pairs |= self.get_spec_dependencies(child_id, child, dependencies)
                pairs.add((spec_id, child_id))
            self.execute(self._set_spec_dependencies, pairs)
        return spec_id

    def get_spec_dependencies(self, parent_id, parent, dependencies):
        # There ought to be an option in the parser to do this
        pairs = set()
        for task_spec in filter(lambda ts: isinstance(ts, SubWorkflowTask), parent.task_specs.values()):
            child = dependencies.get(task_spec.spec)
            child_id, new = self.execute(self._create_workflow_spec, child)
            pairs.add((parent_id, child_id))
            if new:
                pairs |= self.get_spec_dependencies(child_id, child, dependencies)
        return pairs

    def get_workflow_spec(self, spec_id, include_dependencies=True):
        return self.execute(self._get_workflow_spec, spec_id, include_dependencies)

    def list_specs(self):
        return self.execute(self._list_specs)

    def delete_workflow_spec(self, spec_id):
        return self.execute(self._delete_workflow_spec, spec_id)

    def create_workflow(self, workflow, spec_id):
        return self.execute(self._create_workflow, workflow, spec_id)

    def get_workflow(self, wf_id, include_dependencies=True):
        return self.execute(self._get_workflow, wf_id, include_dependencies)

    def update_workflow(self, workflow, wf_id):
        return self.execute(self._update_workflow, workflow, wf_id)

    def list_workflows(self, include_completed=False):
        return self.execute(self._list_workflows, include_completed)

    def delete_workflow(self, wf_id):
        return self.execute(self._delete_workflow, wf_id)

    def _create_workflow_spec(self, cursor, spec):
        cursor.execute(
            "select id, false from workflow_spec where serialization->>'file'=? and serialization->>'name'=?",
            (spec.file, spec.name)
        )
        row = cursor.fetchone()
        if row is None:
            dct = self.to_dict(spec)
            spec_id = uuid4()
            cursor.execute("insert into workflow_spec (id, serialization) values (?, ?)", (spec_id, dct))
            return spec_id, True
        else:
            return row

    def _set_spec_dependencies(self, cursor, values):
        cursor.executemany("insert into _spec_dependency (parent_id, child_id) values (?, ?)", values)

    def _get_workflow_spec(self, cursor, spec_id, include_dependencies):
        cursor.execute("select serialization as 'serialization [json]' from workflow_spec where id=?", (spec_id, ))
        spec = self.from_dict(cursor.fetchone()[0])
        subprocess_specs = {}
        if include_dependencies:
            subprocess_specs = self._get_subprocess_specs(cursor, spec_id)
        return spec, subprocess_specs

    def _get_subprocess_specs(self, cursor, spec_id):
        subprocess_specs = {}
        cursor.execute(
            "select serialization->>'name', serialization as 'serialization [json]' from spec_dependency where root=?",
            (spec_id, )
        )
        for name, serialization in cursor:
            subprocess_specs[name] = self.from_dict(serialization)
        return subprocess_specs

    def _list_specs(self, cursor):
        cursor.execute("select id, name, filename from spec_library")
        return cursor.fetchall()

    def _delete_workflow_spec(self, cursor, spec_id):
        try:
            cursor.execute("delete from workflow_spec where id=?", (spec_id, ))
        except sqlite3.IntegrityError:
            logger.warning(f'Unable to delete spec {spec_id} because it is used by existing workflows')

    def _create_workflow(self, cursor, workflow, spec_id):
        dct = super().to_dict(workflow)
        wf_id = uuid4()
        stmt = "insert into workflow (id, workflow_spec_id, serialization) values (?, ?, ?)"
        cursor.execute(stmt, (wf_id, spec_id, dct))
        if len(workflow.subprocesses) > 0:
            cursor.execute("select serialization->>'name', descendant from spec_dependency where root=?", (spec_id, ))
            dependencies = dict((name, id) for name, id in cursor)
            for sp_id, sp in workflow.subprocesses.items():
                cursor.execute(stmt, (sp_id, dependencies[sp.spec.name], self.to_dict(sp)))
        return wf_id

    def _get_workflow(self, cursor, wf_id, include_dependencies):
        cursor.execute("select workflow_spec_id, serialization as 'serialization [json]' from workflow where id=?", (wf_id, ))
        row = cursor.fetchone()
        spec_id, workflow = row[0], self.from_dict(row[1])
        if include_dependencies:
            workflow.subprocess_specs = self._get_subprocess_specs(cursor, spec_id)
            cursor.execute(
                "select descendant as 'id [uuid]', serialization as 'serialization [json]' from workflow_dependency where root=? order by depth",
                (wf_id, )
            )
            for sp_id, sp in cursor:
                task = workflow.get_task_from_id(sp_id)
                workflow.subprocesses[sp_id] = self.from_dict(sp, task=task, top_workflow=workflow)
        return workflow

    def _update_workflow(self, cursor, workflow, wf_id):
        dct = self.to_dict(workflow)
        cursor.execute("select descendant as 'id [uuid]' from workflow_dependency where root=?", (wf_id, ))
        dependencies = [row[0] for row in cursor]
        cursor.execute(
            "select serialization->>'name', descendant as 'id [uuid]' from spec_dependency where root=(select workflow_spec_id from _workflow where id=?)",
            (wf_id, )
        )
        spec_dependencies = dict((name, spec_id) for name, spec_id in cursor)
        stmt = "update workflow set serialization=? where id=?"
        cursor.execute(stmt, (dct, wf_id))
        for sp_id, sp in workflow.subprocesses.items():
            sp_dct = self.to_dict(sp)
            if sp_id in dependencies:
                cursor.execute(stmt, (sp_dct, sp_id))
            else:
                cursor.execute(
                    "insert into workflow (id, workflow_spec_id, serialization) values (?, ?, ?)",
                    (sp_id, spec_dependencies[sp.spec.name], sp_dct)
                )

    def _list_workflows(self, cursor, include_completed):
        if include_completed:
            query = "select id, spec_name, active_tasks, started, updated, ended from instance"
        else:
            query = "select id, spec_name, active_tasks, started, updated, ended from instance where ended is null"
        cursor.execute(query)
        return cursor.fetchall()

    def _delete_workflow(self, cursor, wf_id):
        cursor.execute("select descendant as 'id [uuid]' from workflow_dependency where root=?", (wf_id, ))
        for sp_id in [row[0] for row in cursor]:
            cursor.execute("delete from workflow where id=?", (sp_id, ))
        cursor.execute("delete from workflow where id=?", (wf_id, ))

    def execute(self, func, *args, **kwargs):

        conn = sqlite3.connect(self.dbname, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        conn.execute("pragma foreign_keys=on")
        sqlite3.register_adapter(UUID, lambda v: str(v))
        sqlite3.register_converter("uuid", lambda s: UUID(s.decode('utf-8')))
        sqlite3.register_adapter(dict, lambda v: json.dumps(v))
        sqlite3.register_converter("json", lambda s: json.loads(s))
        
        cursor = conn.cursor()
        try:
            rv = func(cursor, *args, **kwargs)
            conn.commit()
        except Exception as exc:
            logger.error(str(exc), exc_info=True)
            conn.rollback() 
        finally:
            cursor.close()
            conn.close()
        return rv
