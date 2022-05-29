#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from requests import Response
from response_wrapper import ResponseWrap
from runner import MyWebDriver
from util import print_exception

# 校验器
class Validator(ResponseWrap):

    def __init__(self, driver: MyWebDriver, res: Response = None):
        super(Validator, self).__init__(driver, res)
        # 校验函数映射
        self.funcs = {
            '=': lambda val, param: val == param,
            '>': lambda val, param: float(val) > param,
            '<': lambda val, param: float(val) < param,
            '>=': lambda val, param: float(val) >= param,
            '<=': lambda val, param: float(val) <= param,
            'contains': lambda val, param: param in val,
            'startswith': lambda val, param: val.startswith(param),
            'endswith': lambda val, param: val.endswith(param),
            'regex_match': lambda val, param: re.search(param, val) != None,
        }

    # 执行校验
    def run(self, config):
        if 'validate_by_jsonpath' in config:
            return self.run_type('jsonpath', config['validate_by_jsonpath'])

        if 'validate_by_xpath' in config:
            return self.run_type('xpath', config['validate_by_xpath'])

        if 'validate_by_css' in config:
            return self.run_type('css', config['validate_by_css'])

    # 执行单个类型的校验
    def run_type(self, type, fields):
        for path, rules in fields:
            # 获得字段值
            val = self._get_val_by(type, path)
            # 校验单个字段
            self.run_field(val, rules)

    # 执行单个字段的校验
    def run_field(self, val, rules):
        # 逐个函数校验
        for func, param in rules.items():
            b = self.run_func(func, val, param)
            if b == False:
                raise Exception(f"不满足校验条件: {val} {func} '{param}'")

    '''
    执行单个函数：就是调用函数
    :param func 函数名
    :param val 校验的值
    :param param 参数
    '''
    def run_func(self, func, val, param):
        if func not in self.funcs:
            print_exception(f'无效校验函数: {func}')
            exit()
        # 调用校验函数
        print(f"处理校验函数: {func}={param}")
        func = self.funcs[func]
        func(val, param)