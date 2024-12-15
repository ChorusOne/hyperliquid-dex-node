#!/usr/bin/bash

export HL_KEY=$(cat ~/secrets/node_config.json | jq -r .key)
~/hl-node --chain Testnet --key $HL_KEY send-signed-action '{"type": "CSignerAction", "unjailSelf": null}'

