#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import sys
import os
from ocr import ocr_youdao
from util import read_yaml, print_exception, set_var, replace_var
import extractor
import validator
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from seleniumrequests.request import RequestsSessionMixin
# 整合selenium-requests -- https://libraries.io/pypi/selenium-requests
class MyWebDriver(RequestsSessionMixin, Chrome):
    pass

# selenium基于yaml的执行器
class Runner(object):

    def __init__(self, driver: MyWebDriver):
        # webdriver
        self.driver = driver
        # 已下载过的url对应的文件，key是url，value是文件
        self.downloaded_files = {}
        # 动作映射函数
        self.actions = {
            'sleep': self.sleep,
            'print': self.print,
            'goto': self.goto,
            'get': self.get,
            'post': self.post,
            'upload': self.upload,
            'download': self.download,
            'download_img_tag_by': self.download_img_tag_by,
            'download_img_tags_by': self.download_img_tags_by,
            'recognize_captcha': self.recognize_captcha,
            'recognize_captcha_tag': self.recognize_captcha_tag,
            'submit_form': self.submit_form,
            'input_by_name': self.input_by_name,
            'input_by_css': self.input_by_css,
            'input_by_xpath': self.input_by_xpath,
            'click_by': self.click_by,
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
            'screenshot_tag_by': self.screenshot_tag_by,
            'execute_js': self.execute_js,
            'scroll': self.scroll,
            'scroll_top': self.scroll_top,
            'scroll_bottom': self.scroll_bottom,
            'refresh': self.refresh,
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

    # 打印
    def print(self, msg):
        msg = replace_var(msg)  # 替换变量
        print(msg)

    # 解析响应
    def _analyze_response(self, res, config):
        # 添加固定变量:响应
        set_var('response', res)
        # 校验器
        v = validator.Validator(self.driver, res)
        v.run(config)
        # 提取器
        e = extractor.Extractor(self.driver, res)
        e.run(config)

    # 跳转
    # :param config {url, validate_by_jsonpath, validate_by_css, validate_by_xpath, extract_by_jsonpath, extract_by_css, extract_by_xpath, extract_by_eval}
    def goto(self, config = {}):
        url = config['url']
        url = replace_var(url) # 替换变量
        driver.get(url)
        # fix bug: 如果跳到table页，会异步加载，必须等加载完才能解析table，因此等等
        time.sleep(2)

        # 解析响应
        self._analyze_response(None, config)

    # get请求
    # :param config {url, is_ajax, validate_by_jsonpath, validate_by_css, validate_by_xpath, extract_by_jsonpath, extract_by_css, extract_by_xpath, extract_by_eval}
    def get(self, config = {}):
        url = config['url']
        url = replace_var(url)  # 替换变量
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
    # :param config {url, is_ajax, data, validate_by_jsonpath, validate_by_css, validate_by_xpath, extract_by_jsonpath, extract_by_css, extract_by_xpath, extract_by_eval}
    def post(self, config = {}):
        url = config['url']
        url = replace_var(url)  # 替换变量
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
    # :param config {url, files, validate_by_jsonpath, validate_by_css, validate_by_xpath, extract_by_jsonpath, extract_by_css, extract_by_xpath, extract_by_eval}
    def upload(self, config = {}):
        url = config['url']
        url = replace_var(url)  # 替换变量
        # 文件
        files = {}
        for name, path in config['files'].items():
            files[name] = open(path, 'rb')
        # 发请求
        res = self.driver.request('POST', url, files=files)
        # 解析响应
        self._analyze_response(res, config)

    # 下载文件
    # :param config {url, save_dir, save_file}
    def download(self, config={}):
        url = config['url']
        url = replace_var(url)  # 替换变量
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
        file = open(save_file, 'wb')
        file.write(res.content)
        file.close()
        # 设置变量
        set_var('download_file', save_file)
        self.downloaded_files[url] = save_file
        print(f"下载文件: url为{url}, 另存为{save_file}")
        return save_file

    # 从图片标签中下载图片
    # :param config {css, xpath}
    def download_img_tag_by(self, config={}):
        # 获得img标签
        img = self._find_by_any(config)
        # 获得图片url
        url = img.get_attribute('src')

        # 文件名
        save_file = self._prepare_save_file(config, url)
        # 真正的下载
        self._do_download(url, save_file)
        return save_file

    # 从图片标签中下载图片
    # :param config {css, xpath}
    def download_img_tags_by(self, config={}):
        # 获得img标签
        imgs = self._find_all_by_any(config)
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
    def recognize_captcha_tag(self, config={}):
        # 下载图片
        file_path = self.download_img_tag_by(config)
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
        print(f"识别验证码: 图片为{file_path}, 验证码为{captcha}")
        # 删除文件
        #os.remove(file)

    # 提交表单
    def submit_form(self, input_data = {}):
        # 根据name来填充输入框
        self.input_by_name(input_data)

        # self.driver.find_element_by_tag_name('form').submit() # 提交表单 -- 无效
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
            print(f"替换变量： {name} = {value}")
            value = replace_var(value)  # 替换变量

            # 找到输入框
            try:
                ele = self._find_by(type, name)
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

    # 类型转by
    def type2by(self, type):
        if type == 'id':
            return By.ID
        if type == 'name':
            return By.NAME
        if type == 'css':
            return By.CSS_SELECTOR
        if type == 'xpath':
            return By.XPATH
        raise Exception(f"不支持查找类型: {type}")

    # 根据指定类型，查找元素
    def _find_by(self, type, path):
        return self.driver.find_element(self.type2by(type), path)

    # 根据任一类型，查找元素
    def _find_by_any(self, config):
        types = ['id', 'name', 'css', 'xpath']
        for type in types:
            if type in config:
                path = config[type]
                return self.driver.find_element(self.type2by(type), path)
        raise Exception(f"没有查找类型: {config}")

    # 根据任一类型，查找元素
    def _find_all_by_any(self, config):
        types = ['id', 'name', 'css', 'xpath']
        for type in types:
            if type in config:
                path = config[type]
                return self.driver.find_elements(self.type2by(type), path)
        raise Exception(f"没有查找类型: {config}")

    # 点击按钮
    # :param config {css, xpath}
    def click_by(self, config):
        ele = self._find_by_any(config)
        ele.click()

    # 右击按钮
    # :param config {css, xpath}
    def right_click_by(self, config):
        ele = self._find_by_any(config)
        ActionChains(self.driver).context_click(ele).perform()

    # 双击按钮
    # :param config {css, xpath}
    def double_click_by(self, config):
        ele = self._find_by_any(config)
        ActionChains(self.driver).double_click(ele).perform()

    # 点击弹框的确定按钮
    def alert_accept(self):
        self.driver.switch_to.alert.accept()

    # 取消弹框
    def alert_dismiss(self):
        self.driver.switch_to.alert.dismiss()

    # 最大化窗口
    def max_window(self):
        self.driver.maximize_window()

    # 调整窗口大小
    def resize_window(self, size):
        width, hight = size.split(",", 1)
        self.driver.set_window_size(width, hight)

    # 切换进入iframe
    # :param config {css, xpath}
    def switch_to_frame_by(self, config):
        ele = self._find_by_any(config)
        self.driver.switch_to.frame(ele)

    # 跳回到主框架页
    def switch_to_frame_out(self):
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
    def screenshot_tag_by(self, config):
        ele = self._find_by_any(config)
        # 文件名
        default_file = str(time.time()).split(".")[0] + ".png" # 默认文件名
        save_file = self._prepare_save_file(config, default_file)
        ele.screenshot(save_file)

    # 执行js
    def execute_js(self, js):
        self.driver.execute_script(js)

    # 滚动到指定位置
    def scroll(self, pos):
        x, y = pos.split(",", 1)
        self._do_scroll_to(x, y)

    # 滚动到顶部
    def scroll_top(self):
        self._do_scroll_to(0, 0)

    # 滚动到底部
    def scroll_bottom(self):
        self._do_scroll_to(0, 'document.body.scrollHeight')

    # 滚动到底部
    def _do_scroll_to(self, x, y):
        js = f'window.scrollTo({x}, {y})'
        self.execute_js(js)

    # 刷新网页
    def refresh(self):
        self.driver.refresh()

if __name__ == '__main__':
    # 浏览器驱动
    option = ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    #driver = Chrome(options=option)
    driver = MyWebDriver(options=option)
    # 基于yaml的执行器
    runner = Runner(driver)
    # 步骤配置的yaml
    if len(sys.argv) > 1:
        step_file = sys.argv[1]
    else:
        step_file = os.getcwd() + os.sep + 'step.yml'
    # 执行yaml配置的步骤
    runner.run(step_file)
    driver.quit()