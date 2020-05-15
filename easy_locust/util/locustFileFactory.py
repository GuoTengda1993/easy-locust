# -*- coding: utf-8 -*-
import re
import logging
from .extractExcel import *


BASIC_IMPORT = '''# -*- coding: utf-8 -*-
import sys
import re
import requests
import logging
import random
from locust.wait_time import between
from locust import TaskSet, HttpLocust, TaskSequence, task, seq_task
from locust.contrib.fasthttp import FastHttpLocust
from requests.packages import urllib3


urllib3.disable_warnings()

'''
BASIC_TOKEN = '''
def get_token(url, body, locate):
    try:
        response = requests.post(url=url, json=body, verify=False)
        l = re.split(':|：', locate)
        if l[0].lower() == ('header' or 'headers'):
            token = response.headers[l[1].strip()]
            return token
        elif l[0].lower() == 'json':
            rep = response.json()
            section = l[1].strip().split('.')
            token = rep
            for x in section:
                try:
                    x = int(x)
                except ValueError:
                    pass
                token = token[x]
            return token
    except KeyError:
        logging.error('Please check your auth info, cannot get correct response.')
        sys.exit(1)
    except Exception as e:
        logging.error(e)
        sys.exit(1)


user_info = {USER_INFO}
'''
BASIC_LAST = '''

class ApiTest({REQUEST_MODE}):
    host = '{HOST}'
    task_set = PressureTest
    wait_time = between({MIN_WAIT}, {MAX_WAIT})
'''
BASIC_MODE = '''
class PressureTest({TASK_MODE}):
'''
MODE_TOKEN_FIRST_TIME = '''
    def setup(self):
        global headers
        headers = []
        for each in user_info:
            UserName, PassWord = each[0], each[1]
            body = {TOKEN_BODY}
            token = get_token(url='{TOKEN_URL}', body=body, locate='{TOKEN_LOCATE}')
            header = @-'Content-Type': '{CONTENT_TYPE}', '{TOKEN_PARAM}': token-@
            headers.append(header)
'''
MODE_TOKEN_NEVER = '''
    def setup(self):
        global headers
        headers = [{"Content-Type": "{CONTENT_TYPE}"}]
'''
MODE_TASKSET_GET = '''
    @task({WEIGHT})
    def test{NUM}(self):
        with self.client.{METHOD}('{URL}', headers=random.choice(headers), {VERIFY}catch_response=True) as resp:
            if resp.status_code == int({EXPECT_CODE}):
                if b'{EXPECT_STR}' not in resp.content:
                    resp.failure('Error: wrong response --  ' + resp.content.decode('utf-8'))
                else:
                    resp.success()
            else:
                resp.failure('Error: wrong status code -- ' + str(resp.status_code))

'''
MODE_TASKSET_POST = '''
    @task({WEIGHT})
    def test{NUM}(self):
        body = {POST_BODY}
        with self.client.{METHOD}('{URL}', json=body, headers=random.choice(headers), {VERIFY}catch_response=True) as resp:
            if resp.status_code == int({EXPECT_CODE}):
                if b'{EXPECT_STR}' not in resp.content:
                    resp.failure('Error: wrong response --  ' + resp.content.decode('utf-8'))
                else:
                    resp.success()
            else:
                resp.failure('Error: wrong status code -- ' + str(resp.status_code))

'''
MODE_TASK_SEQ_GET = '''
    @seq_task({SEQ})
    @task({WEIGHT})
    def test{NUM}(self):
        with self.client.{METHOD}('{URL}', headers=random.choice(headers), {VERIFY}catch_response=True) as resp:
            if resp.status_code == int({EXPECT_CODE}):
                if b'{EXPECT_STR}' not in resp.content:
                    resp.failure('Error: wrong response --  ' + resp.content.decode('utf-8'))
                else:
                    resp.success()
            else:
                resp.failure('Error: wrong status code -- ' + str(resp.status_code))
                
'''
MODE_TASK_SEQ_POST = '''
    @seq_task({SEQ})
    @task({WEIGHT})
    def test{NUM}(self):
        body = {POST_BODY}
        with self.client.{METHOD}('{URL}', json=body, headers=random.choice(headers), {VERIFY}catch_response=True) as resp:
            if resp.status_code == int({EXPECT_CODE}):
                if b'{EXPECT_STR}' not in resp.content:
                    resp.failure('Error: wrong response --  ' + resp.content.decode('utf-8'))
                else:
                    resp.success()
            else:
                resp.failure('Error: wrong status code -- ' + str(resp.status_code))

'''
MODE_TASKSET_GET_NC = '''
    @task({WEIGHT})
    def test{NUM}(self):
        self.client.{METHOD}('{URL}', {VERIFY}headers=random.choice(headers))
'''
MODE_TASKSET_POST_NC = '''
    @task({WEIGHT})
    def test{NUM}(self):
        body = {POST_BODY}
        self.client.{METHOD}('{URL}', json=body, {VERIFY}headers=random.choice(headers))
'''
MODE_TASK_SEQ_GET_NC = '''
    @seq_task({SEQ})
    @task({WEIGHT})
    def test{NUM}(self):
        self.client.{METHOD}('{URL}', {VERIFY}headers=random.choice(headers))                
'''
MODE_TASK_SEQ_POST_NC = '''
    @seq_task({SEQ})
    @task({WEIGHT})
    def test{NUM}(self):
        body = {POST_BODY}
        self.client.{METHOD}('{URL}', json=body, {VERIFY}headers=random.choice(headers))
'''


