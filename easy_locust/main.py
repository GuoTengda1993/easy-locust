import inspect
import logging
import os
import importlib
import signal
import socket
import sys
import time
import configargparse
import re
import gevent
import json
import locust

from locust import events, runners, web
from locust.core import HttpLocust, Locust
from locust.inspectlocust import get_task_ratio_dict, print_task_ratio
from locust.log import console_logger, setup_logging
from locust.runners import LocalLocustRunner, MasterLocustRunner, SlaveLocustRunner
from locust.stats import (print_error_report, print_percentile_stats, print_stats,
                    stats_printer, stats_writer, write_stat_csvs)
from locust.util.timespan import parse_timespan

import shutil
import requests
from threading import Thread
from .util.locustFileFactory import make_locustfile
from .util.slaveNode import ConnectSlave
from .util.extractExcel import PtExcel
from .util.boomer_client import gen_boomer_client_json


_internals = [Locust, HttpLocust]
version = locust.__version__


def parse_options(args=None, default_config_files=['~/.locust.conf','locust.conf']):
    """
    Handle command-line options with configargparse.ArgumentParser.

    Returns a two-tuple of parser + the output from parse_args()
    """
    # Initialize
    parser = configargparse.ArgumentParser(default_config_files=default_config_files, auto_env_var_prefix="LOCUST_", add_env_var_help=False)

    parser.add_argument(
        '-H', '--host',
        help="Host to load test in the following format: http://10.21.32.33"
    )

    parser.add_argument(
        '--web-host',
        default="",
        help="Host to bind the web interface to. Defaults to '' (all interfaces)"
    )
    
    parser.add_argument(
        '-P', '--port', '--web-port',
        type=int,
        default=8089,
        help="Port on which to run web host"
    )
    
    parser.add_argument(
        '-f', '--locustfile',
        default='locustfile',
        help="Python module file to import, e.g. '../other.py'. Default: locustfile"
    )

    # A file that contains the current request stats.
    parser.add_argument(
        '--csv', '--csv-base-name',
        dest='csvfilebase',
        help="Store current request stats to files in CSV format.",
    )

    # Adds each stats entry at every iteration to the _stats_history.csv file.
    parser.add_argument(
        '--csv-full-history',
        action='store_true',
        default=False,
        dest='stats_history_enabled',
        help="Store each stats entry in CSV format to _stats_history.csv file",
    )

    # if locust should be run in distributed mode as master
    parser.add_argument(
        '--master',
        action='store_true',
        help="Set locust to run in distributed mode with this process as master"
    )

    # if locust should be run in distributed mode as slave
    parser.add_argument(
        '--slave',
        action='store_true',
        help="Set locust to run in distributed mode with this process as slave"
    )
    
    # master host options
    parser.add_argument(
        '--master-host',
        default="127.0.0.1",
        help="Host or IP address of locust master for distributed load testing. Only used when running with --slave. Defaults to 127.0.0.1."
    )
    
    parser.add_argument(
        '--master-port',
        type=int,
        default=5557,
        help="The port to connect to that is used by the locust master for distributed load testing. Only used when running with --slave. Defaults to 5557. Note that slaves will also connect to the master node on this port + 1."
    )

    parser.add_argument(
        '--master-bind-host',
        default="*",
        help="Interfaces (hostname, ip) that locust master should bind to. Only used when running with --master. Defaults to * (all available interfaces)."
    )
    
    parser.add_argument(
        '--master-bind-port',
        type=int,
        default=5557,
        help="Port that locust master should bind to. Only used when running with --master. Defaults to 5557. Note that Locust will also use this port + 1, so by default the master node will bind to 5557 and 5558."
    )

    parser.add_argument(
        '--heartbeat-liveness',
        type=int,
        default=3,
        help="set number of seconds before failed heartbeat from slave"
    )

    parser.add_argument(
        '--heartbeat-interval',
        type=int,
        default=1,
        help="set number of seconds delay between slave heartbeats to master"
    )

    parser.add_argument(
        '--expect-slaves',
        type=int,
        default=1,
        help="How many slaves master should expect to connect before starting the test (only when --no-web used)."
    )

    # if we should print stats in the console
    parser.add_argument(
        '--no-web',
        action='store_true',
        help="Disable the web interface, and instead start running the test immediately. Requires -c and -t to be specified."
    )

    # Number of clients
    parser.add_argument(
        '-c', '--clients',
        type=int,
        dest='num_clients',
        default=1,
        help="Number of concurrent Locust users. Only used together with --no-web"
    )

    # Client hatch rate
    parser.add_argument(
        '-r', '--hatch-rate',
        type=float,
        default=1,
        help="The rate per second in which clients are spawned. Only used together with --no-web"
    )
    
    # Time limit of the test run
    parser.add_argument(
        '-t', '--run-time',
        help="Stop after the specified amount of time, e.g. (300s, 20m, 3h, 1h30m, etc.). Only used together with --no-web"
    )
    
    # skip logging setup
    parser.add_argument(
        '--skip-log-setup',
        action='store_true',
        dest='skip_log_setup',
        default=False,
        help="Disable Locust's logging setup. Instead, the configuration is provided by the Locust test or Python defaults."
    )

    # Enable Step Load mode
    parser.add_argument(
        '--step-load',
        action='store_true',
        help="Enable Step Load mode to monitor how performance metrics varies when user load increases. Requires --step-clients and --step-time to be specified."
    )

    # Number of clients to incease by Step
    parser.add_argument(
        '--step-clients',
        type=int,
        default=1,
        help="Client count to increase by step in Step Load mode. Only used together with --step-load"
    )

    # Time limit of each step
    parser.add_argument(
        '--step-time',
        help="Step duration in Step Load mode, e.g. (300s, 20m, 3h, 1h30m, etc.). Only used together with --step-load"
    )
    
    # log level
    parser.add_argument(
        '--loglevel', '-L',
        default='INFO',
        help="Choose between DEBUG/INFO/WARNING/ERROR/CRITICAL. Default is INFO.",
    )
    
    # log file
    parser.add_argument(
        '--logfile',
        help="Path to log file. If not set, log will go to stdout/stderr",
    )
    
    # if we should print stats in the console
    parser.add_argument(
        '--print-stats',
        action='store_true',
        help="Print stats in the console"
    )

    # only print summary stats
    parser.add_argument(
       '--only-summary',
       action='store_true',
       help='Only print the summary stats'
    )

    parser.add_argument(
        '--no-reset-stats',
        action='store_true',
        help="[DEPRECATED] Do not reset statistics once hatching has been completed. This is now the default behavior. See --reset-stats to disable",
    )

    parser.add_argument(
        '--reset-stats',
        action='store_true',
        help="Reset statistics once hatching has been completed. Should be set on both master and slaves when running in distributed mode",
    )
    
    # List locust commands found in loaded locust files/source files
    parser.add_argument(
        '-l', '--list',
        action='store_true',
        dest='list_commands',
        help="Show list of possible locust classes and exit"
    )
    
    # Display ratio table of all tasks
    parser.add_argument(
        '--show-task-ratio',
        action='store_true',
        help="print table of the locust classes' task execution ratio"
    )
    # Display ratio table of all tasks in JSON format
    parser.add_argument(
        '--show-task-ratio-json',
        action='store_true',
        help="print json data of the locust classes' task execution ratio"
    )
    
    # Version number (optparse gives you --version but we have to do it
    # ourselves to get -V too. sigh)
    parser.add_argument(
        '-V', '--version',
        action='version',
        version='%(prog)s {}'.format(version),
    )

    # set the exit code to post on errors
    parser.add_argument(
        '--exit-code-on-error',
        type=int,
        default=1,
        help="sets the exit code to post on error"
    )

    parser.add_argument(
        '-s', '--stop-timeout',
        action='store',
        type=int,
        dest='stop_timeout',
        default=None,
        help="Number of seconds to wait for a simulated user to complete any executing task before exiting. Default is to terminate immediately. This parameter only needs to be specified for the master process when running Locust distributed."
    )

    parser.add_argument(
        'locust_classes',
        nargs='*',
        metavar='LocustClass',
    )

    # New feature / Easy-Locust
    parser.add_argument(
        '--demo',
        action='store_true',
        dest='demo',
        default=False,
        help='Generate Excel demo file in current folder'
    )

    parser.add_argument(
        '--xf', '--locustfile-xls',
        dest='xlsfile',
        help="XLS file or JSON file, and this file will be transformed to *.py Default: locustfile"
    )

    parser.add_argument(
        '-d', '--distribute',
        action='store_true',
        dest='distribute',
        default=False,
        help="Distribute tasks to slaves defined in XLS."
    )

    parser.add_argument(
        '--boomer',
        action='store_true',
        dest='boomer',
        default=False,
        help="Run boomer client in slaves."
    )

    return parser, parser.parse_args(args=args)


