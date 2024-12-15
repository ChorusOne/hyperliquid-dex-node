#!/bin/bash

substring=">>> hl-node @@"
logfile="hl_visor_output.log"

~/hl-visor run-non-validator > "$logfile" 2>&1 &   
pid=$!

tail -f "$logfile" | while read -r line; do
  if [[ "$line" == *"$substring"* ]]; then
    echo "Found match for '$substring'. Successfully downloaded hl-node."
    kill -SIGTERM $pid
    break
  fi
done

wait $pid
kill -SIGTERM $(pgrep hl-node)
rm -f "$logfile"

