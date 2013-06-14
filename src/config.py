# Cursa application configuration file
from os.path import join, expanduser, abspath, dirname, pardir
import sys

version = '1.0'


# cursa_path points to the working directory that contains the application dependencies
# When running in production, the application is turned into a stand-alone executable using PyInstaller
# PyInstaller sets the sys._MEIPASS variable to point to the working directory
if getattr(sys, 'frozen', None):
    cursa_path = sys._MEIPASS
# In development mode use the DATA dir
else:
    cursa_path = abspath(join(dirname(__file__),
                        pardir,
                        'DATA'
                        )
                   )

# cursa_home is the root directory for all user files
# This will be where the Modules, Topics and Labs are created
cursa_home = join(expanduser("~"), 'cursa')

# contributor will be used to personalise work produced by cursa
contributor = 'John Roche (jroche@jmail.ie)'

# The Moodle URL
moodle_url = 'http://127.0.0.1:8080/moodle/'

# The web service token for this user
moodle_token = '7a1cacc62f984559a6d3c3ec0ea16da9'
