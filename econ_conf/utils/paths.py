import os

# Root data directory
DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFERENCES_DIR = os.path.join(DATA_DIR, 'data', 'conferences')
OUTPUTS_DIR = os.path.join(DATA_DIR, 'data', 'outputs')
