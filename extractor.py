#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import response_wrapper
from requests import Response
from runner import MyWebDriver
from util import print_exception, set_var

# 抽取器
class Extractor(response_wrapper.ResponseWrap):

    def __init__(self, driver: MyWebDriver, res: Response = None):
        super(Extractor, self).__init__(driver, res)

    # 抽取参数
    def run(self, config):
        if 'extract_by_jsonpath' in config:
            return self.run_type('jsonpath', config['extract_by_jsonpath'])

        if 'extract_by_xpath' in config:
            return self.run_type('xpath', config['extract_by_xpath'])

        if 'extract_by_css' in config:
            return self.run_type('css', config['extract_by_css'])

    # 执行单个类型的抽取
    def run_type(self, type, fields):
        for var, path in fields.items():
            # 获得字段值
            val = self._get_val_by(type, path)
            # 抽取单个字段
            set_var(var, val)
            print(f"从响应中抽取参数: {var}={val}")

