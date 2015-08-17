import logging
import tempfile
import shutil
import subprocess

from sqlalchemy.sql import select

from database import capturesessions, screenshots
from slugify import slugify
from imagemagick import compare as ccompare

def compare(engine, left, right):
  conn = engine.connect()

  logging.info('Comparing ' + left + ' to ' + right)

  def capture_id(name):
    return conn.execute(
      select([capturesessions]).where(capturesessions.c.name == name)
    ).fetchone()['id']

  def get_screenshots(capturesession_id):
    return conn.execute(
      select([screenshots]).where(screenshots.c.capturesession_id == capturesession_id)
    )

  # from [{url: z, file:y}] and [{url: z, file:x}]
  # to
  # {url: [y, z]}
  def appendmapping(mapping, cid):
    for row in get_screenshots(cid):
      if not row[screenshots.c.url] in mapping:
        mapping[row[screenshots.c.url]] = []
      
      mapping[row[screenshots.c.url]].append(row[screenshots.c.uuid])

  mapping = {}
  appendmapping(mapping, capture_id(left))
  appendmapping(mapping, capture_id(right))

  for url, files in mapping.iteritems():
    # TODO handle missing screenshots
    left_path = 'data/captures/'+files[0]
    right_path = 'data/captures/'+files[0]

    logging.debug(left_path + ' vs ' + right_path)

    code, err = ccompare("-metric", "AE", "-fuzz", "8%",
      left_path, right_path, "data/compares/" + slugify(url) + '.png')
    
    if code is 0:
      logging.info("Images are identical for " + url)
    elif code is 1:
      logging.info("Images are different for " + url)
    else:
      logging.warn(err)
      logging.warn("Error comparing images for " + url + 
        ", files " + left_path + " and " + right_path)

    conn.close()