def _is_package(path):
    """
    Is the given path a Python package?
    """
    return (
        os.path.isdir(path)
        and os.path.exists(os.path.join(path, '__init__.py'))
    )


def find_locustfile(locustfile):
    """
    Attempt to locate a locustfile, either explicitly or by searching parent dirs.
    """
    # Obtain env value
    names = [locustfile]
    # Create .py version if necessary
    if not (names[0].endswith('.py') and names[0].endswith('.xls')):
        names += [names[0] + '.py']
    # --- Transform Excel to locustfile
    if names[0].endswith('.xls') or names[0].endswith('.json'):
        _f = make_locustfile(names[0])
        if _f.startswith('ERROR:'):
            console_logger.error(_f)
            sys.exit(1)
        names[0] = re.sub('(\.xls)|(\.json)', '.py', names[0])
        with open(names[0], 'w', encoding='utf-8') as f:
            f.writelines(_f)
    # Does the name contain path elements?
    if os.path.dirname(names[0]):
        # If so, expand home-directory markers and test for existence
        for name in names:
            expanded = os.path.expanduser(name)
            if os.path.exists(expanded):
                if name.endswith('.py') or _is_package(expanded):
                    return os.path.abspath(expanded)
    else:
        # Otherwise, start in cwd and work downwards towards filesystem root
        path = os.path.abspath('.')
        while True:
            for name in names:
                joined = os.path.join(path, name)
                if os.path.exists(joined):
                    if name.endswith('.py') or _is_package(joined):
                        return os.path.abspath(joined)
            parent_path = os.path.dirname(path)
            if parent_path == path:
                # we've reached the root path which has been checked this iteration
                break
            path = parent_path
    # Implicit 'return None' if nothing was found


