import os
import sys
from os.path import expanduser
import collections
import ConfigParser

CONFIG_ENV_VAR = 'NEWSRX_CONFIG'
DEFAULT_CONFIG_DIR = expanduser('~')
DEFAULT_CONFIG_FILE = 'Desktop/MusicRX/newsrx.cfg'

_config = None

def config_file_path():
    return os.getenv(CONFIG_ENV_VAR,
        os.path.join(DEFAULT_CONFIG_DIR, DEFAULT_CONFIG_FILE))

def configuration():
    global _config
    if _config is None:
        _config = ConfigParser.SafeConfigParser()
        path = config_file_path()
        with open(path) as f:
            _config.readfp(f)
    return _config

def get_section_data(section):
    config = configuration()
    d = {}
    for name, value in config.items(section):
        d[name] = value
    return d
  
def get_twitter_keys(section='twitter'):    
    config = configuration()
    TwitterKeys = collections.namedtuple('TwitterKeys', [
        'consumer_key',
        'consumer_secret',
        'access_token',
        'access_token_secret'])
    k = TwitterKeys(
        config.get(section, 'twitter_consumer_key'),
        config.get(section, 'twitter_consumer_secret'),
        config.get(section, 'twitter_access_token'),
        config.get(section, 'twitter_access_token_secret'))
    return k

def get_rss_feeds():
    feeds = {}
    config = configuration()
    for key, value in config.items('rss'):
        d = value.split(',')
        feeds[key] = {'url': d[0].strip(), 'name': d[1].strip()}
    return feeds
