# -*- coding: utf-8 -*-
import os
import sys
import gevent
import logging
import signal
from threading import Thread

from easy_locust.models import Config, Slave, Test
from easy_locust.util.locustFileFactory import generate_locust_file

from locust import runners, events
from locust import web as locust_web
from locust.main import load_locustfile
from locust.runners import LocalLocustRunner
from locust.stats import (print_error_report, print_percentile_stats, print_stats, write_stat_csvs)


class options:
    def __init__(self):
        pass


def config_options():
    config = Config.query.filter_by(id=1).first()
    setattr(options, 'host', config.host)
    setattr(options, 'web_host', '*')
    setattr(options, 'port', config.locust_port)
    setattr(options, 'stats_history_enabled', False)
    setattr(options, 'master-bind-host', '*')
    setattr(options, 'master-bind-port', 5557)
    setattr(options, 'heartbeat-liveness', 3)
    setattr(options, 'heartbeat-interval', 1)
    setattr(options, 'step-load', config.step_load)
    setattr(options, 'step-clients', config.step_clients)
    setattr(options, 'step-time', config.step_time)
    setattr(options, 'stop_timeout', None)
    setattr(options, 'exit_code_on_error', 1)


def generate():
    """
    Generate locust-file, the filename is 'locust_file_by_web.py'
    :return: bool
    """
    config = Config.query.filter_by(id=1).first()
    apis = Test.query.all()
    conf = {
        "host": config.host,
        "min_wait": config.min_wait,
        "max_wait": config.max_wait,
        "request_mode": config.request_mode,
        "get_token": False,
        "run_in_order": False if config.run_in_order == 0 else True,
        "content_type": config.content_type
    }
    api_data = [{
        "weight": api.weight,
        "url": api.url,
        "method": api.method,
        "query": api.query_params,
        "request_data": api.request_data,
        "expect_status_code": api.expect_status_code,
        "expect_str": api.expect_str
    } for api in apis]
    locust_dict = {
        "config": conf,
        "apis": api_data
    }
    return generate_locust_file(locust_dict)


def run_single():
    if not os.path.exists('locust_file_by_web.py'):
        if not generate_locust_file():
            return 'Fail to generate locust-file!'
    docstring, locusts = load_locustfile('locust_file_by_web.py')
    if not locusts:
        return 'No Locust class found in locust_file_by_web.py!'
    locust_classes = list(locusts.values())
    config_options()
    t = Thread(target=run_locust, args=(locust_classes,))
    t.start()


def run_distribute():
    slaves = Slave.query.filter_by(status=1).all()
    pass


def run_locust(locust_classes):
    runners.locust_runner = LocalLocustRunner(locust_classes, options)
    logging.info("Starting web monitor at http://%s:%s" % (options.web_host or "*", options.port))
    main_greenlet = gevent.spawn(locust_web.start, locust_classes, options)
    stats_printer_greenlet = None
    
    def shutdown(code=0):
        """
        Shut down locust by firing quitting event, printing/writing stats and exiting
        """
        logging.info("Shutting down (exit code %s), bye." % code)
        if stats_printer_greenlet is not None:
            stats_printer_greenlet.kill(block=False)
        logging.info("Cleaning up runner...")
        if runners.locust_runner is not None:
            runners.locust_runner.quit()
        logging.info("Running teardowns...")
        events.quitting.fire(reverse=True)
        print_stats(runners.locust_runner.stats, current=False)
        print_percentile_stats(runners.locust_runner.stats)
        if options.csvfilebase:
            write_stat_csvs(options.csvfilebase, options.stats_history_enabled)
        print_error_report()
        sys.exit(code)

    # install SIGTERM handler
    def sig_term_handler():
        logging.info("Got SIGTERM signal")
        shutdown(0)

    gevent.signal_handler(signal.SIGTERM, sig_term_handler)

    try:
        logging.info("Starting Locust...")
        main_greenlet.join()
        code = 0
        lr = runners.locust_runner
        if len(lr.errors) or len(lr.exceptions) or lr.cpu_log_warning():
            code = options.exit_code_on_error
        shutdown(code=code)
    except KeyboardInterrupt:
        shutdown(0)
