# -*- coding: utf-8 -*-
from .extractExcel import *


BASIC_IMPORT = '''# -*- coding: utf-8 -*-
import sys
import re
import requests
import logging
import random
from locust import TaskSet, HttpLocust, TaskSequence, task, seq_task
from requests.packages import urllib3


urllib3.disable_warnings()


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

class ApiTest(HttpLocust):
    host = '{HOST}'
    task_set = PressureTest
    min_wait = {MIN_WAIT}
    max_wait = {MAX_WAIT}
    stop_timeout = {STOP_TIMEOUT}
'''
BASIC_MODE = '''
class PressureTest({TASK_MODE}):
'''
MODE_TOKEN_FIRST_TIME = '''
    def setup(self):
        global headers
        headers = []
        if len(user_info) == 0:
            body = {TOKEN_BODY}
            token = get_token(url='{TOKEN_URL}', body=body, locate='{TOKEN_LOCATE}')
            header = @-'Content-Type': 'application/json', '{TOKEN_PARAM}': token-@
            headers.append(header)
        else:
            for each in user_info:
                UserName, PassWord = each[0], each[1]
                body = {TOKEN_BODY}
                token = get_token(url='{TOKEN_URL}', body=body, locate='{TOKEN_LOCATE}')
                header = @-'Content-Type': 'application/json', '{TOKEN_PARAM}': token-@
                headers.append(header)
'''
MODE_TOKEN_NEVER = '''
    def setup(self):
        global headers
        headers = [{"Content-Type": "application/json"}]
'''
MODE_TASKSET_GET = '''
    @task({WEIGHT})
    def test{NUM}(self):
        query = {QUERY}
        with self.client.{METHOD}('{URL}', headers=random.choice(headers), params=query, verify=False, catch_response=True) as resp:
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
        query = {QUERY}
        body = {POST_BODY}
        with self.client.{METHOD}('{URL}', json=body, headers=random.choice(headers), params=query, verify=False, catch_response=True) as resp:
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
        query = {QUERY}
        with self.client.{METHOD}('{URL}', headers=random.choice(headers), params=query, verify=False, catch_response=True) as resp:
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
        query = {QUERY}
        body = {POST_BODY}
        with self.client.{METHOD}('{URL}', json=body, headers=random.choice(headers), params=query, verify=False, catch_response=True) as resp:
            if resp.status_code == int({EXPECT_CODE}):
                if b'{EXPECT_STR}' not in resp.content:
                    resp.failure('Error: wrong response --  ' + resp.content.decode('utf-8'))
                else:
                    resp.success()
            else:
                resp.failure('Error: wrong status code -- ' + str(resp.status_code))

'''
MODE_TASKSET_GET_TOKEN = '''
    @task({WEIGHT})
    def test{NUM}(self):
        UserName, PassWord = random.choice(user_info)
        body = {TOKEN_BODY}
        token = get_token(url='{TOKEN_URL}', body=body, locate='{TOKEN_LOCATE}')
        headers = @-"Content-Type": "application/json", "{TOKEN_PARAM}": token-@
        query = {QUERY}
        with self.client.{METHOD}('{URL}', headers=headers, params=query, verify=False, catch_response=True) as resp:
            if resp.status_code == int({EXPECT_CODE}):
                if b'{EXPECT_STR}' not in resp.content:
                    resp.failure('Error: wrong response --  ' + resp.content.decode('utf-8'))
                else:
                    resp.success()
            else:
                resp.failure('Error: wrong status code -- ' + str(resp.status_code))
                
'''
MODE_TASKSET_POST_TOKEN = '''
    @task({WEIGHT})
    def test{NUM}(self):
        UserName, PassWord = random.choice(user_info)
        body = {TOKEN_BODY}
        token = get_token(url='{TOKEN_URL}', body=body, locate='{TOKEN_LOCATE}')
        headers = @-"Content-Type": "application/json", "{TOKEN_PARAM}": token-@
        query = {QUERY}
        body = {POST_BODY}
        with self.client.{METHOD}('{URL}', json=body, headers=headers, params=query, verify=False, catch_response=True) as resp:
            if resp.status_code == int({EXPECT_CODE}):
                if b'{EXPECT_STR}' not in resp.content:
                    resp.failure('Error: wrong response --  ' + resp.content.decode('utf-8'))
                else:
                    resp.success()
            else:
                resp.failure('Error: wrong status code -- ' + str(resp.status_code))

'''
MODE_TASK_SEQ_GET_TOKEN = '''
    @seq_task({SEQ})
    @task({WEIGHT})
    def test{NUM}(self):
        UserName, PassWord = random.choice(user_info)
        body = {TOKEN_BODY}
        token = get_token(url='{TOKEN_URL}', body=body, locate='{TOKEN_LOCATE}')
        headers = @-"Content-Type": "application/json", "{TOKEN_PARAM}": token-@
        query = {QUERY}
        with self.client.{METHOD}('{URL}', headers=headers, params=query, verify=False, catch_response=True) as resp:
            if resp.status_code == int({EXPECT_CODE}):
                if b'{EXPECT_STR}' not in resp.content:
                    resp.failure('Error: wrong response --  ' + resp.content.decode('utf-8'))
                else:
                    resp.success()
            else:
                resp.failure('Error: wrong status code -- ' + str(resp.status_code))
                
'''
MODE_TASK_SEQ_POST_TOKEN = '''
    @seq_task({SEQ})
    @task({WEIGHT})
    def test{NUM}(self):
        UserName, PassWord = random.choice(user_info)
        body = {TOKEN_BODY}
        token = get_token(url='{TOKEN_URL}', body=body, locate='{TOKEN_LOCATE}')
        headers = @-"Content-Type": "application/json", "{TOKEN_PARAM}": token-@
        query = {QUERY}
        body = {POST_BODY}
        with self.client.{METHOD}('{URL}', json=body, headers=headers, params=query, verify=False, catch_response=True) as resp:
            if resp.status_code == int({EXPECT_CODE}):
                if b'{EXPECT_STR}' not in resp.content:
                    resp.failure('Error: wrong response --  ' + resp.content.decode('utf-8'))
                else:
                    resp.success()
            else:
                resp.failure('Error: wrong status code -- ' + str(resp.status_code))

'''


