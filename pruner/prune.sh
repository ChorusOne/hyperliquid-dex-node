#!/bin/bash

DELETE_OLDER_THAN_DAYS=$1
PERIOD_SECONDS="${2:-86400}" # Default: 24 hrs

DATA_PATH="/home/hluser/hl"

echo "Will prune every $PERIOD_SECONDS seconds"
echo "Will delete files in data directory older than $DELETE_OLDER_THAN_DAYS days"

while true; do
    echo "Sleeping for $PERIOD_SECONDS seconds"
    sleep $PERIOD_SECONDS

    echo "Deleting files in data directory older than $DELETE_OLDER_THAN_DAYS days"
    find "$DATA_PATH/data" -mindepth 1 -depth -mtime +$DELETE_OLDER_THAN_DAYS -delete
    find "$DATA_PATH/hyperliquid_data" -mindepth 1 -depth -mtime +$DELETE_OLDER_THAN_DAYS -delete
done
