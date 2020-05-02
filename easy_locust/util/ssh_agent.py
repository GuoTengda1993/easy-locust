# -*- coding: utf-8 -*-
import logging
import paramiko


class SSHAgent:

    def __init__(self, ip, username, password, port=22):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        trans = paramiko.Transport((self.ip, self.port))
        trans.connect(username=self.username, password=self.password)
        self.ft = paramiko.SFTPClient.from_transport(trans)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=self.ip, port=self.port, username=self.username, password=self.password)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ssh.close()
        self.ft.close()

    def trans_file(self, source, dest):
        trans = paramiko.Transport((self.ip, self.port))
        trans.connect(username=self.username, password=self.password)
        ft = paramiko.SFTPClient.from_transport(trans)
        ft.put(localpath=source, remotepath=dest)

    def remote_command(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        error = stderr.read()
        if error:
            return False
        return stdout.read().decode('utf-8')

    def check_locust(self):
        res = self.remote_command('locust -h')
        if not res:
            pipit = self.remote_command('pip install locustio')
            if not pipit:
                logging.error('Can not install locustio in this slave: {}'.format(self.ip))
                return False
            else:
                return True
        return True

    def check_boomer_client(self):
        res = self.remote_command('ls -l /root/')
        if 'client_v1' in res:
            return True
        return False

    def close(self):
        self.ft.close()
        self.ssh.close()
