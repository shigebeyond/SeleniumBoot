#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from SeleniumBoot.response_wrapper import ResponseWrap
from selenium import webdriver
from requests import Response
from pyutilb.log import log
from pyutilb import BaseValidator

# 校验器
class Validator(BaseValidator, ResponseWrap):

    def __init__(self, driver: webdriver.Chrome, res: Response = None):
        super(Validator, self).__init__(driver, res)

    # 执行校验
    def run(self, config):
        if 'validate_by_jsonpath' in config:
            return self.run_type('jsonpath', config['validate_by_jsonpath'])

        if 'validate_by_xpath' in config:
            return self.run_type('xpath', config['validate_by_xpath'])

        if 'validate_by_css' in config:
            return self.run_type('css', config['validate_by_css'])