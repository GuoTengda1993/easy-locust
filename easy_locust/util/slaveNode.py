# -*- coding: utf-8 -*-
import re
import logging
import paramiko


class ConnectSlave:

    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password

    def trans_file(self, source, dest):
        trans = paramiko.Transport((self.ip, 22))
        trans.connect(username=self.username, password=self.password)
        ft = paramiko.SFTPClient.from_transport(trans)
        ft.put(localpath=source, remotepath=dest)
        ft.close()

    def remote_command(self, command):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self.ip, port=22, username=self.username, password=self.password)
        stdin, stdout, stderr = ssh.exec_command(command)
        error = stderr.read()
        ssh.close()
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

    def get_pid(self, keyword):
        all_pid = self.remote_command('ps -aux')
        pid_list = all_pid.readlines()
        pid = 0
        for each in pid_list:
            if keyword in each:
                pid = re.split('\s+', each)[1]
                break
        return pid


if __name__ == '__main__':
    c = ConnectSlave('192.168.37.130', 'root', '1q2w3e4r5t')
    out = c.remote_command('nohup locust -f /root/PtDemo.py --slave --master-host=192.168.31.189 > /dev/null 2>&1 &')
    print(out.read())
    print(type(out))
