#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import sys
import os
from util import read_yaml, print_exception, set_var, replace_var
from validator import Validator
from extractor import Extractor
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from seleniumrequests.request import RequestsSessionMixin
# 整合selenium-requests -- https://libraries.io/pypi/selenium-requests
class MyWebDriver(RequestsSessionMixin, webdriver.Chrome):
    pass

# selenium基于yaml的执行器
class Runner(object):

    def __init__(self, driver: MyWebDriver):
        # webdriver
        self.driver = driver
        # 动作映射函数
        self.actions = {
            'sleep': self.sleep,
            'goto': self.goto,
            'get': self.get,
            'post': self.post,
            'upload': self.upload,
            'submit_form': self.submit_form,
            'input_by_name': self.input_by_name,
            'input_by_css': self.input_by_css,
            'input_by_xpath': self.input_by_xpath,
            'click_by_css': self.click_by_css,
            'click_by_xpath': self.click_by_xpath,
        }

    '''
    执行入口
    :param step_file 步骤配置文件路径
    '''
    def run(self, step_file):
        # 获得步骤
        steps = read_yaml(step_file)

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

    # 解析响应
    def _analyze_response(self, res, config):
        # 校验器
        v = Validator(self.driver, res)
        v.run(config)
        # 提取器
        e = Extractor(self.driver, res)
        e.run(config)

    # 跳转
    def goto(self, config = {}):
        url = config['url']
        url = replace_var(url) # 替换变量
        driver.get(url)
        # fix bug: 如果跳到table页，会异步加载，必须等加载完才能解析table，因此等等
        time.sleep(2)

        # 解析响应
        self._analyze_response(None, config)

    # get请求
    def get(self, config = {}):
        url = config['url']
        headers = {}
        if 'is_ajax' in config and config['is_ajax']:
            headers = {
                'X-Requested-With': 'XMLHttpRequest'
            }
        res = self.driver.request('GET', url, headers=headers)
        # print(res.text)
        # 解析响应
        self._analyze_response(res, config)

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
        # print(res.text)
        # 解析响应
        self._analyze_response(res, config)

    # 上传文件
    def upload(self, config = {}):
        # 上传请求
        url = config['url']
        files = {}
        for name, path in config['files'].items():
            files[name] = open(path, 'rb')
        res = self.driver.request('POST', url, files=files)
        # 解析响应
        self._analyze_response(res, config)

    # 提交表单
    def submit_form(self, input_data = {}):
        # 根据name来填充输入框
        self.input_by_name(input_data)

        # self.driver.find_element_by_tag_name('form').submit() # 提交表单 -- 无效
        #self.driver.find_element_by_xpath('//button[@type="submit"]').click() # 点击提交按钮 -- 有效
        # 可以是 input[type=submit] 或 button[type=submit]
        #self.driver.find_element_by_css_selector('[type=submit]').click() # 点击提交按钮 -- 有效
        self.click_by_css('[type=submit]')

    # 点击按钮
    def click_by_css(self, path):
        self.driver.find_element_by_css_selector(path).click()

    # 点击按钮
    def click_by_xpath(self, path):
        self.driver.find_element_by_xpath(path).click()

    # 根据name来填充输入框
    # :param input_data 表单数据, key是输入框的name, value是填入的值
    def input_by_name(self, input_data):
        return self._input_by_type_and_data('name', input_data)

    # 根据css选择器来填充输入框
    # :param input_data 表单数据, key是输入框的css选择器, value是填入的值
    def input_by_css(self, input_data):
        return self._input_by_type_and_data('css', input_data)

    # 根据xpath来填充输入框
    # :param input_data 表单数据, key是输入框的路径, value是填入的值
    def input_by_xpath(self, input_data):
        return self._input_by_type_and_data('xpath', input_data)

    # 根据类型与数据来填充输入框
    # :param type 选择器的类型:name/css/xpath
    # :param input_data 表单数据, key是输入框的路径, value是填入的值
    def _input_by_type_and_data(self, type, input_data):
        for name, value in input_data.items():
            print(f"替换变量： {name} = {value}")
            value = replace_var(value)  # 替换变量

            # 找到输入框
            try:
                ele = self._find_by(type, name)
            except Exception as ex:  # 找不到元素
                print_exception(f"找不到输入元素{name}")
                print_exception(str(ex))
                continue

            # 设置输入框
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
        # js = '$("[lay-verify]").removeAttr("lay-verify")'
        # self.driver.execute_script(js)

    # 查找元素
    def _find_by(self, type, path):
        if type == 'name':
            return self.driver.find_element_by_name(path)
        if type == 'css':
            return self.driver.find_element_by_css_selector(path)
        if type == 'xpath':
            return self.driver.find_element_by_xpath(path)
        raise Exception(f"不支持查找类型: {type}")

if __name__ == '__main__':
    # 浏览器驱动
    #driver = webself.driver.Chrome()
    driver = MyWebDriver()
    # 基于yaml的执行器
    runner = Runner(driver)
    # 步骤配置的yaml
    if len(sys.argv) > 1:
        step_file = sys.argv[1]
    else:
        step_file = os.getcwd() + '/step.yml'
    # 执行yaml配置的步骤
    runner.run(step_file)
    driver.quit()