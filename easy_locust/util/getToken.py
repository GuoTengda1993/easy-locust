# -*- coding: utf-8 -*-
import re
import requests


def get_token(url, body, locate):
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
