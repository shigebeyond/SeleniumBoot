#!/usr/bin/python
import time
import yaml
import re
import random
from jsonpath import jsonpath
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from seleniumrequests.request import RequestsSessionMixin
# 整合selenium-requests： https://libraries.io/pypi/selenium-requests
class MyWebDriver(RequestsSessionMixin, webdriver.Chrome):
    pass

# 变量
vars = {}

# 输出异常
def print_exception(ex):
    print('\033[31m发生异常: ' + str(ex) + '\033[0m')

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

# 读web步骤
def read_web_steps():
    file = open('step.yml', 'r', encoding="utf-8")
    txt = file.read()
    file.close()
    return yaml.load(txt, Loader=yaml.FullLoader)

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

# --------- 动作处理 --------
# 睡眠
def sleep(driver, seconds):
    time.sleep(seconds)

# 跳转
def get(driver, url):
    url = replace_var(url) # 替换变量
    driver.get(url)
    # fix bug: 如果跳到table页，会异步加载，必须等加载完才能解析table，因此等等
    time.sleep(2)

# post请求
def post(driver, config = {}):
    url = config['url']
    data = config['data']
    for k, v in data.items():
        data[k] = replace_var(v)  # 替换变量
    headers = {}
    if 'is_ajax' in config and config['is_ajax']:
        headers = {
            'X-Requested-With': 'XMLHttpRequest'
        }
    res = driver.request('POST', url, headers=headers, data=data)
    print(res.text)
    # 解析响应
    extract_var(config, res)

# 提交表单
def submit_form(driver, form_data = {}):
    for name, value in form_data.items():
        print(f"替换变量： {name} = {value}")
        value = replace_var(value) # 替换变量
        try:
            ele = driver.find_element_by_name(name)
        except Exception as ex:  # 找不到元素
            print_exception(f"找不到表单域{name}")
            print_exception(str(ex))
            continue
        # 设置表单域
        # hidden input调用send_keys()报错：selenium.common.exceptions.ElementNotInteractableException: Message: element not interactable
        # https://www.cnblogs.com/qican/p/14037564.html
        if ele.tag_name == 'select':
            js = f"$('select[name={name}]')[0].selectedIndex = '{value}'"
            driver.execute_script(js)
        elif ele.get_attribute('type') == "hidden":
            js = f"$('input[name={name}]').val('{value}')"
            driver.execute_script(js)
        else:
            ele.send_keys(value)

    # 去掉require检查
    js = '$("[lay-verify]").removeAttr("lay-verify")'
    driver.execute_script(js)

    # driver.find_element_by_tag_name('form').submit() # 提交表单 -- 无效
    #driver.find_element_by_xpath('//button[@type="submit"]').click() # 点击提交按钮 -- 有效
    # 可以是 input[type=submit] 或 button[type=submit]
    driver.find_element_by_css_selector('[type=submit]').click() # 点击提交按钮 -- 有效

# 提取 xpath 的元素值为变量
def extract_by_xpath(driver, var2path = {}):
    for var, path in var2path.items():  # 设置表单域
        vars[var] = driver.find_element_by_xpath(path).text

# 提取 css selector 的元素值为变量
def extract_by_css(driver, var2path = {}):
    for var, path in var2path.items():  # 设置表单域
        vars[var] = driver.find_element_by_css_selector(path).text

# 上传文件
def upload(driver, config = {}):
    # 上传请求
    url = config['url']
    file = config['file']
    files = {'file': (file, open(file, 'rb'), 'application/json', {'Expires': '0'})}
    res = driver.request('POST', url, files=files)
    # 解析响应
    extract_var(config, res)

# 动作映射函数
actions = {
    'sleep': sleep,
    'get': get,
    'post': post,
    'submit_form': submit_form,
    'extract_by_xpath': extract_by_xpath,
    'extract_by_css': extract_by_css,
    'upload': upload,
}

if __name__ == '__main__':
    # 浏览器
    #driver = webdriver.Chrome()
    driver = MyWebDriver()

    # 获得步骤
    steps = read_web_steps()

    # 逐个步骤调用多个动作
    for step in steps:
        for action, param in step.items():
            if action not in actions:
                print_exception(f'无效动作: {action}')
                exit()

            # 调用动作对应的函数
            print(f"处理动作: {action}={param}")
            func = actions[action]
            func(driver, param)

    sleep(driver, 100)
    driver.quit()