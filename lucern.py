import sys
import argparse
import logging
import subprocess
import tempfile
import shutil
from urlparse import urlparse

from sqlalchemy.sql import select

from settings import DB_URL
from lib.camera import create_driver, destroy_driver, capture_at_reso
from lib.database import engine, capturesessions, screenshots


# inspired by https://docs.djangoproject.com/en/1.8/_modules/django/utils/text/#slugify
def slugify(value):
  """
  Converts to ASCII. Converts spaces to hyphens. Removes characters that
  aren't alphanumerics, underscores, or hyphens. Converts to lowercase.
  Also strips leading and trailing whitespace.
  """
  # value = force_text(value)
  import unicodedata, re
  value = re.sub('/', '-', value).strip().lower()
  value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
  value = re.sub('[^\w\s-]', '', value).strip().lower()
  return re.sub('[-\s]+', '-', value)

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger('traxex')
logger.setLevel(logging.DEBUG)


parser = argparse.ArgumentParser(description='Capture and compare web screenshots.')

# http://stackoverflow.com/questions/14660876/python-dependencies-between-groups-using-argparse
group_capture = parser.add_argument_group(title="Capture URLs")
group_capture.add_argument('-n', help="Session name", dest="session")
group_capture.add_argument('-i', type=argparse.FileType('r'), dest='inputurls',
                   help='File containing a list of input URLs')
group_capture.add_argument('-r', help='X resolution (width)', type=int, dest='resolutionX', default=1024)

group_compare = parser.add_argument_group(title="Compare captures")
group_compare.add_argument('-left', help='Capture group left', dest='left')
group_compare.add_argument('-right', help='Capture group right', dest='right')


args = parser.parse_args()

# databae
db = engine
conn = engine.connect()

if args.inputurls != None:
  # selenium driver
  driver = create_driver()

  # input urls list
  urls = args.inputurls.read().split("\n") # TODO remove last line if empty
  
  resolutionX = args.resolutionX

  conn = engine.connect()
  capturesession_id = conn.execute(
    capturesessions.insert().values(
    name=args.session,
    resolutionX=resolutionX)
  ).inserted_primary_key[0]

  browser = dict(map(lambda x: (str(x[0]), str(x[1])), driver.capabilities.iteritems()))

  for url in urls:
    if url == '': continue
    
    logger.info('Capturing ' + url)
    # capture at height of 100 to ensure there is a scrollbar
    uuid = capture_at_reso(driver, url, resolutionX, 100)

    conn.execute(
      screenshots.insert().values(
        uuid = uuid,
        url = urlparse(url).path,
        capturesession_id = capturesession_id,
        resolutionX = resolutionX,
        browser = browser
      )
    )

  destroy_driver(driver)
elif args.left != None:
  logger.info('Comparing ' + args.left + ' to ' + args.right)

  def capture_id(name):
    return conn.execute(
      select([capturesessions]).where(capturesessions.c.name == name)
    ).fetchone()

  def get_screenshots(capturesession_id):
    return conn.execute(
      select([screenshots]).where(screenshots.c.capturesession_id == capturesession_id)
    )

  left_id = capture_id(args.left)
  right_id = capture_id(args.right)

  def append_screenshots(compare, screenshot_id, side='left'):
    for row in get_screenshots(screenshot_id):
      if not row[screenshots.c.url] in compare: compare[row[screenshots.c.url]] = {}

      compare[row[screenshots.c.url]][side] = row[screenshots.c.uuid]
  
  compare = {}
  append_screenshots(compare, left_id['id'])
  append_screenshots(compare, right_id['id'], 'right')

  for url, LR in compare.iteritems():
    # create two temporary files as we might crop them
    left_image = tempfile.NamedTemporaryFile()
    right_image = tempfile.NamedTemporaryFile()
    
    shutil.copy2('data/captures/'+LR['left'], left_image.name)
    shutil.copy2('data/captures/'+LR['right'], right_image.name)

    print left_image.name + " vs " + right_image.name

    # TODO why not function
    # crop height to lowest height
    process = subprocess.Popen(["identify", "-format", '%[fx:h]', left_image.name], stdout=subprocess.PIPE)
    out, err = process.communicate()
    p1 = int(out)

    process = subprocess.Popen(["identify", "-format", '%[fx:h]', right_image.name], stdout=subprocess.PIPE)
    out, err = process.communicate()
    p2 = int(out)

    if p1 > p2: # left is larger
      subprocess.call(["mogrify", "-extent", "x" + str(p2), left_image.name])
    elif p2 > p1: # right is larger
      subprocess.call(["mogrify", "-extent", "x" + str(p1), right_image.name])
    


    subprocess.call(["compare", "-metric", "AE",
        "-fuzz", "8%",
        left_image.name,
        right_image.name,
        "data/compares/" + slugify(url) + '.png'])

    shutil.copy2(left_image.name, "/tmp/l.png")
    shutil.copy2(right_image.name, "/tmp/r.png")

    left_image.close()
    right_image.close()
else:
  print("Nothing to do")

conn.close()
