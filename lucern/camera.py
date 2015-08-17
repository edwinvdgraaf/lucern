import uuid
import os
import threading

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from imagemagick import execute

IMAGE_FOLDER = "data/captures"

def create_driver():
  return webdriver.PhantomJS(service_log_path='/dev/null')


def destroy_driver(driver):
  driver.quit()

def handle_alert(driver):
  # Wait for various things to load, and accept an alert if there is one
  try:
    WebDriverWait(browser, 4).until(EC.alert_is_present())
    alert = browser.switch_to_alert()
    alert.accept()
    logging.warn("Alert accepted")
  except:
    pass
  

def capture_url(driver, url):
  handle_alert(driver)

  imageName = str(uuid.uuid1()) + ".webp"
  driver.get(url)

  handle_alert(driver)

  # make a fifo to temporarily store screenshot so we can convert to webp
  tmppath = "/tmp/lucern-fifo-"+str(uuid.uuid1())

  def convert(path):
    execute(['convert', tmppath, "-define", "webp:lossless=true", IMAGE_FOLDER + '/' + path])

  threading.Thread(target=convert, args = (imageName, )).start()


  os.mkfifo(tmppath)
  driver.save_screenshot(tmppath)

  # remove fifo
  os.remove(tmppath)

  return imageName

def set_resolution(driver, x, y):
  handle_alert(driver)
  handle_alert(driver)
  handle_alert(driver)
  handle_alert(driver)
  driver.set_window_size(x, y)
