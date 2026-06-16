import time
import subprocess
import os
import sys

# Configure sync interval in seconds (default 1 minute for faster response)
SYNC_INTERVAL = 10

# Ensure we are in the correct directory
os.chdir(r'd:\BS\sync_engine')

def run_sync():
    # 1. Run sync.py
    subprocess.run([sys.executable, 'sync.py'], capture_output=True, text=True)
    
    # 2. Run process_deltas.py
    subprocess.run([sys.executable, 'process_deltas.py'], capture_output=True, text=True)

if __name__ == '__main__':
    while True:
        try:
            run_sync()
            time.sleep(SYNC_INTERVAL)
        except Exception:
            # On any error, sleep for 1 minute then retry to prevent rapid crash looping
            time.sleep(60)
