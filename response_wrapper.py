#!/usr/bin/python
# -*- coding: utf-8 -*-

from lxml import etree
from requests import Response
from runner import MyWebDriver

# 响应包装器
class ResponseWrap(object):

    def __init__(self, driver: MyWebDriver, res: Response = None):
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
            if self.res != None:
                html = etree.parse(self.res.text, etree.HTMLParser())
                return html.xpath(path).text

            return self.driver.find_element_by_xpath(path).text

        if type == 'jsonpath':
            if self.res != None:
                return self.res.json()

            raise Exception(f"goto的响应不支持查找类型: {type}")

        raise Exception(f"不支持查找类型: {type}")