#!/usr/bin/python
import time
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from seleniumrequests.request import RequestsSessionMixin
# 整合selenium-requests： https://libraries.io/pypi/selenium-requests
class MyWebDriver(RequestsSessionMixin, webdriver.Chrome):
    pass
# driver = webdriver.Chrome()
driver = MyWebDriver()
'''
#打开浏览器进入登录页面
driver.get("http://admin.jym1.com/login")
#找到账号密码输入框
driver.find_element_by_xpath('//input[@id="input_account"]').send_keys('18877310999')
time.sleep(2)
driver.find_element_by_xpath('//input[@id="input_password"]').send_keys('123456')
time.sleep(2)
#验证码自带，可略过
#点击登录
driver.find_element_by_xpath('//button[@id="login_submit"]').click()
'''

from selenium.webdriver.remote.webdriver import WebDriver
import time

# 提交表单
def submit_form(self, form_data = {}):
    for k, v in form_data.items(): # 设置表单域
        self.find_element_by_name(k).send_keys(v)
    # driver.find_element_by_tag_name('form').submit() # 提交表单 -- 无效
    #driver.find_element_by_xpath('//button[@type="submit"]').click() # 点击提交按钮 -- 有效
    driver.find_element_by_css_selector('button[type=submit]').click() # 点击提交按钮 -- 有效
WebDriver.submit_form = submit_form

# 登录页
driver.get("http://admin.jym1.com/login")
# 提交登录表单
driver.submit_form({
    'account':'18877310999',
    'passwd':'123456',
})

time.sleep(2)

'''
#上次登录时间
login_info = driver.find_element_by_class_name('last-login-time')
cookies = driver.get_cookies()
print(login_info.text)
print(cookies)
'''

'''
url = 'http://admin.jym1.com/goods/goods_service_list'
driver.get(url)
time.sleep(2)
cell = driver.find_element_by_xpath('//table/tbody/tr[1]/td[1]')
print(cell.text)
'''

# 上传图片
url = 'http://admin.jym1.com/upload/common_upload_img/store_img'
file = '/home/shi/fruit.jpeg'
files = {'file': (file, open(file, 'rb'), 'application/json', {'Expires': '0'})}
res = driver.request('POST', url, files=files)
print(res.text)
print(res.json()['data']['url'])

time.sleep(10)
driver.quit()
