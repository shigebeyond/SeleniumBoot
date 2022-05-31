from selenium import webdriver
from time import sleep

driver = webdriver.Remote(
    command_executor='http://127.0.0.1:4444/wd/hub',
    desired_capabilities={'browserName': 'chrome'}
)

driver.get('https://www.baidu.com')
driver.find_element_by_id("kw").send_keys("docker selenium")
driver.find_element_by_id("su").click()
sleep(1)
driver.quit()