def is_locust(tup):
    """
    Takes (name, object) tuple, returns True if it's a public Locust subclass.
    """
    name, item = tup
    return bool(
        inspect.isclass(item)
        and issubclass(item, Locust)
        and hasattr(item, "task_set")
        and getattr(item, "task_set")
        and not name.startswith('_')
    )


def load_locustfile(path):
    """
    Import given locustfile path and return (docstring, callables).

    Specifically, the locustfile's ``__doc__`` attribute (a string) and a
    dictionary of ``{'name': callable}`` containing all callables which pass
    the "is a Locust" test.
    """

    def __import_locustfile__(filename, path):
        """
        Loads the locust file as a module, similar to performing `import`
        """
        try:
            # Python 3 compatible
            source = importlib.machinery.SourceFileLoader(os.path.splitext(locustfile)[0], path)
            imported = source.load_module()
        except AttributeError:
            # Python 2.7 compatible
            import imp
            imported = imp.load_source(os.path.splitext(locustfile)[0], path)

        return imported

    # Start with making sure the current working dir is in the sys.path
    sys.path.insert(0, os.getcwd())
    # Get directory and locustfile name
    directory, locustfile = os.path.split(path)
    # If the directory isn't in the PYTHONPATH, add it so our import will work
    added_to_path = False
    index = None
    if directory not in sys.path:
        sys.path.insert(0, directory)
        added_to_path = True
    # If the directory IS in the PYTHONPATH, move it to the front temporarily,
    # otherwise other locustfiles -- like Locusts's own -- may scoop the intended
    # one.
    else:
        i = sys.path.index(directory)
        if i != 0:
            # Store index for later restoration
            index = i
            # Add to front, then remove from original position
            sys.path.insert(0, directory)
            del sys.path[i + 1]
    # Perform the import
    imported = __import_locustfile__(locustfile, path)
    # Remove directory from path if we added it ourselves (just to be neat)
    if added_to_path:
        del sys.path[0]
    # Put back in original index if we moved it
    if index is not None:
        sys.path.insert(index + 1, directory)
        del sys.path[0]
    # Return our two-tuple
    locusts = dict(filter(is_locust, vars(imported).items()))
    return imported.__doc__, locusts


