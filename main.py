import os
import time
import yaml
import fnmatch
import logging
import argparse
from prometheus_client import Gauge, start_http_server

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

file_age_gauge = Gauge('file_age_seconds', 'Age of a file in seconds', ['directory', 'filename'])
file_count_gauge = Gauge('file_count_total', 'Total number of files in the directory', ['directory'])
file_size_total = Gauge('file_size_bytes_total', 'Total size of files in the directory', ['directory'])
file_age_oldest = Gauge('file_age_oldest_seconds', 'Age of the oldest file in the directory', ['directory'])
file_age_newest = Gauge('file_age_newest_seconds', 'Age of the newest file in the directory', ['directory'])

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def matches_patterns(filename, patterns):
    return any(fnmatch.fnmatch(filename, pattern) for pattern in patterns)