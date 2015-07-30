import uuid

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from settings import IMAGE_FOLDER


def create_driver():
  return webdriver.Firefox()

def destroy_driver(driver):
  driver.quit()

def handle_alert(driver):
  # Wait for various things to load, and accept an alert if there is one
  try:
    WebDriverWait(browser, 4).until(EC.alert_is_present())
    alert = browser.switch_to_alert()
    alert.accept()
    print "alert accepted"
  except:
    pass
  

def capture_url(driver, url):
  handle_alert(driver)

  imageName = str(uuid.uuid1()) + ".png"
  driver.get(url)

  handle_alert(driver)

  driver.implicitly_wait(2) # got a random thing
  driver.save_screenshot(IMAGE_FOLDER + '/' + imageName)
  return imageName

def set_resolution(driver, x, y):
  handle_alert(driver)
  handle_alert(driver)
  handle_alert(driver)
  handle_alert(driver)
  driver.set_window_size(x, y)

def capture_at_reso(driver, url, x, y):
  handle_alert(driver)
  set_resolution(driver, x, y)
  return capture_url(driver, url)
