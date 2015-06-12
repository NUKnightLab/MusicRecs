#!/bin/bash
#
# To run every 4 hours, cron it up as:
#
# 0 */4 * * * /home/infolab/apps/newsrx/scripts/populate.sh >> /home/infolab/logs/newsrx_populate.log 2>&1
#
# Ideally, this would be run more often, but we need to take rate limiting
# into account, which may require that we sleep for 15 minutes periodically.
#

echo "[`date`] Starting populate"
 
cd /home/infolab/apps/newsrx

source /home/infolab/env/newsrx/bin/activate

export NEWSRX_CONFIG='/etc/newsrx.cfg'

python -u rss.py

echo "[`date`] Ending populate"

