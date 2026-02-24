import yaml
from pathlib import Path
from google.colab import drive

drive.mount('/content/drive') # prob already mtd
PROJECT_ROOT = Path('/content/drive/MyDrive/dnrec_dpr_revex_engine')

FISC_PD_TO_CAL_MO = {1:7, 2:8, 3:9, 4:10, 5:11, 6:12, 7:1, 8:2, 9:3, 10:4, 11:5, 12:6}

class Config:
    def __init__(self, data):
        self.paths = type('obj', (object,), data['paths'])
        self.socrata = type('obj', (object,), data['socrata'])

def load_config():
    with open(PROJECT_ROOT / 'config.yaml', 'r') as f:
        return Config(yaml.safe_load(f))

cfg = load_config()