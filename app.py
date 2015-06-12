
import traceback
from flask import Flask, request, session, redirect, render_template, \
    url_for, jsonify
from birdy.twitter import UserClient, TwitterAuthError
import config
import elastic
import get_spotify_tweets


app = Flask(__name__)

from werkzeug.wsgi import DispatcherMiddleware

app.secret_key = '\x07\x9c\xcc\xfc\x8fW\xed\xe8O\xc7\x9c*\xb2\xe2p\xbf\x95\xdaQ\xfb\r\xaa\x01\x1e'

application = DispatcherMiddleware(app, {
    '/newsrx':     app
})

#
# Pre-load available feeds
#
_feeds = []
for key, d in config.get_rss_feeds().iteritems():
    _feeds.append({'key': key, 'name': d['name']})

#
# Utility
#

def session_pop(key):
    if key in session:
        session.pop(key)
    
def session_pop_list(key_list):
    for key in key_list:    
        if key in session:
            session.pop(key)

#
# Auth
#

@app.route('/auth/clear/')
def auth_clear():
    session_pop_list(['auth_token', 'auth_token_secret', 'auth_redirect',
        'access_token', 'access_token_secret', 'screen_name'])
    return jsonify({ 'status': 'OK' })

@app.route('/auth/check/')
def auth_check():
    """
    Check authorization.  Get signin token and auth_url, if needed.
    
    @redirect = redirect to this url post-authorization verification
    """
    try:
        access_token = session.get('access_token')
        access_token_secret = session.get('access_token_secret')


        tk = config.get_twitter_keys()
        print tk


        if access_token and access_token_secret:
            client = UserClient(
                tk.consumer_key,
                tk.consumer_secret,
                tk.access_token,
                tk.access_token_secret)

            # We need to make a call to verify_credentials in case the user
            # has revoked access for this application. This is a rate-limited
            # call and so this approach might not be ideal.
            verif = client.api.account.verify_credentials.get()
            if verif.headers['status'].split()[0] == '200':
                return jsonify({'is_auth': 1})
            else:
                # possibly revoked access, although this will probably
                # get handled by the TwitterAuthError catch
                auth_clear()
                return jsonify({'is_auth': 0})
            
        client = UserClient(tk.consumer_key, tk.consumer_secret)

        callback = 'http://'+request.host+url_for('auth_verify')
        print 'getting auth token for callback:', callback
        token = client.get_authorize_token(callback)
                
        session['auth_token'] = token.oauth_token
        session['auth_token_secret'] = token.oauth_token_secret
        session['auth_redirect'] = request.args.get('redirect') or ''

        # START DEBUG
        #print 'AUTH_CHECK', app
        #for k, v in session.iteritems():
        #    print k, v
        # END DEBUG
        data = {'is_auth': 0, 'auth_url': token.auth_url}
        return jsonify(data)
    except TwitterAuthError:
        auth_clear()
        return jsonify({'is_auth': 0})
    except Exception, e:
        traceback.print_exc()
        return jsonify({'error': str(e)})
             

@app.route('/auth/verify/')
def auth_verify():
    """
    Get final access token and secret, redirect       
    @oauth_verifier = parameter from auth_url callback (see above)  
    """
    try:
        # START DEBUG
        # if session values are in the AUTH CHECK but not here - be sure
        # to check cookie settings. Note: Firefox let's you select
        # "Accept Cookies" even when in "Always use private mode" -- however
        # cookies do not work in this mode.
        #print 'AUTH_VERIFY', app
        #for k, v in session.iteritems():
        #    print k, v
        # END DEBUG

        oauth_verifier = request.args.get('oauth_verifier')
        if not oauth_verifier:
            raise Exception('Expected oauth_verifier parameter')

        auth_token = session.get('auth_token')
        auth_token_secret = session.get('auth_token_secret')    
        auth_redirect = session.get('auth_redirect') or url_for('index')
        if not (auth_token and auth_token_secret):
            raise Exception('Authorization credentials not found in session')
    
        tk = config.get_twitter_keys()
        client = UserClient(tk.consumer_key, tk.consumer_secret,
                    auth_token, auth_token_secret)                    
        token = client.get_access_token(oauth_verifier)
        
        print token
        
        session['access_token'] = token.oauth_token
        session['access_token_secret'] = token.oauth_token_secret  
        session['screen_name'] = token.screen_name
        session_pop_list(['auth_token', 'auth_token_secret', 'auth_redirect'])
        
        return redirect(auth_redirect)
    except Exception, e:
        traceback.print_exc()
        return redirect(auth_redirect)

#
# Main routes
#

@app.route('/', methods=['GET', 'POST'])
def index():  
    """
    Main page
    """
    try:        
        return render_template('index.html', screen_name=session.get('screen_name'))
    except Exception, e:
        traceback.print_exc()
        return render_template('index.html', error=str(e))
    
@app.route('/music/', methods=['GET', 'POST'])
def articles():  
    """
    Display article recommendations
    """
    try:
        screen_name = request.values.get('screen_name', '')
        print(screen_name)
        
        if not screen_name:
            raise Exception('Expected "screen_name" parameter.')

        #feeds = request.form.getlist('feeds')
        #if not feeds:
        #    raise Exception('Expected "feeds" parameter')
            
        access_token = session.get('access_token')
        access_token_secret = session.get('access_token_secret')

        if not (access_token and access_token_secret):
            raise Exception('Could not retrieve access tokens')
            
        tk = config.get_twitter_keys()


        client = UserClient(
            tk.consumer_key,
            tk.consumer_secret,
            tk.access_token,
            tk.access_token_secret)

        raw_data = elastic.find_articles(screen_name, twitter_client=client)
        user_list = raw_data[1]
        user_list = list(set(user_list))
        track_list = raw_data[0]
        track_list = list(set(track_list))
        mentions_list = raw_data[2]
        hash_list = raw_data[3]
        print "TRACK LIST"
        print track_list

        source = get_spotify_tweets.make_spotify_playlist(track_list)




        return render_template('recommendations.html', 
            screen_name=screen_name, src = source,userList=user_list,mentionsList=mentions_list,hashList = hash_list, trackList = track_list)
    except Exception, e:
        traceback.print_exc()
        print(e)
        return render_template('recommendations.html', src = source, userList=user_list,mentionsList=mentions_list, hashList = hash_list, bigE = e, trackList = track_list)

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
