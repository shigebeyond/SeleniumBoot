from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
server='http://localhost:4723/wd/hub'
desired_caps={
  "platformName": "Android",
  "platformVersion": "9",
  "deviceName": "f978cc97",
  "appPackage": "io.material.catalog",
  "appActivity": "io.material.catalog.main.MainActivity",
  "automationName": "UiAutomator2"
}
driver = webdriver.Remote(server,desired_caps)
time.sleep(5)
el1 = driver.find_element_by_xpath("/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.view.ViewGroup/androidx.recyclerview.widget.RecyclerView/android.widget.FrameLayout[1]/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.ImageView")
el1.click()

wait = WebDriverWait(driver,30)
phone_text = wait.until(EC.presence_of_element_located((By.ID,"com.didi.store:id/et_phone")))
phone_text.send_keys("18345672901")

time.sleep(100000)