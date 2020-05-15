# -*- coding: utf-8 -*-
import os
import sys
import inspect
import importlib
import logging
import time

import requests

from locust.core import HttpLocust, Locust

from .util.ssh_agent import SSHAgent
from .util.locustFileFactory import generate_locust_file


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
        _status = generate_locust_file(names[0])
        if not _status:
            sys.exit(1)
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
    connect = SSHAgent(ip, username, password)
    with connect:
        check = connect.check_locust()
        if check:
            dest = '/root/locust_client.py'
            connect.trans_file(source=ptfile, dest=dest)
            connect.remote_command(command=ptcommand)
        else:
            logging.error('Slave {} cannot run locust.'.format(ip))


def pt_slave_boomer(ip, username, password, file_list, command, targets_data):
    connect = SSHAgent(ip, username, password)
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
