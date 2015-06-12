import time
from birdy.twitter import AppClient
from config import get_twitter_keys


_app_client = None


def get_app_client():
    """
    Get twitter client.  Use the AppClient for app authenticated requests,
    because it has higher rate limits.
    """
    global _app_client
    if _app_client is None:
        tk = get_twitter_keys()
        access_token = AppClient(tk.consumer_key, tk.consumer_secret).get_access_token()
        _app_client = AppClient(tk.consumer_key, tk.consumer_secret, access_token)
    return _app_client

def destroy_app_client():
    """
    Destroy the twitter app client (so it gets recreated on next call).
    """
    global _app_client
    _app_client = None

def get_rate_limit_status(client):
    """
    Get client rate limit status for resources.  These limits have a 15-minute
    window, and 'reset' is epoch time, e.g. int(time.time()).
    """
    r = client.api.application.rate_limit_status \
        .get(resources='search,statuses').data.resources
    return {
        'search': {
            'remaining': r.search.get('/search/tweets').remaining,
            'reset': r.search.get('/search/tweets').reset
        },
        'user_timeline': {
            'remaining': r.statuses.get('/statuses/user_timeline').remaining,
            'reset': r.statuses.get('/statuses/user_timeline').reset
        }
    }
 
 #
 # search
 #

def search(params, client=None):
    """Search twitter"""
    ct = client or get_app_client()   
    return ct.api.search.tweets.get(**params).data

def search_by_url(url, count=10, client=None):
    """Search for tweets containing url"""
    params = {'q': url, 'count': count, 'result_type': 'recent'}
    result = search(params, client)
    return result.statuses    

def get_user_ids_by_url(url, count=10, client=None):
    """Get list of user_ids that have tweeted out url"""
    tweet_list = search_by_url(url, count, client)
    return [t.user.id_str for t in tweet_list]

#
# user timeline
#

def get_user_timeline(params, client=None):
    """Get user timeline"""
    ct = client or get_app_client()
    return ct.api.statuses.user_timeline.get(**params).data
        
def get_tweets_by_user_id(user_id, count=100, client=None):
    """Get most recent user tweets for user_id"""
    params = {'user_id': user_id, 'count': count, 'include_rts': True}
    return get_user_timeline(params, client)

def get_tweets_by_screen_name(screen_name, count=100, client=None):
    """Get most recent user tweets for screen_name"""
    params = {'screen_name': screen_name, 'count': count, 'include_rts': True}
    return get_user_timeline(params, client)
        
def get_text_by_user_id(user_id, count=100, client=None):
    """Get text of past 100 tweets by user_id"""
    tweet_list = get_tweets_by_user_id(user_id, count, client)
    return ' '.join([t.text for t in tweet_list])
    
def get_text_by_screen_name(screen_name, count=100, client=None):
    """Get text of past 100 tweets by screen_name"""
    tweet_list = get_tweets_by_screen_name(screen_name, count, client)
    return ' '.join([t.text for t in tweet_list])


