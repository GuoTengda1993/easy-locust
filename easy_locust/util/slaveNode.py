# -*- coding: utf-8 -*-
import logging
import paramiko


class ConnectSlave:

    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password
        trans = paramiko.Transport((self.ip, 22))
        trans.connect(username=self.username, password=self.password)
        self.ft = paramiko.SFTPClient.from_transport(trans)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=self.ip, port=22, username=self.username, password=self.password)

    def trans_file(self, source, dest):
        trans = paramiko.Transport((self.ip, 22))
        trans.connect(username=self.username, password=self.password)
        ft = paramiko.SFTPClient.from_transport(trans)
        ft.put(localpath=source, remotepath=dest)

    def remote_command(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        error = stderr.read()
        if error:
            return 0
        else:
            return stdout

    def check_locust(self):
        res = self.remote_command('locust -h')
        if not res:
            pipit = self.remote_command('pip install locustio')
            if not pipit:
                logging.error('Can not install locustio in this slave: {}'.format(self.ip))
                return 0
            else:
                return 1
        else:
            return 1

    def check_boomer_client(self):
        res = self.remote_command('ls -l /root/')
        if b'client_v1' in res.read():
            return 1
        return 0

    def close(self):
        self.ft.close()
        self.ssh.close()