# New feature: find locust path
def get_locust_path():
    if 'win' in sys.platform:
        python3_path = os.getenv('PYTHON')
        if not python3_path:
            python3_path = os.getenv('PYTHON3')
        if python3_path:
            if 'python3' in python3_path.lower():
                if 'scripts' in python3_path.lower():
                    locust_path = os.path.join(os.path.dirname(os.path.dirname(python3_path)), 'Lib\\site-packages\\easy_locust\\')
                else:
                    locust_path = os.path.join(python3_path, 'Lib\\site-packages\\easy_locust\\')
        else:
            sys_path = os.getenv('path').split(';')
            for each in sys_path:
                if 'python3' in each.lower() and 'scripts' not in each.lower() and 'site-packages' not in each.lower():
                    python3_path = each
                    break
            locust_path = os.path.join(python3_path, 'Lib\\site-packages\\easy_locust\\')
    elif 'linux' in sys.platform:
        with os.popen('find /usr/local/ -name easy_locust -type d') as lp:
            locust_path = lp.read().strip()
    return locust_path


# New feature: connect slave and distribute task
def pt_slave(ip, username, password, ptfile, ptcommand):
    connect = ConnectSlave(ip, username, password)
    check = connect.check_locust()
    if check:
        dest = '/root/' + ptfile
        connect.trans_file(source=ptfile, dest=dest)
        connect.remote_command(command=ptcommand)
        connect.close()
    else:
        logging.error('Slave {} cannot run locust.'.format(ip))


def pt_slave_boomer(ip, username, password, file_list, command, targets_data):
    connect = ConnectSlave(ip, username, password)
    check = connect.check_boomer_client()
    if check:
        file_list.pop()
    for f in file_list:
        dest = 'client_v1' if 'client_v1' in f else f
        connect.trans_file(source=f, dest=dest)
    api_run = 'http://{}:9999/target'.format(ip)
    api_heartbeat = 'http://{}:9999/heartbeat'.format(ip)
    api_shutdown = 'http://{}:9999/shutdown'.format(ip)
    try:
        requests.get(api_heartbeat)
        requests.get(api_shutdown)
    except requests.exceptions.ConnectionError:
        connect.remote_command(command='chmod a+x client_v1')
        connect.remote_command(command=command)
        time.sleep(1)
    finally:
        connect.close()
        requests.post(api_run, json=targets_data)


