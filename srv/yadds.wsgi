import os
import sys

sys.path.append(os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

import bottle
import yadds

application = bottle.default_app()
