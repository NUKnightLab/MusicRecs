import twitter
import pymongo
import urllib2
from TwitterSearch import *
import json,httplib
import urlparse
import time
connection = httplib.HTTPSConnection('api.parse.com', 443)
connection.connect()



#keys
consumer_key = '24WdUDibyMkmDxerQgHbuvIGN'
consumer_secret = 'fsR4gdXLfzZCYHko4iAyzmG23iuVLCxP2KwzqWD7M5PLwSxRAq'
access_token_key = '2423952686-mX7SYVfDrSFL5En2KuxApvU6TeB3yoTXkQ19ReU'
access_token_secret = 'gBbesRqSNOcaBFJcmQDfifRxyWdhczsnDs6PIscNmP9aX'


#get tweets
def get_spotify_tweets():
    """retrieves all tweets (within Twitter limits) that link to Spotify songs, stores in a Parse database"""
    try:
        tso=TwitterSearchOrder()
        tso.set_keywords(['spoti.fi'])
        tso.set_language('en')
        ts = TwitterSearch(consumer_key, consumer_secret, access_token_key, access_token_secret)
        tweetList = []
        for tweet in ts.search_tweets_iterable(tso):
            if (tweet["user"]["screen_name"] not in tweetList) and ("open.spotify.com/track" in expand_url(tweet['entities']['urls'][0]['expanded_url'])):
                tweetList.append(tweet["user"]["screen_name"])
                connection.request('POST', '/1/classes/Tweets', json.dumps({
                "userName":tweet['user']["screen_name"],
                "tweetString":twitter.get_text_by_screen_name(tweet['user']['screen_name']),
                "trackid":get_track_id(expand_url(tweet['entities']['urls'][0]['expanded_url']))
            }), {
           "X-Parse-Application-Id": "ipEjxkPbQP8CTFidgpPG45dB0tyaHKSkwvNpnbC2",
           "X-Parse-REST-API-Key": "7A6EtP8HfWMPeWYNzb7cx1xOGjjSwyJ0cn9yx4oL",
           "Content-Type": "application/json"
         })
                result = json.loads(connection.getresponse().read())
                print result


    except TwitterSearchException as e:
        print e


def expand_url(url):
    """expands a Spotify URL to make sure that it is not shortened"""
    if url[0:7] != 'http://':
        url = 'http://' + url
    a=urllib2.urlopen(url)
    return a.url

def get_track_id(url):
    """returns a Spotify track id given an http://open.spotify.... url"""
    curr = -1
    track_id = []
    while url[curr] != '/':
        track_id.append(url[curr])
        curr = curr - 1

    track_id.reverse()
    track_id = "".join(track_id)

    return track_id

def make_spotify_playlist(trackids):
    """Given a list of track ids, makes the src tag for a Spotify widget playlist"""
    src = "https://embed.spotify.com/?uri=spotify:trackset:MusicRecs:"
    for trackid in trackids:
        src = src + trackid + ','
    src = src[:-1]

    return src

#get_spotify_tweets()


