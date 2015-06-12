"""
WSGI config for newsrx project.
"""
import os
import sys
import site

site.addsitedir('/home/infolab/env/newsrx/lib/python2.7/site-packages')
sys.path.append('/home/infolab/apps/newsrx')
sys.stdout = sys.stderr

os.environ.setdefault('NEWSRX_CONFIG', '/etc/newsrx.cfg')

#from app import app as application
from app import application
