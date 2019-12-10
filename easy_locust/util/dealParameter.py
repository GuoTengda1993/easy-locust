# -*- coding: utf-8 -*-
import re


# 将API文档中URL存在“/{***}”的，转换为实际可用来测试的URL
def deal_parameter(string, para):
    paras = re.findall('.*?\$\$(.*?)\$\$', string)  # 正则表达式匹配存在“/{***}”字段的网址
    if paras:
        real_string = string
        for each in paras:
            real_string = real_string.replace('$$'+each+'$$', para[each])
    else:
        real_string = string
    return real_string


if __name__ == '__main__':
    pass
