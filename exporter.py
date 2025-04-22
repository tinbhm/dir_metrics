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

def scan_directory(directory_config):
    path = directory_config['path']
    name = directory_config.get('name', path)
    recursive = directory_config.get('recursive', False)
    include_patterns = directory_config.get('include_patterns', ['*'])
    include_dirs = directory_config.get('include_dirs', [])

    actual_path = path
    logging.info(f"📁 Scanning: {actual_path} (name: {name})")

    files = []
    total_size = 0

    try:
        if recursive:
            for root, dirs, filenames in os.walk(actual_path):
                if include_dirs:
                    dirs[:] = [d for d in dirs if d in include_dirs]
                for filename in filenames:
                    if matches_patterns(filename, include_patterns):
                        filepath = os.path.join(root, filename)
                        try:
                            stat = os.stat(filepath)
                            files.append((filepath, stat.st_mtime, stat.st_size))
                            total_size += stat.st_size
                        except Exception as e:
                            logging.warning(f"⚠️  Fehler beim Zugriff auf Datei {filepath}: {e}")
        else:
            for filename in os.listdir(actual_path):
                if matches_patterns(filename, include_patterns):
                    filepath = os.path.join(actual_path, filename)
                    if os.path.isfile(filepath):
                        try:
                            stat = os.stat(filepath)
                            files.append((filepath, stat.st_mtime, stat.st_size))
                            total_size += stat.st_size
                        except Exception as e:
                            logging.warning(f"⚠️  Fehler beim Zugriff auf Datei {filepath}: {e}")

        now = time.time()
        if files:
            ages = [now - mtime for _, mtime, _ in files]
            newest = min(ages)
            oldest = max(ages)
            file_age_oldest.labels(directory=name).set(oldest)
            file_age_newest.labels(directory=name).set(newest)
            for filepath, mtime, _ in files:
                age = now - mtime
                file_age_gauge.labels(directory=name, filename=os.path.basename(filepath)).set(age)
        else:
            file_age_oldest.labels(directory=name).set(0)
            file_age_newest.labels(directory=name).set(0)

        file_count_gauge.labels(directory=name).set(len(files))
        file_size_total.labels(directory=name).set(total_size)

    except Exception as e:
        logging.error(f"❌ Fehler beim Zugriff auf {actual_path}: {e}")
        file_count_gauge.labels(directory=name).set(0)
        file_age_oldest.labels(directory=name).set(0)
        file_age_newest.labels(directory=name).set(0)
        file_size_total.labels(directory=name).set(0)

def run_exporter(config):
    port = config.get('port', 8000)
    interval = config.get('interval', 30)
    directories = config.get('directories', [])

    start_http_server(port)
    logging.info(f"🚀 Exporter läuft auf Port {port}, Scan-Intervall: {interval} Sekunden")

    while True:
        for directory_config in directories:
            scan_directory(directory_config)
        time.sleep(interval)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Prometheus File Exporter")
    parser.add_argument('--config', required=True, help='Pfad zur config.yml')
    args = parser.parse_args()

    config = load_config(args.config)
    run_exporter(config)