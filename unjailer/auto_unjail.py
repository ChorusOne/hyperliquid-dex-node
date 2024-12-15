#!/usr/bin/env python3

import time
import logging
import requests
import subprocess
import json
from datetime import datetime
import argparse
import os

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Validator Check Script")
    parser.add_argument("--node", required=True, help="Hyperliquid node name (e.g., hyperliquid-validator01)")
    parser.add_argument("--period", type=int, default=600, help="Period in seconds for the script to run (default: 600)")
    return parser.parse_args()

def query_prometheus(node, prom_url):
    prom_query = f'increase(hl_block_height{{node_name="{node}"}}[2m])'
    try:
        response = requests.get(f"{prom_url}/api/v1/query", params={"query": prom_query})
        logging.info(f"Prometheus response status: {response.status_code}, JSON: {response.json()}")
        response.raise_for_status()
        data = response.json()
        result = data.get("data", {}).get("result", [])
        if result:
            return float(result[0]["value"][1])
        return None
    except Exception as e:
        logging.error(f"Error querying Prometheus: {e}")
        return None

def query_validator_api():
    validator_api_url = "https://api.hyperliquid-testnet.xyz/info"
    validator_name = "Chorus One"
    try:
        response = requests.post(
            validator_api_url,
            json={"type": "validatorSummaries"},
            headers={"Content-Type": "application/json"}
        )
        logging.info(f"Validator API response status: {response.status_code}")
        response.raise_for_status()
        validators = response.json()
        for validator in validators:
            if validator.get("name") == validator_name:
                return validator
        return None
    except Exception as e:
        logging.error(f"Error querying validator API: {e}")
        return None

def validate_conditions(node, prom_url):
    prom_value = query_prometheus(node, prom_url)
    if prom_value is None or prom_value <= 20:
        logging.info("Unjail condition 1 not satisfied: Prometheus value <= 20 or not available.")
        return False

    validator_data = query_validator_api()
    logging.info(f"Validator data: {validator_data}")
    if not validator_data:
        logging.info("Unjail condition 2/3 not satisfied: Validator data not available.")
        return False

    is_jailed = validator_data.get("isJailed", False)
    unjailable_after = validator_data.get("unjailableAfter")

    if is_jailed and unjailable_after:
        current_time = int(datetime.utcnow().timestamp())
        if current_time > unjailable_after:
            return True
        else:
            logging.info("Unjail condition 3 not satisfied: Current time <= unjailableAfter.")
    else:
        logging.info("Unjail condition 2 not satisfied: Validator not jailed or unjailableAfter not set.")

    return False

def execute_command(command):
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        logging.info(f"Command executed successfully. Output: {result.stdout}")
        if result.stderr:
            logging.warning(f"Command executed with warnings/errors: {result.stderr}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command: {e}. Stderr: {e.stderr}")

def main():
    args = parse_arguments()
    prom_url = os.getenv("PROM_URL")
    if not prom_url:
        logging.error("PROM_URL environment variable is not set. Exiting.")
        exit(1)

    node = args.node
    period = args.period

    logging.info(f"Starting with configuration: node={node}, period={period}s, prom_url={prom_url}")

    while True:
        try:
            logging.info("Starting unjail condition check...")
            if validate_conditions(node, prom_url):
                logging.info("All unjail conditions satisfied. Executing unjail command.")
                dirpath = os.path.dirname(os.path.realpath(__file__))
                execute_command([f"{dirpath}/unjail.sh"])
            else:
                logging.info("Unjail conditions not satisfied. Skipping unjail command execution.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

        logging.info(f"Sleeping for {period} seconds.")
        time.sleep(period)

if __name__ == "__main__":
    main()

