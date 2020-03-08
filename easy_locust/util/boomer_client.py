# -*- coding: utf-8 -*-
from uuid import uuid1
from .extractExcel import *


def gen_boomer_client_json(ptfile):
    boomer_dict = {
        "config": {
            "timeout": 30,
            "disableCompression": False,
            "disableKeepalive": False
        },
        "targets": []
    }
    target = {
            "method": "GET",
            "url": "",
            "postFile": None,
            "contentType": "application/json",
            "verbose": False,
            "weight": 10,
            "name": "test1"
        }
    file_list = []
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
        host, _, _, _, _, _ = pt_data.pt_config()
        pt_api_info = pt_data.pt_api_info()
    else:
        configs = ptfile.get('config')
        host = configs['host']
        pt_api_info = ptfile.get('apis')
    targets = []
    i = 0
    for each_api in pt_api_info:
        i += 1
        if file_type == 'xls':
            weight, pt_url, method, body, _, _ = each_api
        else:
            weight = each_api.get('weight', 100)
            query = each_api.get('query', None)
            if not isinstance(query, dict):
                return "ERROR: query is not dict in json file"
            pt_url = each_api['url'] if query is None else urlunparse(each_api['url'], query)
            method = each_api['method']
            try:
                body = json.dumps(each_api.get('request_data', {}))
            except:
                return "ERROR: request_data should be json format."
        target['method'] = method.upper()
        target['url'] = pt_url if pt_url.startswith('http') else host + pt_url
        target['weight'] = weight
        if method == "GET" or method == "DELETE" or body == "" or body == {}:
            target['postFile'] = None
        else:
            name = 'boomer_' + str(uuid1()) + '.json'
            with open(name, "w") as f:
                if file_type == 'dict':
                    json.dump(body, f)
                else:
                    f.write(body)
            target['postFile'] = name
            file_list.append(name)
        targets.append(target)
    boomer_dict['targets'] = targets
    return boomer_dict, file_list
