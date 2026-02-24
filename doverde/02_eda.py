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

# %% [markdown] id="JUxW312z-yhg"
# # EDA & Classification: Revenue and Expenses

# %% [markdown] id="IG85ghvsAcJx"
# ## Setup

# %% id="LvLzrQitlfh_" colab={"base_uri": "https://localhost:8080/"} executionInfo={"status": "ok", "timestamp": 1771906874826, "user_tz": 300, "elapsed": 1383, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="57e46bbc-ee5e-4907-bef9-d3f73281c323"
import sys
from datetime import date
from pathlib import Path

from google.colab import data_table, drive
# import missingno as msno
import polars as pl
import polars.selectors as cs

drive.mount('/content/drive')
sys.path.append('/content/drive/MyDrive/doverde/doverde')
from config import cfg, FISC_PD_TO_CAL_MO

data_table.enable_dataframe_formatter()

# %% [markdown] id="30aBKmeUAWqI"
# ## Load files to DataFrames

# %% id="bWLLM-cw6XpQ" executionInfo={"status": "ok", "timestamp": 1771906875032, "user_tz": 300, "elapsed": 166, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
data_dir = Path(cfg.paths.raw_dir)
rev_file = Path(data_dir) / 'rev.parquet'
dfr = pl.read_parquet(rev_file)

ex_file = Path(data_dir) / 'ex.parquet'
dfe = pl.read_parquet(ex_file)

# %% [markdown] id="me1RSIIDFM-v"
# ## Engineer both tables
#
# *   Drop FY 2026 (it is incomplete)
# <!-- *   List item -->
#
#

# %% id="n3Gb5D6PFTk6" executionInfo={"status": "ok", "timestamp": 1771906875076, "user_tz": 300, "elapsed": 8, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
_conditional = pl.col('fiscal_year') != 2026
dfr = dfr.filter(_conditional)
dfe = dfe.filter(_conditional)

# %% [markdown] id="UKTaGZKdAfrA"
# ## Explore Revenue
#
# clean null data; add sum col; view shape, dtypes and data

# %% id="dYG4Z8pj_J6m" executionInfo={"status": "ok", "timestamp": 1771906876747, "user_tz": 300, "elapsed": 1675, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/", "height": 700} outputId="93d46ffe-edb6-4495-907a-1240cdb59ae3"
dfr = (dfr
    .fill_nan(0)
    .with_columns(pl.sum_horizontal(cs.ends_with('fund')).alias('total'))
)

print(f'{dfr.dtypes=}')
print(f'{dfr.shape=}')

dfr_pd = dfr.to_pandas(use_pyarrow_extension_array=True) # Colab data_table only takes Pandas
dfr_pd

# %% [markdown] id="3hlnnWn4Ol2x"
# ### Casually observed anomalies
#
# Example: Observations in DNREC DPR data. Replace with your own observations.
# *   \$1.4M revenue in FY22 - microfilm sales
# *   $9K in revenue in FY22 - Medicare Part A
# *   No workshops in FY21 (expected - COVID-19)
#
#

# %% [markdown] id="d_QDqAsTtVMt"
# ### Group and aggregate by category, ignoring FY

# %% id="USrLjVeVtTSm" executionInfo={"status": "ok", "timestamp": 1771906876812, "user_tz": 300, "elapsed": 61, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/", "height": 662} outputId="1f94e196-5d1b-4f2f-cc65-8845bff409bb"
grouped_dfr = dfr.group_by('category').agg(
    cs.contains('fund').sum().name.suffix('_sum'),
    pl.col('total').sum().alias('overall_total_sum')
)
print(f'{grouped_dfr.shape=}')
grouped_dfr.to_pandas(use_pyarrow_extension_array=True)

# %% [markdown] id="wLKJLovltkv2"
# ### ID categories with values in multiple funds
#
# 'Prior year adjustment' has non-zero values in multiple fields, which makes sense.

