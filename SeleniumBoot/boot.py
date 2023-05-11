#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import sys
import os
import fnmatch
from pathlib import Path
from pyutilb.util import *
from pyutilb.file import *
from pyutilb.cmd import *
from pyutilb import YamlBoot, BreakException, ocr_youdao
from pyutilb.log import log
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


# selenium基于yaml的启动器
class Boot(YamlBoot):

    def __init__(self):
        super().__init__()
        # 动作映射函数
        actions = {
            'close_driver': self.close_driver,
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
            'moveon_if_exist_by': self.moveon_if_exist_by,
            'break_if_exist_by': self.break_if_exist_by,
            'break_if_not_exist_by': self.break_if_not_exist_by,
            'validate_by_jsonpath': self.validate_by_jsonpath,
            'validate_by_xpath': self.validate_by_xpath,
            'validate_by_css': self.validate_by_css,
            'extract_by_jsonpath': self.extract_by_jsonpath,
            'extract_by_xpath': self.extract_by_xpath,
            'extract_by_css': self.extract_by_css,
            'extract_by_eval': self.extract_by_eval,
        }
        self.add_actions(actions)

        # webdriver
        self.driver = None
        # 已下载过的url对应的文件，key是url，value是文件
        self.downloaded_files = {}
        # 基础url
        self._base_url = None

    def run_action(self, action, param):
        return super().run_action(action, param)

    # 执行多个步骤
    def run_steps(self, steps):
        # 延迟初始化driver
        if self.driver == None:
            self.init_driver()

        # 调用父类实现
        super().run_steps(steps)

    # --------- 动作处理的函数 --------
    # 初始化driver
    def init_driver(self, _ = None):
        if self.driver != None:
            return

        # 浏览器驱动
        option = ChromeOptions()
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        # 模拟手机设备 https://blog.csdn.net/qq_38316655/article/details/113739442
        # option.add_experimental_option("mobileEmulation", {"deviceName": "Nexus 5"})
        # self.driver = Chrome(options=option)
        self.driver = MyWebDriver(options=option)
        # 当前页面的校验器, 依赖于driver
        self.validator = Validator(self.driver)
        # 当前页面的提取器, 依赖于driver
        self.extractor = Extractor(self.driver)

    # 关闭driver(浏览器)
    def close_driver(self, _ = None):
        if self.driver != None:
            self.driver.quit()
            self.driver = None

    # 当前url
    @property
    def current_url(self):
        if self.driver == None:
            return None
        return self.driver.current_url

    # 检查并继续for循环
    def moveon_if_exist_by(self, config):
        self.break_if_not_exist_by(config)

    # 跳出for循环
    def break_if_not_exist_by(self, config):
        if not self.exist_by_any(config):
            raise BreakException(config)

    # 跳出for循环
    def break_if_exist_by(self, config):
        if self.exist_by_any(config):
            raise BreakException(config)

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
        self.driver.get(url)
        # fix bug: 如果跳到table页，会异步加载，必须等加载完才能解析table，因此等等
        time.sleep(2)

        # 解析响应
        self._analyze_response(None, config)

    # get请求
    # :param config {url, is_ajax, data, validate_by_jsonpath, validate_by_css, validate_by_xpath, extract_by_jsonpath, extract_by_css, extract_by_xpath, extract_by_eval}
    def get(self, config = {}):
        url = self._get_url(config)
        data = None
        if 'data' in config:
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
            raise Exception('Too many file in save_dir, please change other directory.')

        return save_file

    # 执行下载文件
    def _do_download(self, url, save_file):
        # 忽略base64编码的图片, 如 data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7
        if url.startswith('data:'):
            return
        if url in self.downloaded_files:
            return self.downloaded_files[url]

        # 发请求
        res = self.driver.request('GET', url)
        # 保存响应的文件
        write_byte_file(save_file, res.content)
        # 设置变量
        set_var('download_file', save_file)
        self.downloaded_files[url] = save_file
        log.debug(f"Dowload file: url is %s, save path is %s", url, save_file)
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
        log.debug(f"Recognize captcha: image file is %s, captcha is %s", file_path, captcha)
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
            value = replace_var(value)  # 替换变量

            # 找到输入框
            try:
                ele = self.find_by(type, name)
            except Exception as ex:  # 找不到元素
                log.error(f"Input element not found: %s", name, exc_info = ex)
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
                style = ele.get_attribute('style')
                # 开放隐藏的元素
                mat = re.search(r'display:\s*none;', style)
                if mat != None:
                    style = style.replace(mat.group(), '')
                    #ele.set_attribute('style', style) # 无此方法
                    self.set_attribute(ele, 'style', style)
                ele.clear() # 先清空
                ele.send_keys(value) # 后输入

    # js修改元素的属性值
    def set_attribute(self, ele, name, value):
        self.driver.execute_script("arguments[0].setAttribute(arguments[1],arguments[2])", ele, name, value)

    # js删除元素的属性值
    def remove_attribute(self, ele, name):
        self.driver.execute_script("arguments[0].removeAttribute(arguments[1])", ele, name)

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
        raise Exception(f"Invalid find type: {config}")

    # 根据任一类型，查找元素
    def find_all_by_any(self, config):
        types = ['id', 'name', 'css', 'xpath']
        for type in types:
            if type in config:
                path = config[type]
                return self.driver.find_elements(type2by(type), path)
        raise Exception(f"Invalid find type: {config}")

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
        if config == None: # 默认进入最后一个iframe
            try:
                ele = self.find_by('css', 'iframe:last-child') # 只有一个iframe时报错：NoSuchElementException
            except NoSuchElementException:
                ele = self.find_by('css', 'iframe')
        else:
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
    # https://zhuanlan.zhihu.com/p/525742938
    def scroll_to_by(self, config):
        ele = self.find_by_any(config)
        self.execute_js("arguments[0].scrollIntoView(false);", ele)

    # 鼠标移动到指定元素
    def move_to_by(self, config):
        ele = self.find_by_any(config)
        ActionChains(self.driver).move_to_element(ele).perform()

    # 将元素拖到指定坐标
    def drag_to_by(self, config):
        ele = self.find_by_any(config)
        # ActionChains(self.driver).click_and_hold(ele).move_by_offset(400, 150).release().perform()
        # 等价于
        x, y = config['pos'].split(",", 1)
        ActionChains(self.driver).drag_and_drop_by_offset(ele, x, y).perform()

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
    # 基于yaml的执行器
    boot = Boot()
    # 读元数据：author/version/description
    dir = os.path.dirname(__file__)
    meta = read_init_file_meta(dir + os.sep + '__init__.py')
    # 步骤配置的yaml
    step_files, option = parse_cmd('SeleniumBoot', meta['version'])
    if len(step_files) == 0:
        raise Exception("Miss step config file or directory")
    try:
        # 执行yaml配置的步骤
        boot.run(step_files)
    except Exception as ex:
        log.error(f"Exception occurs: current step file is %s, 当前url为 %s", boot.step_file, boot.current_url, exc_info = ex)
        raise ex
    finally:
        # 关闭浏览器
        if option.autoclose:
            boot.close_driver()

if __name__ == '__main__':
    main()