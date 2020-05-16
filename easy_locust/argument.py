# -*- coding: utf-8 -*-
import os
import sys
import logging
import time

import requests

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