def make_locustfile(ptfile) -> str:
    if isinstance(ptfile, dict):
        file_type = 'dict'
    elif ptfile.endswith('.xls'):
        file_type = 'xls'
    elif ptfile.endswith('.json'):
        with open(ptfile, 'r') as f:
            ptfile = json.load(f, encoding='utf-8')
        file_type = 'dict'
    if file_type == 'xls':
        pt_data = PtExcel(ptfile)
        token_url, token_body, token_para, token_locate = pt_data.auth_info()
        host, min_wait, max_wait, token_type, run_in_order, request_mode, content_type = pt_data.pt_config()
        pt_api_info = pt_data.pt_api_info()
    else:
        configs = ptfile.get('config')
        host = configs['host']
        min_wait = configs['min_wait']
        max_wait = configs['max_wait']
        request_mode = configs['request_mode']
        token_type = configs['get_token']
        run_in_order = configs['run_in_order']
        content_type = configs['content_type']
        if request_mode not in ['FastHttpLocust', 'HttpLocust']:
            return "ERROR: request_mode must be HttpLocust or FastHttpLocust"
        if token_type:
            auth = ptfile.get('auth')
            token_url = auth['token_url']
            token_body = auth['body']
            token_para = auth['key']
            token_locate = auth['token_index']
        else:
            token_url, token_body, token_para, token_locate = None, None, None, None

        pt_api_info = ptfile.get('apis')

    if 'UserName' in token_body and 'PassWord' in token_body:
        user_infos = pt_data.pt_user_info() if file_type == 'xls' else ptfile.get('user_info')
    else:
        user_infos = [[None, None]]

    locustfile = BASIC_IMPORT.format(USER_INFO=str(user_infos))

    if str(run_in_order) == '0' or run_in_order == 'FALSE' or run_in_order is False:
        locustfile += BASIC_MODE.format(TASK_MODE='TaskSet')
        if token_type == 'YES' or token_type is True:
            locustfile += BASIC_TOKEN
            locustfile += MODE_TOKEN_FIRST_TIME.format(TOKEN_URL=token_url,
                                                       TOKEN_BODY=token_body,
                                                       TOKEN_LOCATE=token_locate,
                                                       TOKEN_PARAM=token_para,
                                                       CONTENT_TYPE=content_type)
        else:
            locustfile += MODE_TOKEN_NEVER.format(CONTENT_TYPE=content_type)

        if request_mode == 'HttpLocust':
            verify = 'verify=False, '
        else:
            verify = ''
        ii = 0
        for each_api in pt_api_info:
            ii += 1
            if file_type == 'xls':
                weight, pt_url, method, body, expect_code, expect_str = each_api
                if expect_code == '': expect_code = None
                if expect_str == '': expect_str = ''
            else:
                weight = each_api.get('weight', 100)
                query = each_api.get('query', None)
                if not isinstance(query, dict):
                    return "ERROR: query is not dict in json file"
                pt_url = each_api['url'] if query is None else urlunparse(each_api['url'], query)
                method = each_api['method']
                body = each_api['request_data']
                expect_code = each_api.get('expect_status_code', None)
                expect_str = each_api.get('expect_str', '')
            method = method.lower()
            if method == 'get' or method == 'delete' or method == 'head' or method == 'options':
                if expect_code:
                    locustfile += MODE_TASKSET_GET.format(WEIGHT=weight, NUM=ii, METHOD=method, URL=pt_url,
                                                          EXPECT_CODE=expect_code,
                                                          EXPECT_STR=expect_str, VERIFY=verify)
                else:
                    locustfile += MODE_TASKSET_GET_NC.format(WEIGHT=weight, NUM=ii, METHOD=method, URL=pt_url,
                                                             VERIFY=verify)
            else:
                if expect_code:
                    locustfile += MODE_TASKSET_POST.format(WEIGHT=weight, NUM=ii, POST_BODY=body,
                                                           METHOD=method, URL=pt_url,
                                                           EXPECT_CODE=expect_code,
                                                           EXPECT_STR=expect_str, VERIFY=verify
                                                           )
                else:
                    locustfile += MODE_TASKSET_POST_NC.format(WEIGHT=weight, NUM=ii, POST_BODY=body,
                                                              METHOD=method, URL=pt_url, VERIFY=verify)
    else:
        locustfile += BASIC_MODE.format(TASK_MODE='TaskSequence')
        if token_type == 'YES' or token_type is True:
            locustfile += BASIC_TOKEN
            locustfile += MODE_TOKEN_FIRST_TIME.format(TOKEN_URL=token_url,
                                                       TOKEN_BODY=token_body,
                                                       TOKEN_LOCATE=token_locate,
                                                       TOKEN_PARAM=token_para,
                                                       CONTENT_TYPE=content_type)
        else:
            locustfile += MODE_TOKEN_NEVER.format(CONTENT_TYPE=content_type)
        if request_mode == 'HttpLocust':
            verify = 'verify=False, '
        else:
            verify = ''
        ii = 0
        for each_api in pt_api_info:
            ii += 1
            if file_type == 'xls':
                weight, pt_url, method, body, expect_code, expect_str = each_api
                if expect_code == '': expect_code = None
                if expect_str == '': expect_str = ''
            else:
                weight = each_api.get('weight', 100)
                query = each_api.get('query', None)
                if query is not None and not isinstance(query, dict):
                    console_logger.error("query is not dict in json file, query will not be parsed to url.")
                    return None
                pt_url = each_api['url'] if query is None else urlunparse(each_api['url'], query)
                method = each_api['method']
                body = each_api['request_data']
                expect_code = each_api.get('expect_status_code', None)
                expect_str = each_api.get('expect_str', '')
            method = method.lower()
            if method == 'get' or method == 'delete' or method == 'head' or method == 'options':
                if expect_code:
                    locustfile += MODE_TASK_SEQ_GET.format(SEQ=ii, WEIGHT=weight, NUM=ii, METHOD=method, URL=pt_url,
                                                           EXPECT_CODE=expect_code,
                                                           EXPECT_STR=expect_str, VERIFY=verify
                                                           )
                else:
                    locustfile += MODE_TASK_SEQ_GET_NC.format(SEQ=ii, WEIGHT=weight, NUM=ii, METHOD=method,
                                                              URL=pt_url)
            else:
                if expect_code:
                    locustfile += MODE_TASK_SEQ_POST.format(SEQ=ii, WEIGHT=weight, NUM=ii, POST_BODY=body, METHOD=method,
                                                            URL=pt_url, EXPECT_CODE=expect_code, EXPECT_STR=expect_str,
                                                            VERIFY=verify
                                                            )
                else:
                    locustfile += MODE_TASK_SEQ_POST_NC.format(SEQ=ii, WEIGHT=weight, NUM=ii, POST_BODY=body,
                                                               METHOD=method, URL=pt_url, VERIFY=verify)

    locustfile += BASIC_LAST.format(HOST=host, MIN_WAIT=min_wait, MAX_WAIT=max_wait, REQUEST_MODE=request_mode)
    locustfile = locustfile.replace('@-', '{')
    locustfile = locustfile.replace('-@', '}')
    return locustfile


def generate_locust_file(filename):
    _f = make_locustfile(filename)
    if _f.startswith('ERROR:'):
        logging.error(_f)
        return False
    _fn = re.sub('(\.xls)|(\.json)', '.py', filename)
    with open(_fn, 'w', encoding='utf-8') as f:
        f.writelines(_f)
    logging.info('Transform xls/json to locustfile finish.')
    return True
