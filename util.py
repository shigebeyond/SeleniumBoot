#!/usr/bin/python
import time
import yaml
import re
import random
from jsonpath import jsonpath

# 变量
vars = {}

# 读web步骤
def read_web_steps(path):
    file = open(path, 'r', encoding="utf-8")
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
        return vars[name]
    return re.sub(r'\$([\w\d_]+)+', replace, txt)

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

# 从响应中抽取参数
def extract_var(config, res):
    if 'extract_by_jsonpath' in config:
        res = res.json()
        for var, path in config['extract_by_jsonpath'].items():  # json提取器
            val = jsonpath(res, path)[0] # jsonpath 返回的居然是数组
            vars[var] = val
            print(f"从响应中抽取参数: {var}={val}")