def main():
    parser, options = parse_options()

    # setup logging
    if not options.skip_log_setup:
        setup_logging(options.loglevel, options.logfile)

    logger = logging.getLogger(__name__)

    locust_path = get_locust_path()

    if options.demo:
        if not locust_path:
            logger.error('''Cannot locate Python path, make sure it is in right place. If windows add it to sys PATH,
            if linux make sure python is installed in /usr/local/lib/''')
            sys.exit(1)
        pt_demo_path = os.path.join(locust_path, 'demo', 'demo_pressuretest.xls')
        pt_demo_path_json = os.path.join(locust_path, 'demo', 'demo_locustfile.json')
        pt_new_demo = os.path.join(os.getcwd(), 'PtDemo.xls')
        pt_new_demo_json = os.path.join(os.getcwd(), 'demo.json')
        shutil.copyfile(pt_demo_path, pt_new_demo)
        shutil.copyfile(pt_demo_path_json, pt_new_demo_json)
        sys.exit(0)

    if options.xlsfile:
        pt_file = options.xlsfile
        if not (pt_file.endswith('.xls') or pt_file.endswith('.json')):
            logger.error("PressureTest file must be end with '.xls' or '.json' and see --help for available options.")
            sys.exit(1)
        if not os.path.isfile(pt_file):
            logger.error('PressureTest file is not exist, please check it.')
            sys.exit(1)
        _f = make_locustfile(pt_file)
        if _f.startswith('ERROR:'):
            console_logger.error(_f)
            sys.exit(1)
        _fn = re.sub('(\.xls)|(\.json)', '.py', pt_file)
        with open(_fn, 'w', encoding='utf-8') as f:
            f.writelines(_f)
        logger.info('Transform xls/json to locustfile finish.')
        sys.exit(0)

    locustfile = find_locustfile(options.locustfile)

    if not locustfile:
        logger.error("Could not find any locustfile! Ensure file ends in '.py' and see --help for available options.")
        sys.exit(1)

    if locustfile == "locust.py" or locustfile == "locust.xls" or locustfile == "locust.json":
        logger.error("The locustfile must not be named `locust.py` or `locust.xls` or `locust.json`. "
                     "Please rename the file and try again.")
        sys.exit(1)

    docstring, locusts = load_locustfile(locustfile)

    if options.list_commands:
        console_logger.info("Available Locusts:")
        for name in locusts:
            console_logger.info("    " + name)
        sys.exit(0)

    if not locusts:
        logger.error("No Locust class found!")
        sys.exit(1)

    # make sure specified Locust exists
    if options.locust_classes:
        missing = set(options.locust_classes) - set(locusts.keys())
        if missing:
            logger.error("Unknown Locust(s): %s\n" % (", ".join(missing)))
            sys.exit(1)
        else:
            names = set(options.locust_classes) & set(locusts.keys())
            locust_classes = [locusts[n] for n in names]
    else:
        # list() call is needed to consume the dict_view object in Python 3
        locust_classes = list(locusts.values())
    
    if options.show_task_ratio:
        console_logger.info("\n Task ratio per locust class")
        console_logger.info( "-" * 80)
        print_task_ratio(locust_classes)
        console_logger.info("\n Total task ratio")
        console_logger.info("-" * 80)
        print_task_ratio(locust_classes, total=True)
        sys.exit(0)
    if options.show_task_ratio_json:
        from json import dumps
        task_data = {
            "per_class": get_task_ratio_dict(locust_classes), 
            "total": get_task_ratio_dict(locust_classes, total=True)
        }
        console_logger.info(dumps(task_data))
        sys.exit(0)
    
    if options.run_time:
        if not options.no_web:
            logger.error("The --run-time argument can only be used together with --no-web")
            sys.exit(1)
        if options.slave:
            logger.error("--run-time should be specified on the master node, and not on slave nodes")
            sys.exit(1)
        try:
            options.run_time = parse_timespan(options.run_time)
        except ValueError:
            logger.error("Valid --run-time formats are: 20, 20s, 3m, 2h, 1h20m, 3h30m10s, etc.")
            sys.exit(1)
        def spawn_run_time_limit_greenlet():
            logger.info("Run time limit set to %s seconds" % options.run_time)
            def timelimit_stop():
                logger.info("Time limit reached. Stopping Locust.")
                runners.locust_runner.quit()
            gevent.spawn_later(options.run_time, timelimit_stop)

    if options.step_time:
        if not options.step_load:
            logger.error("The --step-time argument can only be used together with --step-load")
            sys.exit(1)
        if options.slave:
            logger.error("--step-time should be specified on the master node, and not on slave nodes")
            sys.exit(1)
        try:
            options.step_time = parse_timespan(options.step_time)
        except ValueError:
            logger.error("Valid --step-time formats are: 20, 20s, 3m, 2h, 1h20m, 3h30m10s, etc.")
            sys.exit(1)
    
    if options.master:
        # Add -d for automatically run slaves
        if options.distribute:
            ptpy = locustfile
            if options.locustfile.endswith('.xls'):
                _type = 'xls'
                pt_s = PtExcel(options.locustfile)
                master_ip, pt_slave_info = pt_s.pt_slave()
            else:
                _type = 'dict'
                with open(options.locustfile, 'r') as f:
                    _d = json.load(f, encoding='utf-8')
                master_ip = _d.get('master_ip')
                pt_slave_info = _d.get('slaves')
            if master_ip == '':
                logger.error('master IP cannot be None if you use --distribute')
                sys.exit(1)
            if options.boomer:
                locust_cli_slave = 'nohup ./client_v1 --web --master-host={masteIP} > /dev/null 2>&1 &'.format(masteIP=master_ip)
                targets_dict, file_list = gen_boomer_client_json(options.locustfile)
                boomer_client_file = os.path.join(locust_path, 'boomer_client', 'client_v1')
                file_list.append(boomer_client_file)
                thread_pool = []
                try:
                    for slave in pt_slave_info:
                        if _type == 'xls':
                            slave_ip, slave_username, slave_password = slave
                        else:
                            slave_ip, slave_username, slave_password = slave['ip'], slave['username'], slave['password']
                        _t = Thread(target=pt_slave_boomer,
                                    args=(slave_ip, slave_username, slave_password, file_list, locust_cli_slave, targets_dict))
                        logger.info('Prepare slave {}'.format(slave_ip))
                        thread_pool.append(_t)
                        _t.start()
                    for each_t in thread_pool:
                        each_t.join()
                    file_list.pop()
                    for each in file_list:
                        os.remove(each)
                except KeyboardInterrupt:
                    pass
                except Exception as e:
                    logger.error('Something happened, collect Exceptions here: {}'.format(e))
            else:
                try:
                    locust_cli_slave = 'nohup locust -f /root/{locustfile} --slave --master-host={masteIP} > /dev/null 2>&1 &'.format(
                        locustfile=ptpy, masteIP=master_ip)
                    thread_pool = []
                    for slave in pt_slave_info:
                        if _type == 'xls':
                            slave_ip, slave_username, slave_password = slave
                        else:
                            slave_ip, slave_username, slave_password = slave['ip'], slave['username'], slave['password']
                        _t = Thread(target=pt_slave,
                                    args=(slave_ip, slave_username, slave_password, ptpy, locust_cli_slave))
                        logger.info('Prepare slave {}'.format(slave_ip))
                        thread_pool.append(_t)
                        _t.start()
                    for each_t in thread_pool:
                        each_t.join()
                except KeyboardInterrupt:
                    pass
                except Exception as e:
                    logger.error('Something happened, collect Exceptions here: {}'.format(e))

        runners.locust_runner = MasterLocustRunner(locust_classes, options)
    elif options.slave:
        try:
            runners.locust_runner = SlaveLocustRunner(locust_classes, options)
        except socket.error as e:
            logger.error("Failed to connect to the Locust master: %s", e)
            sys.exit(-1)
    else:
        runners.locust_runner = LocalLocustRunner(locust_classes, options)
    # main_greenlet is pointing to runners.locust_runner.greenlet by default, it will point the web greenlet later if in web mode
    main_greenlet = runners.locust_runner.greenlet

    if options.no_web:
        if options.master:
            while len(runners.locust_runner.clients.ready) < options.expect_slaves:
                logging.info("Waiting for slaves to be ready, %s of %s connected",
                             len(runners.locust_runner.clients.ready), options.expect_slaves)
                time.sleep(1)
        if options.step_time:
            runners.locust_runner.start_stepload(options.num_clients, options.hatch_rate, options.step_clients, options.step_time)
        elif not options.slave:
            runners.locust_runner.start_hatching(options.num_clients, options.hatch_rate)
            # make locusts are spawned
            time.sleep(1)
    elif not options.slave:
        # spawn web greenlet
        logger.info("Starting web monitor at http://%s:%s" % (options.web_host or "*", options.port))
        main_greenlet = gevent.spawn(web.start, locust_classes, options)

    if options.run_time:
        spawn_run_time_limit_greenlet()

    stats_printer_greenlet = None
    if not options.only_summary and (options.print_stats or (options.no_web and not options.slave)):
        # spawn stats printing greenlet
        stats_printer_greenlet = gevent.spawn(stats_printer)

    if options.csvfilebase:
        gevent.spawn(stats_writer, options.csvfilebase, options.stats_history_enabled)

    def shutdown(code=0):
        """
        Shut down locust by firing quitting event, printing/writing stats and exiting
        """
        logger.info("Shutting down (exit code %s), bye." % code)
        if stats_printer_greenlet is not None:
            stats_printer_greenlet.kill(block=False)
        logger.info("Cleaning up runner...")
        if runners.locust_runner is not None:
            runners.locust_runner.quit()
        logger.info("Running teardowns...")
        events.quitting.fire(reverse=True)
        print_stats(runners.locust_runner.stats, current=False)
        print_percentile_stats(runners.locust_runner.stats)
        if options.csvfilebase:
            write_stat_csvs(options.csvfilebase, options.stats_history_enabled)
        print_error_report()
        sys.exit(code)
    
    # install SIGTERM handler
    def sig_term_handler():
        logger.info("Got SIGTERM signal")
        shutdown(0)
    gevent.signal(signal.SIGTERM, sig_term_handler)
    
    try:
        logger.info("Starting Locust %s" % version)
        main_greenlet.join()
        code = 0
        if len(runners.locust_runner.errors) or len(runners.locust_runner.exceptions):
            code = options.exit_code_on_error
        shutdown(code=code)
    except KeyboardInterrupt as e:
        shutdown(0)
