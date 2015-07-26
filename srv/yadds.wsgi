import os
import sys

sys.path.append("/var/www/yadds/srv/")
os.chdir(os.path.dirname(__file__))

import bottle
import yadds

application = bottle.default_app()
