import argparse
import json
import logging

def create_arg_parser():

    parser = argparse.ArgumentParser('Simple BPMN runner')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-p', '--process', dest='process', help='The top-level BPMN Process ID')
    group.add_argument('-c', '--collabortion', dest='collaboration', help='The ID of the collaboration')
    parser.add_argument('-b', '--bpmn', dest='bpmn', nargs='+', help='BPMN files to load')
    parser.add_argument('-d', '--dmn', dest='dmn', nargs='*', help='DMN files to load')
    parser.add_argument('-r', '--restore', dest='restore', metavar='FILE',  help='Restore state from %(metavar)s')
    parser.add_argument('-s', '--step', dest='step', action='store_true', help='Display prompt at every step')
    parser.add_argument('-l', '--log-level', dest='log_level', metavar='LEVEL', help='Use log level %(metavar)s', default='WARN')
    return parser

def configure_logging(log_level, filename):

    logging.addLevelName(15, 'DATA')

    def get_logger(name, fmt):
        logger = logging.getLogger(name)
        formatter = logging.Formatter(fmt)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    spiff_log = get_logger('spiff', '%(asctime)s [%(name)s:%(levelname)s] (%(workflow_name)s:%(task_spec)s) %(message)s')
    metrics_log = get_logger('spiff.metrics', '%(asctime)s [%(name)s:%(levelname)s] (%(task_type)s:%(action)s) %(elapsed)2.4f')
    metrics_log.propagate = False

    def log_updates(rec):
        with open(filename, 'a') as fh:
            fh.write(json.dumps({
                'task_id': str(rec.task_id),
                'timestamp': rec.created,
                'data': rec.data,
            }))
            fh.write('\n')
        return 0

    data_log = logging.getLogger('spiff.data')
    data_log.addFilter(log_updates)
    spiff_log.setLevel(log_level)