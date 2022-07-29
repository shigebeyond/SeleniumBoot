#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import sys
import os
import fnmatch
from pathlib import Path
from pyutilb.util import *
from pyutilb import log, ocr_youdao
import ast
from SeleniumBoot.validator import Validator
from SeleniumBoot.extractor import Extractor
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from seleniumrequests.request import RequestsSessionMixin
# 整合selenium-requests -- https://libraries.io/pypi/selenium-requests
class MyWebDriver(RequestsSessionMixin, Chrome):
    pass

# 跳出循环的异常
class BreakException(Exception):
    def __init__(self, condition):
        self.condition = condition # 跳转条件

# selenium基于yaml的启动器
class Boot(object):

    def __init__(self, driver: MyWebDriver):
        # webdriver
        self.driver = driver
        # 步骤文件所在的目录
        self.step_dir = None
        # 已下载过的url对应的文件，key是url，value是文件
        self.downloaded_files = {}
        # 基础url
        self._base_url = None
        # 当前页面的校验器
        self.validator = Validator(self.driver)
        # 当前页面的提取器
        self.extractor = Extractor(self.driver)
        # 动作映射函数
        self.actions = {
            'sleep': self.sleep,
            'print': self.print,
            'base_url': self.base_url,
            'goto': self.goto,
            'get': self.get,
            'post': self.post,
            'upload': self.upload,
            'download': self.download,
            'download_img_element_by': self.download_img_element_by,
            'download_img_elements_by': self.download_img_elements_by,
            'recognize_captcha': self.recognize_captcha,
            'recognize_captcha_element': self.recognize_captcha_element,
            'submit_form': self.submit_form,
            'input_by_name': self.input_by_name,
            'input_by_css': self.input_by_css,
            'input_by_xpath': self.input_by_xpath,
            'click_by': self.click_by,
            'click_by_if_exist': self.click_by_if_exist,
            'right_click_by': self.right_click_by,
            'double_click_by': self.double_click_by,
            'alert_accept': self.alert_accept,
            'alert_dismiss': self.alert_dismiss,
            'max_window': self.max_window,
            'resize_window': self.resize_window,
            'switch_to_frame_by': self.switch_to_frame_by,
            'switch_to_frame_out': self.switch_to_frame_out,
            'switch_to_window': self.switch_to_window,
            'screenshot': self.screenshot,
            'screenshot_element_by': self.screenshot_element_by,
            'execute_js': self.execute_js,
            'scroll': self.scroll,
            'scroll_top': self.scroll_top,
            'scroll_bottom': self.scroll_bottom,
            'refresh': self.refresh,
            'forward': self.forward,
            'back': self.back,
            'for': self.do_for,
            'once': self.once,
            'break_if': self.break_if,
            'moveon_if': self.moveon_if,
            'moveon_if_exist_by': self.moveon_if_exist_by,
            'break_if_not_exist_by': self.break_if_not_exist_by,
            'include': self.include,
            'set_vars': self.set_vars,
            'print_vars': self.print_vars,
            'validate_by_jsonpath': self.validate_by_jsonpath,
            'validate_by_xpath': self.validate_by_xpath,
            'validate_by_css': self.validate_by_css,
            'extract_by_jsonpath': self.extract_by_jsonpath,
            'extract_by_xpath': self.extract_by_xpath,
            'extract_by_css': self.extract_by_css,
            'extract_by_eval': self.extract_by_eval,
        }
        set_var('boot', self)

    '''
    执行入口
    :param step_files 步骤配置文件或目录的列表
    '''
    def run(self, step_files):
        for path in step_files:
            # 1 模式文件
            if '*' in path:
                dir, pattern = path.rsplit(os.sep, 1)  # 从后面分割，分割为目录+模式
                if not os.path.exists(dir):
                    raise Exception(f'步骤配置目录不存在: {dir}')
                self.run_1dir(dir, pattern)
                return

            # 2 不存在
            if not os.path.exists(path):
                raise Exception(f'步骤配置文件或目录不存在: {path}')

            # 3 目录: 遍历执行子文件
            if os.path.isdir(path):
                self.run_1dir(path)
                return

            # 4 纯文件
            self.run_1file(path)

    # 执行单个步骤目录: 遍历执行子文件
    # :param path 目录
    # :param pattern 文件名模式
    def run_1dir(self, dir, pattern ='*.yml'):
        # 遍历目录: https://blog.csdn.net/allway2/article/details/124176562
        files = os.listdir(dir)
        files.sort() # 按文件名排序
        for file in files:
            if fnmatch.fnmatch(file, pattern): # 匹配文件名模式
                file = os.path.join(dir, file)
                if os.path.isfile(file):
                    self.run_1file(file)

    # 执行单个步骤文件
    # :param step_file 步骤配置文件路径
    # :param include 是否inlude动作触发
    def run_1file(self, step_file, include = False):
        # 获得步骤文件的绝对路径
        if include: # 补上绝对路径
            if not os.path.isabs(step_file):
                step_file = self.step_dir + os.sep + step_file
        else: # 记录目录
            step_file = os.path.abspath(step_file)
            self.step_dir = os.path.dirname(step_file)

        log.debug(f"加载并执行步骤文件: {step_file}")
        # 获得步骤
        steps = read_yaml(step_file)

        steps = read_yaml(step_file)
        try:
            # 执行多个步骤
            self.run_steps(steps)
        except Exception as ex:
            log.debug(f"异常环境:当前步骤文件为 {step_file}, 当前url为 {self.driver.current_url}")
            raise ex

    # 执行多个步骤
    def run_steps(self, steps):
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
        if 'for(' in action:
            n = int(action[4:-1])
            self.do_for(param, n)
            return

        if action not in self.actions:
            raise Exception(f'无效动作: [{action}]')

        # 调用动作对应的函数
        log.debug(f"处理动作: {action}={param}")
        func = self.actions[action]
        func(param)

    # --------- 动作处理的函数 --------
    # for循环
    # :param steps 每个迭代中要执行的步骤
    # :param n 循环次数
    def do_for(self, steps, n = None):
        label = f"for({n})"
        if n == None:
            n = sys.maxsize # 最大int，等于无限循环次数
            label = f"for(∞)"
        log.debug(f"-- 开始循环: {label} -- ")
        try:
            for i in range(n):
                # i+1表示迭代次数比较容易理解
                log.debug(f"第{i+1}次迭代")
                set_var('for_i', i+1)
                self.run_steps(steps)
        except BreakException as e:  # 跳出循环
            log.debug(f"-- 跳出循环: {label}, 跳出条件: {e.condition} -- ")
        else:
            log.debug(f"-- 结束循环: {label} -- ")

    # 执行一次子步骤，相当于 for(1)
    def once(self, steps):
        self.do_for(steps, 1)

    # 检查并继续for循环
    def moveon_if(self, expr):
        # break_if(条件取反)
        self.break_if(f"not ({expr})")

    # 跳出for循环
    def break_if(self, expr):
        val = eval(expr, globals(), bvars)  # 丢失本地与全局变量, 如引用不了json模块
        if bool(val):
            raise BreakException(expr)

    # 检查并继续for循环
    def moveon_if_exist_by(self, config):
        self.break_if_not_exist_by(config)

    # 跳出for循环
    def break_if_not_exist_by(self, config):
        if not self.exist_by_any(config):
            raise BreakException(config)

    # 加载并执行其他步骤文件
    def include(self, step_file):
        self.run_1file(step_file, True)

    # 设置变量
    def set_vars(self, vars):
        for k, v in vars.items():
            v = replace_var(v)  # 替换变量
            set_var(k, v)

    # 打印变量
    def print_vars(self, _):
        log.info(f"打印变量: {bvars}")

    # 睡眠
    def sleep(self, seconds):
        seconds = replace_var(seconds)  # 替换变量
        time.sleep(int(seconds))

    # 打印
    def print(self, msg):
        msg = replace_var(msg)  # 替换变量
        log.debug(msg)

    # 解析响应
    def _analyze_response(self, res, config):
        # 添加固定变量:响应
        set_var('response', res)
        # 校验器
        v = Validator(self.driver, res)
        v.run(config)
        # 提取器
        e = Extractor(self.driver, res)
        e.run(config)

    # 设置基础url
    def base_url(self, url):
        self._base_url = url

    # 拼接url
    def _get_url(self, config):
        url = config['url']
        url = replace_var(url)  # 替换变量
        # 添加基url
        if (self._base_url is not None) and ("http" not in url):
            url = self._base_url + url
        return url

    # 跳转
    # :param config {url, validate_by_jsonpath, validate_by_css, validate_by_xpath, extract_by_jsonpath, extract_by_css, extract_by_xpath, extract_by_eval}
    def goto(self, config = {}):
        url = self._get_url(config)
        driver.get(url)
        # fix bug: 如果跳到table页，会异步加载，必须等加载完才能解析table，因此等等
        time.sleep(2)

        # 解析响应
        self._analyze_response(None, config)

    # get请求
    # :param config {url, is_ajax, data, validate_by_jsonpath, validate_by_css, validate_by_xpath, extract_by_jsonpath, extract_by_css, extract_by_xpath, extract_by_eval}
    def get(self, config = {}):
        url = self._get_url(config)
        data = replace_var(config['data'], False)
        headers = {}
        if 'is_ajax' in config and config['is_ajax']:
            headers = {
                'X-Requested-With': 'XMLHttpRequest'
            }
        res = self.driver.request('GET', url, headers=headers, data=data)
        # log.debug(res.text)
        # 解析响应
        self._analyze_response(res, config)

    # post请求
    # :param config {url, is_ajax, data, validate_by_jsonpath, validate_by_css, validate_by_xpath, extract_by_jsonpath, extract_by_css, extract_by_xpath, extract_by_eval}
    def post(self, config = {}):
        url = self._get_url(config)
        data = replace_var(config['data'], False)
        headers = {}
        if 'is_ajax' in config and config['is_ajax']:
            headers = {
                'X-Requested-With': 'XMLHttpRequest'
            }
        res = self.driver.request('POST', url, headers=headers, data=data)
        # 解析响应
        self._analyze_response(res, config)

    # 上传文件
    # :param config {url, files, validate_by_jsonpath, validate_by_css, validate_by_xpath, extract_by_jsonpath, extract_by_css, extract_by_xpath, extract_by_eval}
    def upload(self, config = {}):
        url = self._get_url(config)
        # 文件
        files = {}
        for name, path in config['files'].items():
            path = replace_var(path)
            files[name] = open(path, 'rb')
        # 发请求
        res = self.driver.request('POST', url, files=files)
        # 解析响应
        self._analyze_response(res, config)

    # 下载文件
    # :param config {url, save_dir, save_file}
    def download(self, config={}):
        url = self._get_url(config)
        # 文件名
        save_file = self._prepare_save_file(config, url)
        # 真正的下载
        self._do_download(url, save_file)
        return save_file

    # 获得文件名
    # config['save_dir'] + config['save_file'] 或 url中的默认文件名
    def _prepare_save_file(self, config, url):
        # 获得保存的目录
        if 'save_dir' in config:
            save_dir = config['save_dir']
        else:
            save_dir = 'downloads'
        # 获得保存的文件名
        if 'save_file' in config:
            save_file = config['save_file']
        else:
            save_file = os.path.basename(url)
        save_file = os.path.abspath(save_dir + os.sep + save_file)  # 转绝对路径
        # 准备目录
        dir, name = os.path.split(save_file)
        if not os.path.exists(dir):
            os.makedirs(dir)
        # 检查重复
        if os.path.exists(save_file):
            for i in range(100000000000000):
                if '.' in save_file:
                    path, ext = save_file.rsplit(".", 1) # 从后面分割，分割为路径+扩展名
                    newname = f"{path}-{i}.{ext}"
                else:
                    newname = f"{save_file}-{i}"
                if not os.path.exists(newname):
                    return newname
            raise Exception('目录太多文件，建议新建目录')

        return save_file

    # 执行下载文件
    def _do_download(self, url, save_file):
        if url in self.downloaded_files:
            return self.downloaded_files[url]

        # 发请求
        res = self.driver.request('GET', url)
        # 保存响应的文件
        write_byte_file(save_file, res.content)
        # 设置变量
        set_var('download_file', save_file)
        self.downloaded_files[url] = save_file
        log.debug(f"下载文件: url为{url}, 另存为{save_file}")
        return save_file

    # 从图片标签中下载图片
    # :param config {css, xpath}
    def download_img_element_by(self, config={}):
        # 获得img标签
        img = self.find_by_any(config)
        # 获得图片url
        url = img.get_attribute('src')

        # 文件名
        save_file = self._prepare_save_file(config, url)
        # 真正的下载
        self._do_download(url, save_file)
        return save_file

    # 从图片标签中下载图片
    # :param config {css, xpath}
    def download_img_elements_by(self, config={}):
        # 获得img标签
        imgs = self.find_all_by_any(config)
        save_files = [] # 记录多个下载图片
        for img in imgs:
            # 获得图片url
            url = img.get_attribute('src')
            # 文件名
            save_file = self._prepare_save_file(config, url)
            # 真正的下载
            self._do_download(url, save_file)
            save_files.append(save_file)
        # 设置变量
        set_var('download_files', save_files)

    # 识别url中的验证码
    def recognize_captcha(self, config={}):
        # 下载图片
        file = self.download(config)
        # 识别验证码
        self._do_recognize_captcha(file)

    # 识别验证码标签中的验证码
    def recognize_captcha_element(self, config={}):
        # 下载图片
        file_path = self.download_img_element_by(config)
        # 识别验证码
        self._do_recognize_captcha(file_path)

    # 真正的识别验证码
    def _do_recognize_captcha(self, file_path):
        # 1 使用 pytesseract 识别图片 -- wrong: 默认没训练过的识别不了
        # img = Image.open(file_path)
        # captcha = pytesseract.image_to_string(img)
        # 2 使用有道ocr
        captcha = ocr_youdao.recognize_text(file_path)
        # 设置变量
        set_var('captcha', captcha)
        log.debug(f"识别验证码: 图片为{file_path}, 验证码为{captcha}")
        # 删除文件
        #os.remove(file)

    # 提交表单
    def submit_form(self, input_data = {}):
        # 根据name来填充输入框
        self.input_by_name(input_data)

        # self.driver.find_element_by_element_name('form').submit() # 提交表单 -- 无效
        #self.driver.find_element_by_xpath('//button[@type="submit"]').click() # 点击提交按钮 -- 有效
        # 可以是 input[type=submit] 或 button[type=submit]
        #self.driver.find_element_by_css_selector('[type=submit]').click() # 点击提交按钮 -- 有效
        self.click_by({'css':'[type=submit]'})

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
            log.debug(f"替换变量： {name} = {value}")
            value = replace_var(value)  # 替换变量

            # 找到输入框
            try:
                ele = self.find_by(type, name)
            except Exception as ex:  # 找不到元素
                print_exception(f"找不到输入元素{name}")
                print_exception(str(ex))
                continue

            if ele.tag_name == 'select': # 设置输入框
                # js = f"$('select[name={name}]')[0].selectedIndex = '{value}'"
                # self.driver.execute_script(js)
                Select(ele).select_by_value(value)
            elif ele.get_attribute('type') == "hidden": # 设置隐藏域
                # hidden input调用send_keys()报错：selenium.common.exceptions.ElementNotInteractableException: Message: element not interactable
                # https://www.cnblogs.com/qican/p/14037564.html
                #js = f"$('input[name={name}]').val('{value}')" # jquery
                js = f"arguments[0].value = '{value}'" # 原生js
                self.driver.execute_script(js, ele)
            else:
                ele.clear() # 先清空
                ele.send_keys(value) # 后输入

    # 根据指定类型，查找元素
    def find_by(self, type, path):
        return self.driver.find_element(type2by(type), path)

    # 根据任一类型，查找元素
    def find_by_any(self, config):
        types = ['id', 'name', 'css', 'xpath']
        for type in types:
            if type in config:
                path = config[type]
                if type == 'xpath': # xpath支持变量
                    path = replace_var(path)
                return self.driver.find_element(type2by(type), path)
        raise Exception(f"没有查找类型: {config}")

    # 根据任一类型，查找元素
    def find_all_by_any(self, config):
        types = ['id', 'name', 'css', 'xpath']
        for type in types:
            if type in config:
                path = config[type]
                return self.driver.find_elements(type2by(type), path)
        raise Exception(f"没有查找类型: {config}")

    # 根据指定类型，检查元素是否存在
    def exist_by(self, type, path):
        try:
            self.find_by(type, path)
            return True
        except NoSuchElementException:
            return False

    # 根据任一类型，检查元素是否存在
    def exist_by_any(self, config):
        try:
            self.find_by_any(config)
            return True
        except NoSuchElementException:
            return False

    # 根据指定类型，查找元素的文本
    def get_text_by(self, type, path):
        ele = self.find_by(type, path)
        return ele.text

    # 根据指定类型，检查元素的文本是否等于
    def check_text_by(self, type, path, txt):
        return self.get_text_by(type, path) == txt

    # 点击按钮
    # :param config {css, xpath}
    def click_by(self, config):
        ele = self.find_by_any(config)
        ele.click()

    # 如果按钮存在，则点击
    # :param config {id, aid, class, xpath}
    def click_by_if_exist(self, config):
        try:
            ele = self.find_by_any(config)
        except:
            ele = None
        if ele != None:
            ele.click()

    # 右击按钮
    # :param config {css, xpath}
    def right_click_by(self, config):
        ele = self.find_by_any(config)
        ActionChains(self.driver).context_click(ele).perform()

    # 双击按钮
    # :param config {css, xpath}
    def double_click_by(self, config):
        ele = self.find_by_any(config)
        ActionChains(self.driver).double_click(ele).perform()

    # 点击弹框的确定按钮
    def alert_accept(self, _):
        self.driver.switch_to.alert.accept()

    # 取消弹框
    def alert_dismiss(self, _):
        self.driver.switch_to.alert.dismiss()

    # 最大化窗口
    def max_window(self, _):
        self.driver.maximize_window()

    # 调整窗口大小
    def resize_window(self, size):
        width, hight = size.split(",", 1)
        self.driver.set_window_size(width, hight)

    # 切换进入iframe
    # :param config {css, xpath}
    def switch_to_frame_by(self, config):
        ele = self.find_by_any(config)
        self.driver.switch_to.frame(ele)

    # 跳回到主框架页
    def switch_to_frame_out(self, _):
        self.driver.switch_to.default_content()

    # 切到第几个窗口
    def switch_to_window(self, window: int):
        handle = self.driver.window_handles[window]
        self.driver.switch_to.window(handle)

    # 整个窗口截图存为png
    # :param config {save_dir, save_file}
    def screenshot(self, config):
        # 文件名
        default_file = str(time.time()).split(".")[0] + ".png"
        save_file = self._prepare_save_file(config, default_file)
        self.driver.save_screenshot(save_file)

    # 对某个标签截图存为png
    # :param config {css, xpath, save_dir, save_file}
    def screenshot_element_by(self, config):
        ele = self.find_by_any(config)
        # 文件名
        default_file = str(time.time()).split(".")[0] + ".png" # 默认文件名
        save_file = self._prepare_save_file(config, default_file)
        ele.screenshot(save_file)

    # 执行js
    def execute_js(self, js, *args):
        self.driver.execute_script(js, *args)

    # 滚动到指定位置
    def scroll(self, pos):
        x, y = pos.split(",", 1)
        self._do_scroll_to(x, y)

    # 滚动到顶部
    def scroll_top(self, _):
        self._do_scroll_to(0, 0)

    # 滚动到底部
    def scroll_bottom(self, _):
        self._do_scroll_to(0, 'document.body.scrollHeight')

    # 滚动到底部
    def _do_scroll_to(self, x, y):
        js = f'window.scrollTo({x}, {y})'
        self.execute_js(js)

    # 滚动到指定元素
    def scroll_to_by(self, config):
        ele = self.find_by_any(config)
        self.execute_js("arguments[0].scrollIntoView(false);", ele)

    # 鼠标移动到指定元素
    def move_to_by(self, config):
        ele = self.find_by_any(config)
        ActionChains(self.driver).move_to_element(ele).perform()

    # 刷新网页
    def refresh(self, _):
        self.driver.refresh()

    # 前进
    def forward(self, _):
        self.driver.forward()

    # 后退
    def back(self, _):
        self.driver.back()

    # 全选 ctrl + a
    def select_all_by(self, config):
        ele = self.find_by_any(config)
        ele.send_keys(Keys.CONTROL, 'a')

    # 复制 ctrl + c
    def copy_by(self, config):
        ele = self.find_by_any(config)
        ele.send_keys(Keys.CONTROL, 'c')

    # 剪切 ctrl + x
    def clip_by(self, config):
        ele = self.find_by_any(config)
        ele.send_keys(Keys.CONTROL, 'x')

    # 粘贴 ctrl + v
    def paste_by(self, config):
        ele = self.find_by_any(config)
        ele.send_keys(Keys.CONTROL, 'v')

    def validate_by_jsonpath(self, fields):
        return self.validator.run_type('jsonpath', fields)

    def validate_by_xpath(self, fields):
        return self.validator.run_type('xpath', fields)

    def validate_by_css(self, fields):
        return self.validator.run_type('css', fields)

    def extract_by_jsonpath(self, fields):
        return self.extractor.run_type('jsonpath', fields)

    def extract_by_xpath(self, fields):
        return self.extractor.run_type('xpath', fields)

    def extract_by_css(self, fields):
        return self.extractor.run_type('css', fields)

    def extract_by_eval(self, fields):
        return self.extractor.run_eval(fields)

# cli入口
def main():
    global driver
    # 浏览器驱动
    option = ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    # driver = Chrome(options=option)
    driver = MyWebDriver(options=option)
    # 基于yaml的执行器
    boot = Boot(driver)
    # 步骤配置的yaml
    if len(sys.argv) > 1:
        step_files = sys.argv[1:]
    else:
        raise Exception("未指定步骤配置文件或目录")
    # 执行yaml配置的步骤
    boot.run(step_files)
    driver.quit()


if __name__ == '__main__':
    main()