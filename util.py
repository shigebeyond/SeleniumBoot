#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import yaml
import re
import random
from jsonpath import jsonpath

# 变量
vars = {}

# 读yaml配置
# :param yaml_file (步骤配置的)yaml文件
def read_yaml(yaml_file):
    file = open(yaml_file, 'r', encoding="utf-8")
    txt = file.read()
    file.close()
    return yaml.load(txt, Loader=yaml.FullLoader)

# 输出异常
def print_exception(ex):
    print('\033[31m发生异常: ' + str(ex) + '\033[0m')

# 设置变量
def set_var(name, val):
    vars[name] = val

# 替换变量： 将 {变量名} 替换为 变量值
def replace_var(txt):
    if isinstance(txt, int) or isinstance(txt, float):
        return txt
    # https://cloud.tencent.com/developer/article/1774589
    def replace(match) -> str:
        name = match.group(1)
        if name.startswith('random_str'):
            len = int(name[10:])
            return random_str(len)
        if name.startswith('random_int'):
            len = int(name[10:])
            return random_int(len)
        if '.' in name: # 有多级属性, 如 data.msg
            return jsonpath(vars, '$.' + name)[0]
        return vars[name]
    txt = re.sub(r'\$([\w\d_]+)', replace, txt) # 处理变量 $msg
    txt = re.sub(r'\$\{([\w\d_\.]+)\}', replace, txt) # 处理变量 ${data.msg}
    return txt

# 生成一个指定长度的随机字符串
def random_str(n):
  random_str =''
  base_str ='ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
  length =len(base_str) -1
  for i in range(n):
    random_str +=base_str[random.randint(0, length)]
  return random_str

# 生成一个指定长度的随机数字
def random_int(n):
  random_str =''
  for i in range(n):
    random_str += str(random.randint(0, 9))
  return random_str