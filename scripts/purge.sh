#!/bin/bash
#
# To run every day, cron it up as:
#
# 0 6 * * * /home/infolab/apps/newsrx/scripts/purge.sh >> /home/infolab/logs/newsrx_purge.log 2>&1
#
#

echo "[`date`] Starting purge"
 
cd /home/infolab/apps/newsrx

source /home/infolab/env/newsrx/bin/activate

export NEWSRX_CONFIG='/etc/newsrx.cfg'

python -u elastic.py purge

echo "[`date`] Ending purge"

