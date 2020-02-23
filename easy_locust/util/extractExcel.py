# -*- coding: utf-8 -*-
import json
import xlrd
from locust.log import console_logger


def urlunparse(prefix, query):
    if len(query) == 0:
        return prefix
    prefix = prefix + '?'
    for item in query.items():
        segment = item[0] + '=' + item[1] + '&'
        prefix += segment
    return prefix.strip('&')


class PtExcel:

    def __init__(self, filename):
        self.filename = filename
        self.workbook = xlrd.open_workbook(self.filename)

    def pt_config(self):
        pt_sheet = self.workbook.sheet_by_name('PT')
        host = pt_sheet.cell_value(0, 1)

        min_wait = pt_sheet.cell_value(1, 1)
        if min_wait == '':
            min_wait = str(0.3)
        else:
            min_wait = str(float(min_wait))

        max_wait = pt_sheet.cell_value(2, 1)
        if max_wait == '':
            max_wait = str(0.5)
        else:
            max_wait = str(float(max_wait))

        request_mode = pt_sheet.cell_value(3, 1)
        if request_mode == '' or request_mode is None:
            request_mode = 'HttpLocust'

        token_type = pt_sheet.cell_value(4, 1)
        run_in_order = pt_sheet.cell_value(5, 1)
        return host, min_wait, max_wait, token_type, run_in_order, request_mode

    def pt_api_info(self):
        pt_sheet = self.workbook.sheet_by_name('PT')
        nrows = pt_sheet.nrows
        api_list = []
        for i in range(8, nrows):
            weight = str(int(pt_sheet.cell_value(i, 0)))
            pt_url = pt_sheet.cell_value(i, 1)
            method = pt_sheet.cell_value(i, 2)
            query = pt_sheet.cell_value(i, 3).strip()
            if query != '':
                if '\'' in query:
                    query.replace('\'', '"')
                try:
                    query = json.loads(query)
                    pt_url = urlunparse(pt_url, query)
                except json.decoder.JSONDecodeError:
                    console_logger.warning('Query decode error, this will not parse to url: {}'.format(query))
            body = pt_sheet.cell_value(i, 4)
            if '\'' in body:
                body.replace('\'', '"')
            expect_code = pt_sheet.cell_value(i, 5)
            expect_str = pt_sheet.cell_value(i, 6)
            api_list.append([weight, pt_url, method, body, expect_code, expect_str])
        return api_list

    def pt_slave(self):
        pt_sheet = self.workbook.sheet_by_name('Slave')
        master_ip = pt_sheet.cell_value(0, 1)
        nrows = pt_sheet.nrows
        slave_list = []
        for i in range(2, nrows):
            slave_ip = pt_sheet.cell_value(i, 0)
            slave_username = pt_sheet.cell_value(i, 1)
            slave_password = pt_sheet.cell_value(i, 2)
            slave_list.append([slave_ip, slave_username, slave_password])
        return master_ip, slave_list

    def pt_user_info(self):
        pt_sheet = self.workbook.sheet_by_name('UserInfo')
        nrows = pt_sheet.nrows
        user_infos = []
        for i in range(1, nrows):
            username = pt_sheet.cell_value(i, 0)
            password = pt_sheet.cell_value(i, 1)
            user_infos.append([username, password])
        return user_infos

    def auth_info(self):
        auth_sheet = self.workbook.sheet_by_name('AuthInfo')
        token_url = auth_sheet.cell_value(0, 1)
        body = auth_sheet.cell_value(1, 1)
        token_para = auth_sheet.cell_value(2, 0)
        token_locate = auth_sheet.cell_value(2, 1)
        return token_url, body, token_para, token_locate
