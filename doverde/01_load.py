# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: Python 3
#     name: python3
# ---

# %% [markdown] id="VmovYB4YL2N-"
# # Delaware Revenue / Expense Data ETL

# %% [markdown] id="oONrAT6HRW4M"
# ## Load libraries and our config module which loads config.yaml
#
# config.yaml (in project dir) defines filters (e.g. DNREC/DPR), default API limits, default columns to fetch, API URL and keyed Socrata data IDs. Runtime must be restarted for changes to take effect.
#
# You could edit the fetch method on this page to use a Socrata API key (may allow for higher limits).

# %% colab={"base_uri": "https://localhost:8080/"} executionInfo={"elapsed": 2540, "status": "ok", "timestamp": 1771906706332, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}, "user_tz": 300} id="R7sxD9UXB2lr" outputId="bd2d3ee5-19d8-478b-de16-f50fd54fb520"
# @title
from datetime import datetime
import sys
# !uv pip install sodapy jupytext
import polars as pl
from sodapy import Socrata
from pathlib import Path
from dataclasses import dataclass
from google.colab import data_table, drive#, userdata # uncomment to get secrets

drive.mount('/content/drive')
sys.path.append('/content/drive/MyDrive/doverde/doverde')
from config import cfg, FISC_PD_TO_CAL_MO


# %% id="MxRbieC7vCMU" executionInfo={"status": "ok", "timestamp": 1771906706460, "user_tz": 300, "elapsed": 95, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
def _fp_to_cal_mo(fp: int) -> int:
    """Convert fiscal period to calendar month for a July-start FY (e.g. Del.)

    Args:
        fp (int): Fiscal period (1=July through 12=June). Casts to int.

    Returns:
        int: Calendar month (1=January through 12=December).
    """
    #Jan:Jul ... Dec:Jun
    return FISC_PD_TO_CAL_MO[int(fp)]

def _get_remote_updated_at(client, data_id) -> datetime:
    """Get the last updated timestamp from Socrata dataset metadata."""
    metadata = client.get_metadata(data_id)
    return datetime.fromtimestamp(metadata['rowsUpdatedAt'])

def _get_local_updated_at(data_id_key) -> datetime | None:
    """Get the last modified time of the local parquet file, or None if it doesn't exist."""
    filepath = Path(cfg.paths.processed_dir) / f'{data_id_key}.parquet'
    if not filepath.exists():
        return None
    return datetime.fromtimestamp(filepath.stat().st_mtime)

def fetch_dataset(data_id_key, force_refresh=False, **query_overrides):
    with Socrata(cfg.socrata.api_url, None) as client:
        data_id = cfg.socrata.api_data_ids[data_id_key]
        api_get_kwargs = {**cfg.socrata.api_filters, **query_overrides}

        local_updated_at = _get_local_updated_at(data_id_key)

        # --- FRESHNESS CHECK and backup row count check ---
        if not force_refresh and local_updated_at is not None:
            remote_updated_at = _get_remote_updated_at(client, data_id)
            if remote_updated_at <= local_updated_at:
                print(f'{data_id_key}: local file is current as of {local_updated_at:%Y-%m-%d}. Loading from parquet.')
                return pl.read_parquet(Path(cfg.paths.processed_dir) / f'{data_id_key}.parquet')

            # Remote is newer — secondary count check
            print(f'{data_id_key}: remote updated {remote_updated_at:%Y-%m-%d}, local {local_updated_at:%Y-%m-%d}. Checking count...')
            count_results = client.get(data_id, select="COUNT(*)", **api_get_kwargs)
            remote_count = int(count_results[0]['COUNT'])
            local_count = len(pl.read_parquet(Path(cfg.paths.processed_dir) / f'{data_id_key}.parquet'))
            if remote_count == local_count:
                print(f'Count unchanged at {remote_count:,} — but remote is newer. Fetching to be safe.')

        # --- SOCRATA DATA FETCH ---
        count_results = client.get(data_id, select="COUNT(*)", **api_get_kwargs)
        total_count = int(count_results[0]['COUNT'])
        if total_count > cfg.socrata.limit:
            print(f"WARNING: {data_id_key} has {total_count:,} records, but your limit is {cfg.socrata.limit:,}!")
        else:
            print(f"Fetching {total_count:,} records...")

        cols = cfg.socrata.api_default_fields.get(data_id_key)
        select_str = ",".join(cols) if cols else "*"
        fetch_kwargs = {**api_get_kwargs, 'limit': cfg.socrata.limit, 'select': select_str}
        results = client.get(data_id, **fetch_kwargs)
        return pl.from_dicts(results)

def save_df(df, data_id_key):
    """Save a Polars DataFrame as parquet"""
    proc_dir = Path(cfg.paths.processed_dir)
    proc_dir.mkdir(parents=True, exist_ok=True)
    filepath = proc_dir / f'{data_id_key}.parquet'
    df.write_parquet(filepath)
    print(f'Saved {data_id_key} to {filepath}.')


# %% [markdown] id="3JWVweXBNUp5"
# ## Fetch Data

# %% colab={"base_uri": "https://localhost:8080/"} id="of78GLICB6Tr" outputId="e9016fd6-e95e-4a4c-e017-fc1a71ecc1cf" executionInfo={"status": "ok", "timestamp": 1771906721749, "user_tz": 300, "elapsed": 15285, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
force_refresh = getattr(cfg.socrata, 'force_refresh', False)
dfe = fetch_dataset('ex', force_refresh=force_refresh)
dfr = fetch_dataset('rev', force_refresh=force_refresh)

# %% [markdown] id="zMEwFkueLyrc"
# ## Transform Expense Data
#
# **Despite the dataset name, these are line items, not checks** (note how check numbers appear more than once on the same date).
#
# Types converted below.

# %% id="EKxuDnThHEjs" executionInfo={"status": "ok", "timestamp": 1771906722018, "user_tz": 300, "elapsed": 263, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
dfe = dfe.with_columns([
    pl.col('fiscal_year').cast(pl.UInt16),
    pl.col('fiscal_period').cast(pl.UInt8),
    pl.col('amount').cast(pl.Decimal),
    pl.col('check_date').str.to_date('%Y-%m-%dT%H:%M:%S%.3f'),
    pl.col(['vendor', 'category', 'fund_type']).cast(pl.Categorical),
])
# dfe.head(5) # uncomment to preview data in notebook

# %% [markdown] id="-mQGJuHhQ2bU"
# ## Transform Revenue Data

# %% id="0vhHH81RZVwd" executionInfo={"status": "ok", "timestamp": 1771906722028, "user_tz": 300, "elapsed": 7, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
dfr = dfr.with_columns([
    pl.col('fiscal_year').cast(pl.UInt16),
    pl.col(['general_fund', 'federal_fund', 'capital_fund', 'special_fund']).cast(pl.Decimal(scale=2)),
    pl.col('category').cast(pl.Categorical),
])
# dfr.head(5) # uncomment to preview data in notebook

# %% [markdown] id="rNgGRGgvZXYV"
# ## Load Data to Google Drive in Parquet format

# %% id="HgZ30O8_ZWuN" colab={"base_uri": "https://localhost:8080/"} executionInfo={"status": "ok", "timestamp": 1771906722269, "user_tz": 300, "elapsed": 244, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="8f9cee83-9296-4b94-9dc8-df12ef2bfb8c"
save_df(dfe, 'ex')
save_df(dfr, 'rev')
