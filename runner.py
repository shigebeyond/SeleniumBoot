#!/usr/bin/python
import time
from util import read_web_steps, print_exception, set_var, replace_var, extract_var
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from seleniumrequests.request import RequestsSessionMixin
# 整合selenium-requests： https://libraries.io/pypi/selenium-requests
class MyWebDriver(RequestsSessionMixin, webdriver.Chrome):
    pass


class Runner(object):

    def __init__(self, driver: MyWebDriver):
        # webdriver
        self.driver = driver
        # 动作映射函数
        self.actions = {
            'sleep': self.sleep,
            'get': self.get,
            'post': self.post,
            'submit_form': self.submit_form,
            'extract_by_xpath': self.extract_by_xpath,
            'extract_by_css': self.extract_by_css,
            'upload': self.upload,
        }

    '''
    执行入口
    :param path 步骤配置文件路径
    '''
    def run(self, path):
        # 获得步骤
        steps = read_web_steps(path)

        # 逐个步骤调用多个动作
        for step in steps:
            for action, param in step.items():
                self.run_action(action, param)

    '''
    执行单个动作：就是调用动作名对应的函数
    :param action 动作名
    :param param 参数
    '''
    def run_action(self, action, param):
        if action not in self.actions:
            print_exception(f'无效动作: {action}')
            exit()
        # 调用动作对应的函数
        print(f"处理动作: {action}={param}")
        func = self.actions[action]
        func(param)

    # --------- 动作处理的函数 --------
    # 睡眠
    def sleep(self, seconds):
        time.sleep(seconds)

    # 跳转
    def get(self, url):
        url = replace_var(url) # 替换变量
        driver.get(url)
        # fix bug: 如果跳到table页，会异步加载，必须等加载完才能解析table，因此等等
        time.sleep(2)

    # post请求
    def post(self, config = {}):
        url = config['url']
        data = config['data']
        for k, v in data.items():
            data[k] = replace_var(v)  # 替换变量
        headers = {}
        if 'is_ajax' in config and config['is_ajax']:
            headers = {
                'X-Requested-With': 'XMLHttpRequest'
            }
        res = self.driver.request('POST', url, headers=headers, data=data)
        print(res.text)
        # 解析响应
        extract_var(config, res)

    # 提交表单
    def submit_form(self, form_data = {}):
        for name, value in form_data.items():
            print(f"替换变量： {name} = {value}")
            value = replace_var(value) # 替换变量
            try:
                ele = self.driver.find_element_by_name(name)
            except Exception as ex:  # 找不到元素
                print_exception(f"找不到表单域{name}")
                print_exception(str(ex))
                continue
            # 设置表单域
            # hidden input调用send_keys()报错：selenium.common.exceptions.ElementNotInteractableException: Message: element not interactable
            # https://www.cnblogs.com/qican/p/14037564.html
            if ele.tag_name == 'select':
                js = f"$('select[name={name}]')[0].selectedIndex = '{value}'"
                self.driver.execute_script(js)
            elif ele.get_attribute('type') == "hidden":
                js = f"$('input[name={name}]').val('{value}')"
                self.driver.execute_script(js)
            else:
                ele.send_keys(value)

        # 去掉require检查
        js = '$("[lay-verify]").removeAttr("lay-verify")'
        self.driver.execute_script(js)

        # self.driver.find_element_by_tag_name('form').submit() # 提交表单 -- 无效
        #self.driver.find_element_by_xpath('//button[@type="submit"]').click() # 点击提交按钮 -- 有效
        # 可以是 input[type=submit] 或 button[type=submit]
        self.driver.find_element_by_css_selector('[type=submit]').click() # 点击提交按钮 -- 有效

    # 提取 xpath 的元素值为变量
    def extract_by_xpath(self, var2path = {}):
        for var, path in var2path.items():  # 设置表单域
            val = self.driver.find_element_by_xpath(path).text
            set_var(var, val)

    # 提取 css selector 的元素值为变量
    def extract_by_css(self, var2path = {}):
        for var, path in var2path.items():  # 设置表单域
            val = self.driver.find_element_by_css_selector(path).text
            set_var(var, val)

    # 上传文件
    def upload(self, config = {}):
        # 上传请求
        url = config['url']
        file = config['file']
        files = {'file': (file, open(file, 'rb'), 'application/json', {'Expires': '0'})}
        res = self.driver.request('POST', url, files=files)
        # 解析响应
        extract_var(config, res)

if __name__ == '__main__':
    # 浏览器
    #driver = webself.driver.Chrome()
    driver = MyWebDriver()
    runner = Runner(driver)
    runner.run('step.yml')
    driver.quit()