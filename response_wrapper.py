#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from lxml import etree
from requests import Response
from selenium import webdriver

# 响应包装器
class ResponseWrap(object):

    def __init__(self, driver: webdriver.Chrome, res: Response = None):
        # webdriver
        self.driver = driver
        # 响应
        self.res = res

    # 获得元素值
    def _get_val_by(self, type, path):
        if type == 'css':
            if self.res != None:
                html = etree.parse(self.res.text, etree.HTMLParser())
                return html.cssselect(path).text

            return self.driver.find_element_by_css_selector(path).text

        if type == 'xpath':
            # 检查xpath是否最后有属性
            mat = re.search('/@[\w\d]+$', path)
            prop = ''
            if (mat != None):  # 有属性
                # 分离元素path+属性
                prop = mat.group()
                path = path.replace(prop, '')
                prop = prop.replace('/@', '')

            if self.res != None:
                html = etree.parse(self.res.text, etree.HTMLParser())
                ele = html.xpath(path)
                if prop != '': # 获得属性
                    return ele.get(prop)
                return ele.text

            ele = self.driver.find_element_by_xpath(path)
            if prop != '': # 获得属性
                return ele.get_attribute(prop)
            return ele.text

        if type == 'jsonpath':
            if self.res != None:
                return self.res.json()

            raise Exception(f"goto的响应不支持查找类型: {type}")

        raise Exception(f"不支持查找类型: {type}")