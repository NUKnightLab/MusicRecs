"""
Elasticsearch-related ops

Usage:
    python <script> [options] <command> [<arg>]

Options:
    -h, --help
        Print this help information

Commands:
    load_data
        Load data from file
        <arg> = required, file path
    
    find_articles
        Find relevant articles
        <arg> = required, screen_name
    
    purge
        Purge the newsrx index
        <arg> = relative hours threshold (default = 48)
    dump
        Dumps info from newsrx index
        <arg> = optional, sort order (default = dt:asc)
"""
"""
View index details
   
    http://127.0.0.1:9200/newsrx/_mapping/tweet/?pretty

Delete index

    curl -XDELETE 'localhost:9200/newsrx?pretty'

List all indexes

    curl 'localhost:9200/_cat/indices?v'

"""
import sys
import re
import getopt
import os
import traceback
from pprint import pprint as pp
from datetime import datetime, timedelta
import json
from elasticsearch import Elasticsearch
import config
import twitter
import rss

_index = 'newsrx'

#
# Note that feed and url are specified as 'not_analyzed', because we want to 
# do exact matching only on those fields
#
_index_body = {
    "mappings": {
        "tweet": {
            "properties": {
                "userName": {"type": "string"},
                "objectId": {"type": "string"},
                "trackid": {"type": "string"},
                "tweetString": {"type": "string"},
                "updatedAt": {"type": "string"},
                "createdAt": {"type": "string"}
            }
        }
    }
}

_es = None
    

def get_client():
    """
    Get elasticsearch user client
    """
    global _es
    if _es is None:
        conn_params = config.get_section_data('elasticsearch')
        _es = Elasticsearch([conn_params])
    return _es
  
def test():
    es = get_client()
    pp(es.info())
    pp(es.indices.get_settings(index='_all'))
    
def dump():
    """dump stuff to stdout"""
    es = get_client()

    q = {
        'query': {
            'filtered': {
                'query': {
                    'match_all': {}
                }
            }
        }
    }
    result = es.search(index=_index, body=q, size=99999, _source='userName')
    print(result)  
   # for hit in result['hits']['hits']:
    #    print (hit)
      
def purge(hours=48):
    """
    Purge all articles published more than a certain number of hours ago
    """
    es = get_client()
    
    dt = datetime.utcnow() - timedelta(hours=hours)
    threshold = dt.isoformat().split('.')[0]
    
    q = {
        'query': {
            'filtered': {
                'query': {
                    'match_all': {}
                }
            }
        }
    }
                        
    result = es.search(index=_index, body=q, size=99999, _source='dt,url')  
    print 'Deleting %d items before %s' % (len(result['hits']['hits']), threshold)        
    return es.delete_by_query(index=_index, body=q)    

def has_article(name):
    """
    Whether or not an article already exists in ElasticSearch
    """
    es = get_client()
    es.indices.create(index=_index, body=_index_body, ignore=400)

    q = {'query': {'match': {'trackid': name}}}
    result = es.search(index=_index, body=q, _source='trackid')  
    return len(result['hits']['hits'])

def has_article2(name):
    """
    Whether or not an article already exists in ElasticSearch
    """
    es = get_client()
    es.indices.create(index=_index, body=_index_body, ignore=400)

    q = {'query': {'match': {'userName': name}}}
    result = es.search(index=_index, body=q, _source='userName')  
    return len(result['hits']['hits'])
     
def find_articles(screen_name, twitter_client=None):
    """
    Find relevant articles in ElasticSearch for screen_name from feeds
    @feeds = list of string feed keys (see config file)
    """
    es = get_client()
    returnList = [[],[],[],[]]
    tweets = twitter.get_text_by_screen_name(screen_name, client=twitter_client)
    word_list = tweets.split()
    ct1 = ' '.join(word_list[:500])
    q = {
        'query': {
            'filtered': {
                'query': {
                    'match': {'tweetString': ct1}
                }
            }
        }
    }
    result = es.search(index=_index, body=q)
    pp(result)
    id_list = []
    user_list = []
    mentions_list = []
    hash_list = []
    for hit in result['hits']['hits']:
        print("&&&&&&&&&&&&&&&&&&&&&&&&&")
        print(hit)
        if (len(id_list) >= 8):
           break
        else:
           x = (hit['_source']["trackid"]).encode('utf-8')
           y = (hit['_source']["userName"]).encode('utf-8')
           id_list.append(x)
           user_list.append(y)
           mentions_list.append(list(set([re.sub(r'\W+','',word) for word in hit['_source']['tweetString'].split() if "@" in word]))[:5])
           hash_list.append(list(set([re.sub(r'\W+','',word) for word in hit['_source']['tweetString'].split() if "#" in word]))[:5])

    returnList[0] = id_list
    returnList[1] = user_list
    returnList[2] = mentions_list
    returnList[3] = hash_list
    return returnList



def load_data():
    """
    Load new data into elasticsearch

    """
    data = rss.get_data()
    print 'Examining %d items...' % len(data) 
    es = get_client()
    
    es.indices.create(index=_index, body=_index_body, ignore=400)
    for doc in data:
        if (has_article(doc['trackid']) or has_article2(doc['userName'])):
            print 'Skipping %s' % doc['trackid']
        else:  
            es.index(index=_index, doc_type='tweet', body=doc)
    es.indices.refresh(index=_index)


"""def load_data_from_file(json_file_path):
   
    print 'Reading %s...' % json_file_path
    with open(json_file_path) as fp:
        data = json.load(fp)       
        load_data()


#
# Main
#
    
class Usage(Exception):
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
        if n_args < 1 or n_args > 2:
            raise Usage("invalid number of arguments")     
        arg_command = args[0]  

        if arg_command == 'dump':
            if n_args > 1:
                dump(args[1])   
            else:
                dump()       
        elif arg_command == 'load_data':
            load_data_from_file(args[1])
        elif arg_command == 'find_articles':
            pp(find_articles(args[1], ['abc', 'bbc', 'huffpo']))
        elif arg_command == 'purge':
            if n_args > 1:                
                print purge(int(args[1]))
            else:
                print purge()
        else:
            raise Usage('unknown command "%s"' % arg_command)

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        sys.exit(2)
    except Exception, err:
        print >>sys.stderr, err
        traceback.print_exc(err)
        sys.exit(1)
    else:
        sys.exit(0)"""
