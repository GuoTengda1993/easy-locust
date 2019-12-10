# -*- coding: utf-8 -*-
import xlrd


class HandleExcel:
    def __init__(self, filename):
        self.filename = filename
        self.workbook = xlrd.open_workbook(self.filename)

    def url_parameter(self):
        url_para_sheet = self.workbook.sheet_by_index(1)
        nrows = url_para_sheet.nrows
        url_para = {}
        for i in range(1, nrows):
            key = url_para_sheet.cell_value(i, 0)
            value = url_para_sheet.cell_value(i, 1)
            if not isinstance(value, str):
                value = str(int(value))
            url_para[key] = value
        return url_para

    def request_parameter(self):
        url_para_sheet = self.workbook.sheet_by_index(2)
        nrows = url_para_sheet.nrows
        req_para = {}
        for i in range(1, nrows):
            key = url_para_sheet.cell_value(i, 0)
            value = url_para_sheet.cell_value(i, 1)
            if not isinstance(value, str):
                value = str(int(value))
            req_para[key] = value
        return req_para

    def auth_info(self):
        auth_sheet = self.workbook.sheet_by_name('AuthInfo')
        token_url = auth_sheet.cell_value(0, 1)
        body = auth_sheet.cell_value(1, 1)
        token_para = auth_sheet.cell_value(2, 0)
        token_locate = auth_sheet.cell_value(2, 1)
        return token_url, body, token_para, token_locate


class PtExcel(HandleExcel):

    def pt_config(self):
        pt_sheet = self.workbook.sheet_by_name('PT')
        host = pt_sheet.cell_value(0, 1)

        min_wait = pt_sheet.cell_value(1, 1)
        if min_wait == '' or isinstance(min_wait, str):
            min_wait = str(300)
        else:
            min_wait = str(int(min_wait))

        max_wait = pt_sheet.cell_value(2, 1)
        if max_wait == '' or isinstance(max_wait, str):
            max_wait = str(500)
        else:
            max_wait = str(int(max_wait))

        stop_timeout = pt_sheet.cell_value(3, 1)
        if stop_timeout == '' or isinstance(stop_timeout, str):
            stop_timeout = str(1000)
        else:
            stop_timeout = str(int(stop_timeout))

        token_type = pt_sheet.cell_value(4, 1)
        run_in_order = pt_sheet.cell_value(5, 1)
        return host, min_wait, max_wait, token_type, run_in_order, stop_timeout

    def pt_api_info(self):
        pt_sheet = self.workbook.sheet_by_name('PT')
        nrows = pt_sheet.nrows
        api_list = []
        for i in range(8, nrows):
            weight = str(int(pt_sheet.cell_value(i, 0)))
            pt_url = pt_sheet.cell_value(i, 1)
            method = pt_sheet.cell_value(i, 2)
            query = pt_sheet.cell_value(i, 3)
            if '\'' in query:
                query.replace('\'', '"')
            body = pt_sheet.cell_value(i, 4)
            if '\'' in body:
                body.replace('\'', '"')
            expect_code = pt_sheet.cell_value(i, 5)
            expect_str = pt_sheet.cell_value(i, 6)
            api_list.append([weight, pt_url, method, query, body, expect_code, expect_str])
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

    def url_parameter(self):
        pass

    def request_parameter(self):
        pass


if __name__ == '__main__':
    test = PtExcel('E:\\Temp\\pt.xls')
    conf = test.pt_config()
    print(conf)
    api = test.pt_api_info()
    for each in api:
        print(each)
