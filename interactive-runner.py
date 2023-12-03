#!/usr/bin/env python

import curses
import os, sqlite3
from argparse import ArgumentParser

from SpiffWorkflow.spiff.parser.process import SpiffBpmnParser
from SpiffWorkflow.spiff.specs.defaults import UserTask, ManualTask
from SpiffWorkflow.spiff.serializer.config import SPIFF_CONFIG
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow, BpmnSubWorkflow
from SpiffWorkflow.bpmn.specs.bpmn_process_spec import BpmnProcessSpec
from SpiffWorkflow.bpmn.specs.mixins.none_task import NoneTask

from spiff_task_handlers import UserTaskHandler, ManualTaskHandler
from engine.serializer import (
    SqliteSerializer,
    WorkflowConverter,
    SubworkflowConverter,
    WorkflowSpecConverter
)
from engine.engine import BpmnEngine
from curses_app import CursesApp

SPIFF_CONFIG[BpmnWorkflow] = WorkflowConverter
SPIFF_CONFIG[BpmnSubWorkflow] = SubworkflowConverter
SPIFF_CONFIG[BpmnProcessSpec] = WorkflowSpecConverter

if __name__ == '__main__':

    parent = ArgumentParser('Simple BPMN App')
    parent.add_argument('dbname', nargs='?', default='spiff.db', metavar='DB', help='Use database %(metavar)s')
    parent.add_argument('-l', '--log-level', dest='log_level', default='WARN', metavar='LEVEL', help='Use log level %(metavar)s')
    args = parent.parse_args()

    with sqlite3.connect(args.dbname) as db:
        SqliteSerializer.initialize(db)

    parser = SpiffBpmnParser()

    registry = SqliteSerializer.configure(SPIFF_CONFIG)
    serializer = SqliteSerializer(args.dbname, registry=registry)

    handlers = {
        UserTask: UserTaskHandler,
        ManualTask: ManualTaskHandler,
        NoneTask: ManualTaskHandler,
    }

    engine = BpmnEngine(parser, serializer, handlers)

    app = curses.wrapper(CursesApp, engine)

