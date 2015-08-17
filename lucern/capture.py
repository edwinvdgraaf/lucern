import logging
from urlparse import urlparse

from camera import create_driver, destroy_driver, set_resolution, capture_url
from database import capturesessions, screenshots

def capture(name, urls, width, dbcon):
  # Selenium driver
  driver = create_driver()

  capturesession_id = dbcon.execute(
    capturesessions.insert().values(
    name=name,
    resolutionX=width)
  ).inserted_primary_key[0]

  browser = dict(map(lambda x: (str(x[0]), str(x[1])), driver.capabilities.iteritems()))

  # capture at height of 50 to hopefully ensure there is a scrollbar (in Firefox)
  set_resolution(driver, width, 50)

  for url in urls:
    if url == '': continue
    
    logging.info('Capturing ' + url)
    
    uuid = capture_url(driver, url)

    # TODO maybe handle root url

    dbcon.execute(
      screenshots.insert().values(
        uuid = uuid,
        url = urlparse(url).path,
        capturesession_id = capturesession_id,
        resolutionX = width,
        browser = browser
      )
    )

  destroy_driver(driver)
