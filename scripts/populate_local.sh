#!/bin/bash
#
# local test script
#

echo "[`date`] Starting populate"
 
cd /Users/jenny/repos/newsrx

source /Users/jenny/envs/newsrx/bin/activate

export NEWSRX_CONFIG='/Users/jenny/newsrx.cfg'

python -u rss.py

echo "[`date`] Ending populate"

