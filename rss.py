"""
Get list of RSS feeds (from config file)
Get text of last 100 tweets from each user that has tweeted a link.
Load data into ElasticSearch.

Usage:
    python <script> [options]

Options:
    -h, --help
        Print this help information   
"""
import sys
import getopt
import os
import traceback
import time
import json
from pprint import pprint as pp
import feedparser
from birdy.twitter import TwitterRateLimitError
from dateutil import parser
import pytz
from config import get_rss_feeds
import twitter
import elastic
import json, httplib
import urllib

_rate_limits = None

def dump_feed(rss_url):
    """
    Dump rss feed entries to stdout.  Each entry needs to have 'link' and
    dateutil-parsable 'published' datetime.
    """
    d = feedparser.parse(rss_url)
    for entry in d.entries:
        pp(entry)
    print len(d.entries)
        
def get_article_list(feed_key, feed_url):
    """
    Get list of articles in RSS feed
    """
    article_list = []
    
    d = feedparser.parse(feed_url)        
    for post in d.entries:
        dt = parser.parse(post.published).astimezone(pytz.utc)        
        article_list.append({
            'feed': feed_key,
            'url': post.link, 
            'dt': dt.isoformat()
        })         
    return article_list    

def get_user_id_list(url):
    """
    Get user id list for an article
    (wrapped for Twitter API rate limiting)
    """
    try:
        return twitter.get_user_ids_by_url(url)
    except TwitterRateLimitError, e:
        print str(e)
        print 'Sleeping for 15 minutes...'
        twitter.destroy_app_client()
        time.sleep(900)
        print 'Resuming execution, retrying...'
        return get_user_id_list(url)

def get_user_text(user_id):
    """
    Get the tweet text for user_id
    (wrapped for Twitter API rate limiting)
    """
    try:
        return twitter.get_text_by_user_id(user_id)
    except TwitterRateLimitError, e:
        print str(e)
        print 'Sleeping for 15 minutes...'
        twitter.destroy_app_client()
        time.sleep(900)
        print 'Resuming execution, retrying...'
        return get_user_text(user_id)

def get_data():
    """
    Get data for each article in RSS feed.
    """
    """article_list = get_article_list(feed_key, feed_url)    
    print 'Found %d articles' % len(article_list)
    
    data_list = []    
    for article in article_list:
        url = article['url']
        
        if elastic.has_article(url):
            print 'Skipping (duplicate) %s' % url
        else:
            user_id_list = get_user_id_list(url)   
            n_users = len(user_id_list)
            if n_users < 5:
                print 'Skipping (%d users) %s' % (n_users, url)
            else:                         
                print 'Processing (%d users) %s' % (n_users, url)
            
                text_list = []        
                for user_id in user_id_list:
                    text_list.append(get_user_text(user_id))                            
                if len(text_list):
                    article['text'] = ' '.join(text_list)
                    data_list.append(article)
    print("******@#$%&^%#@$#^%@#********" + str(data_list))"""

    connection = httplib.HTTPSConnection('api.parse.com', 443)
    params = urllib.urlencode({"limit":1000})
    connection.connect()
    connection.request('GET', '/1/classes/Tweets?%s' % params, '', {
       "X-Parse-Application-Id": "ipEjxkPbQP8CTFidgpPG45dB0tyaHKSkwvNpnbC2",
       "X-Parse-REST-API-Key": "7A6EtP8HfWMPeWYNzb7cx1xOGjjSwyJ0cn9yx4oL"
     })
    result = json.loads(connection.getresponse().read())
    return result["results"]

        
def write_data(json_data, json_path):
    """
    Write json data to file
    (not using this anymore, loading directly into elastic search)
    """
    with open(json_path, 'w') as fp:
        json.dump(json_data, fp, indent=4)

#
# Main
#
def main():
    feeds = get_rss_feeds()
    for feed_key, d in feeds.iteritems():
        print '\nReading %(url)s' % d
        json_data = get_data(feed_key, d['url'])
        item_count = len(json_data)
        if item_count:
            elastic.load_data(json_data)
            print("*******" + json.dumps(json_data))

            print("got past elastic load")

        else:
            print 'Skipping, no data to load'    

"""class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

if __name__ == "__main__":
    try:
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hr:", ["help", "rss="])
        except getopt.error, msg:
             raise Usage(msg)

        # Handle options 
        for option, value in opts:
            if option in ("-h", "--help"):
                print __doc__
                sys.exit(0)
            else:
                raise Usage('unknown option "%s"' % option)
                            
        # Handle arguments 
        n_args = len(args)
        if n_args:
            raise Usage("invalid number of arguments")       

        # Doit
        main()                            
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        sys.exit(2)
    except Exception, err:
        print >>sys.stderr, err
        traceback.print_exc(err)
        sys.exit(1)
    else:
        sys.exit(0)
"""
