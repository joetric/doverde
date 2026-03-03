# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: Python 3
#     name: python3
# ---

# %% colab={"base_uri": "https://localhost:8080/"} id="o7bEEtIDAlgU" executionInfo={"status": "ok", "timestamp": 1772564193282, "user_tz": 300, "elapsed": 32645, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="9e9f1d90-3066-438d-c79f-1a7118e49635"
#SETUP
import sys
from datetime import date
from pathlib import Path

from google.colab import data_table, drive
import polars as pl
import polars.selectors as cs

drive.mount('/content/drive')
sys.path.append('/content/drive/MyDrive/doverde/doverde')
from config import cfg, FISC_PD_TO_CAL_MO

# --- SETTINGS FOR THIS FILE ---
CURRENT_FY = 2026 #TODO make dynamic function
LAST_FY_STR = str(CURRENT_FY - 1)
DATA_DIR = Path(cfg.paths.raw_dir)

 # use Colab data tables (must convert to Pandas before displaying)
data_table.enable_dataframe_formatter()

# %% id="Hx20baCqBgCU" executionInfo={"status": "ok", "timestamp": 1772564204424, "user_tz": 300, "elapsed": 4563, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
_conditional = pl.col('fiscal_year') != CURRENT_FY

dfr = pl.read_parquet(DATA_DIR / 'rev.parquet').filter(_conditional)
dfe = pl.read_parquet(DATA_DIR / 'ex.parquet').filter(_conditional)

# %% colab={"base_uri": "https://localhost:8080/", "height": 443} id="8FoRg8ZbDgzW" executionInfo={"status": "ok", "timestamp": 1772564214256, "user_tz": 300, "elapsed": 32, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="8f660fa0-730e-42e7-d146-d2fbcff2e078"
dfr