def make_locustfile(ptfile):
    pt_data = PtExcel(ptfile)
    token_url, token_body, token_para, token_locate = pt_data.auth_info()
    host, min_wait, max_wait, token_type, run_in_order, stop_timeout = pt_data.pt_config()
    pt_api_info = pt_data.pt_api_info()
    if 'UserName' in token_body and 'PassWord' in token_body:
        user_infos = pt_data.pt_user_info()
    else:
        user_infos = [[None, None]]

    locustfile = BASIC_IMPORT.format(USER_INFO=str(user_infos))

    if str(run_in_order) == '0' or run_in_order == 'FALSE':
        locustfile += BASIC_MODE.format(TASK_MODE='TaskSet')
        if token_type != 'Everytime':
            if token_type == 'JustFistTime':
                locustfile += MODE_TOKEN_FIRST_TIME.format(TOKEN_URL=token_url,
                                                           TOKEN_BODY=token_body,
                                                           TOKEN_LOCATE=token_locate,
                                                           TOKEN_PARAM=token_para)
            else:
                locustfile += MODE_TOKEN_NEVER
            ii = 0
            for each_api in pt_api_info:
                ii += 1
                weight, pt_url, method, query, body, expect_code, expect_str = each_api
                if query == '': query = '{}'
                if body == '': body = '{}'
                if expect_code == '': expect_code = '200'
                if expect_str == '': expect_str = ''
                method = method.lower()
                if method == 'get' or method == 'delete' or method == 'head' or method == 'options':
                    locustfile += MODE_TASKSET_GET.format(WEIGHT=weight, NUM=ii, QUERY=query, METHOD=method, URL=pt_url,
                                                          EXPECT_CODE=expect_code,
                                                          EXPECT_STR=expect_str)
                else:
                    locustfile += MODE_TASKSET_POST.format(WEIGHT=weight, NUM=ii, QUERY=query, POST_BODY=body,
                                                           METHOD=method, URL=pt_url,
                                                           EXPECT_CODE=expect_code,
                                                           EXPECT_STR=expect_str
                                                           )
        else:
            ii = 0
            for each_api in pt_api_info:
                ii += 1
                weight, pt_url, method, query, body, expect_code, expect_str = each_api
                if query == '': query = '{}'
                if body == '': body = '{}'
                if expect_code == '': expect_code = '200'
                if expect_str == '': expect_str = ''
                method = method.lower()
                if method == 'get' or method == 'delete' or method == 'head' or method == 'options':
                    locustfile += MODE_TASKSET_GET_TOKEN.format(WEIGHT=weight, NUM=ii, QUERY=query, METHOD=method, URL=pt_url,
                                                                TOKEN_BODY=token_body,
                                                                TOKEN_URL=token_url,
                                                                TOKEN_LOCATE=token_locate,
                                                                TOKEN_PARAM=token_para,
                                                                EXPECT_CODE=expect_code,
                                                                EXPECT_STR=expect_str
                                                                )
                else:
                    locustfile += MODE_TASKSET_POST_TOKEN.format(WEIGHT=weight, NUM=ii, QUERY=query, POST_BODY=body, METHOD=method,
                                                                 URL=pt_url,
                                                                 TOKEN_BODY=token_body,
                                                                 TOKEN_URL=token_url,
                                                                 TOKEN_LOCATE=token_locate,
                                                                 TOKEN_PARAM=token_para,
                                                                 EXPECT_CODE=expect_code,
                                                                 EXPECT_STR=expect_str
                                                                 )
    else:
        locustfile += BASIC_MODE.format(TASK_MODE='TaskSequence')
        if token_type != 'Everytime':
            if token_type == 'JustFistTime':
                locustfile += MODE_TOKEN_FIRST_TIME.format(TOKEN_URL=token_url,
                                                           TOKEN_BODY=token_body,
                                                           TOKEN_LOCATE=token_locate,
                                                           TOKEN_PARAM=token_para)
            else:
                locustfile += MODE_TOKEN_NEVER
            ii = 0
            for each_api in pt_api_info:
                ii += 1
                weight, pt_url, method, query, body, expect_code, expect_str = each_api
                if query == '': query = '{}'
                if body == '': body = '{}'
                if expect_code == '': expect_code = '200'
                if expect_str == '': expect_str = ''
                method = method.lower()
                if method == 'get' or method == 'delete' or method == 'head' or method == 'options':
                    locustfile += MODE_TASK_SEQ_GET.format(SEQ=ii, WEIGHT=weight, NUM=ii, QUERY=query, METHOD=method, URL=pt_url,
                                                           EXPECT_CODE=expect_code,
                                                           EXPECT_STR=expect_str
                                                           )
                else:
                    locustfile += MODE_TASK_SEQ_POST.format(SEQ=ii, WEIGHT=weight, NUM=ii, QUERY=query, POST_BODY=body, METHOD=method, URL=pt_url,
                                                            EXPECT_CODE=expect_code,
                                                            EXPECT_STR=expect_str
                                                            )
        else:
            ii = 0
            for each_api in pt_api_info:
                ii += 1
                weight, pt_url, method, query, body, expect_code, expect_str = each_api
                if query == '': query = '{}'
                if body == '': body = '{}'
                if expect_code == '': expect_code = '200'
                if expect_str == '': expect_str = ''
                method = method.lower()
                if method == 'get' or method == 'delete' or method == 'head' or method == 'options':
                    locustfile += MODE_TASK_SEQ_GET_TOKEN.format(SEQ=ii, WEIGHT=weight, NUM=ii, QUERY=query, METHOD=method, URL=pt_url,
                                                                 TOKEN_BODY=token_body,
                                                                 TOKEN_URL=token_url,
                                                                 TOKEN_LOCATE=token_locate,
                                                                 TOKEN_PARAM=token_para,
                                                                 EXPECT_CODE=expect_code,
                                                                 EXPECT_STR=expect_str
                                                                 )
                else:
                    locustfile += MODE_TASK_SEQ_POST_TOKEN.format(SEQ=ii, WEIGHT=weight, NUM=ii, QUERY=query, METHOD=method,
                                                                  POST_BODY=body,
                                                                  URL=pt_url,
                                                                  TOKEN_BODY=token_body,
                                                                  TOKEN_URL=token_url,
                                                                  TOKEN_LOCATE=token_locate,
                                                                  TOKEN_PARAM=token_para,
                                                                  EXPECT_CODE=expect_code,
                                                                  EXPECT_STR=expect_str
                                                                  )
    locustfile += BASIC_LAST.format(HOST=host, MIN_WAIT=min_wait, MAX_WAIT=max_wait, STOP_TIMEOUT=stop_timeout)
    locustfile = locustfile.replace('@-', '{')
    locustfile = locustfile.replace('-@', '}')
    l_f = ptfile.replace('.xls', '.py')
    with open(l_f, 'w', encoding='utf-8') as f:
        f.writelines(locustfile)
