#!/bin/bash
#
# local test script
#

echo "[`date`] Starting purge"
 
cd /Users/jenny/repos/newsrx

source /Users/jenny/envs/newsrx/bin/activate

export NEWSRX_CONFIG='/Users/jenny/newsrx.cfg'

python -u elastic.py purge

echo "[`date`] Ending purge"

