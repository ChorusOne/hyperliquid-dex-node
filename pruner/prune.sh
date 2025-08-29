#!/bin/bash

DELETE_OLDER_THAN_DAYS=$1
PERIOD_SECONDS="${2:-86400}" # Default: 24 hrs

# Only prune data directory, not the new `hyperliquid_data` directory
DATA_PATH="/home/hluser/hl/data"

echo "Will prune every $PERIOD_SECONDS seconds"
echo "Will delete files in data directory older than $DELETE_OLDER_THAN_DAYS days"

while true; do
    # prune before sleeping
    echo "Deleting files in data directory older than $DELETE_OLDER_THAN_DAYS days"
    find "$DATA_PATH" -mindepth 1 -depth -mtime +$DELETE_OLDER_THAN_DAYS -delete

    echo "Sleeping for $PERIOD_SECONDS seconds"
    sleep $PERIOD_SECONDS
done