# %% id="a647f474" executionInfo={"status": "ok", "timestamp": 1771906876837, "user_tz": 300, "elapsed": 22, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/", "height": 130} outputId="4963bb26-2a80-491c-9499-31451ff66d99"
# ID what categories have values in multiple funds
# ie. ID multi-fund entries
dfr_non_single_fund = grouped_dfr.with_columns(
    pl.sum_horizontal(cs.contains('fund') != 0).alias('multifund_cat_count')
).filter(pl.col('multifund_cat_count') > 1)

print(f'{dfr_non_single_fund.shape=}')
dfr_non_single_fund.to_pandas(use_pyarrow_extension_array=True)

# %% [markdown] id="e2QZ1Km4c7NU"
# ### Pivot Revenue by FY, indexed on category (value = total rev.)

# %% id="FHK3MrQ5RDvG" executionInfo={"status": "ok", "timestamp": 1771906876925, "user_tz": 300, "elapsed": 85, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/", "height": 645} outputId="00f1c2d0-14fb-4089-92b0-a1ef3863856e"
dfr_pivot = dfr.pivot("fiscal_year", index="category", values="total")
dfr_pivot.to_pandas(use_pyarrow_extension_array=True).fillna(0) # display as pd df

# %% [markdown] id="CcnQBQB_QuLy"
# Good - no null values

# %% [markdown] id="OH6cBg4mAg8b"
# ## Explore Payments

# %% id="Sr_gL6GXAiFJ" executionInfo={"status": "ok", "timestamp": 1771906877000, "user_tz": 300, "elapsed": 72, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/", "height": 255} outputId="67415854-e837-4d7b-dac7-ef08ad5341e1"
dfe.head(5)

# %% [markdown] id="LZyZXv3dhipI"
# ### Pivot Payments by Category and FY

# %% id="TrM1J9fBh1X3" executionInfo={"status": "ok", "timestamp": 1771906889916, "user_tz": 300, "elapsed": 104, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/", "height": 645} outputId="ce8b6885-5e8e-4cac-82d1-2bc6a2f55d3e"
# Pivot by Category and FY
dfe_pivot_cat_pd = (dfe.group_by(['category', 'fiscal_year'])
 .agg(pl.col('amount').sum())
 .sort('fiscal_year', 'amount', descending=True)
 .pivot(on='fiscal_year', index='category', values='amount')
 .to_pandas(use_pyarrow_extension_array=True)
 .sort_values('2025', ascending=False)
#  .fillna(0)
)
# pl.write_csv('', dfe_pivot_cat_pd)
dfe_pivot_cat_pd

# %% [markdown] id="8a31HNVKYh_a"
# ### Pivot Payments by Vendor and FY

# %% id="kcU3skOR6fD0" executionInfo={"status": "ok", "timestamp": 1771906889925, "user_tz": 300, "elapsed": 5, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
# CLEAN DATA
# would have to cast vendor to str, then back to cat - really not needed for our analysis
# without this, the below code won't work, but gives an idea of what this would look like
# dfe = dfe.with_columns(
#     pl.col('vendor').str.replace_all('SAUL EWING ARNSTEIN & LEHR LLP', 'SAUL EWING LLP')
# )

# %% id="C80iNeO1Pz3w" executionInfo={"status": "ok", "timestamp": 1771906890292, "user_tz": 300, "elapsed": 364, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/", "height": 645} outputId="753a5375-0a98-4074-cfd6-aec9e91b8f7d"
# Pivot by Vendor and FY
dfe_pivot_vend_pd = (dfe.group_by(['vendor', 'fiscal_year'])
 .agg(pl.col('amount').sum())
 .sort('fiscal_year', 'amount', descending=True)
 .pivot(on='fiscal_year', index='vendor', values='amount')
 .to_pandas(use_pyarrow_extension_array=True)
 .sort_values('2025', ascending=False)
#  .fillna(0)
)
dfe_pivot_vend_pd
