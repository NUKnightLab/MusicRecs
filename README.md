# Deployment Status

Currently deployed to prd-web1 at http://23.236.61.92/newsrx/

Uses Elastic search on localrx-elasticsearch

populate.sh script cron-ed to run every 4 hours

purge.sh script cron-ed to run every day 


# Development

### Setup virtual environment

`mkvirtualenv newsrx`

`pip install -r requirements.txt`

### ElasticSearch

Download from http://www.elasticsearch.org/download/

Run from bin directory: `./elasticsearch`

You may be be prompted to install a JDK.

### Getting started

Place a copy of `newsrx.cfg` in your home directory and fill out as required.

Activate the virtual environment, and change into the repository directory.

To verify the app can read the cfg file, dump the Twitter key information:

`python -c "import config;  print config.get_twitter_keys()"`

To verify the app can connect to Elasticsearch, dump the index information:

`python -c "import elastic; print elastic.test()"`

Run `python rss.py` to load data into ElasticSearch.

Run app.py to start the application.

Visit the web app at `http://localhost:5000`