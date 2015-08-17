"""lucern

Usage:
  lucern.py createdb <filename> [--dir=<dir>]
  lucern.py capture <inputurls.txt> <name> [--width=<width>] [--dir=<dir>]
  lucern.py compare <left> <right> [--dir=<dir>]

Options:
  -d <dir>, --dir=<dir>  Directory to store files in, defaults to your current directory
  --width=<width>  Width in pixels [default: 1024].
"""

import os
import sys
import logging

from docopt import docopt
from sqlalchemy.sql import select

from imagemagick import execute
from database import engine, metadata, capturesessions, screenshots
from capture import capture
from compare import compare

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

if __name__ == '__main__':
  arguments = docopt(__doc__)

  # default directory
  if arguments['--dir'] is None:
    directory = os.getcwd()
  else:
    directory = arguments['--dir']
  
  if arguments['createdb']:
    metadata.create_all(engine)
    logging.info('Database created')
  elif arguments['capture']:
    conn = engine.connect()
    
    with open(os.path.join(directory, arguments['<inputurls.txt>'])) as f:
      urls = f.read().split("\n")

    capture(arguments['<name>'], urls, int(arguments['--width']), conn)
    conn.close()
  elif arguments['compare']:
    conn = engine.connect()

    compare(engine, arguments['<left>'], arguments['<right>'])

    conn.close()
