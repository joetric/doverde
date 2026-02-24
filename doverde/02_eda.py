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

# %% id="LvLzrQitlfh_" colab={"base_uri": "https://localhost:8080/"} executionInfo={"status": "ok", "timestamp": 1771896278762, "user_tz": 300, "elapsed": 64015, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="7f970b59-2a3e-4f56-d5d1-7cdb5bd2a0bc"
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

# %% id="bWLLM-cw6XpQ"
data_dir = Path(cfg.paths.raw_dir)
Dial
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

# %% id="n3Gb5D6PFTk6"
_conditional = pl.col('fiscal_year') != 2026
dfr = dfr.filter(_conditional)
dfe = dfe.filter(_conditional)

# %% [markdown] id="UKTaGZKdAfrA"
# ## Explore Revenue
#
# clean null data; add sum col; view shape, dtypes and data

# %% colab={"base_uri": "https://localhost:8080/", "height": 680} id="dYG4Z8pj_J6m" executionInfo={"status": "ok", "timestamp": 1771896281161, "user_tz": 300, "elapsed": 1043, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="8c084378-fa04-4a97-ab16-42bfb7ac8a29"
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

# %% colab={"base_uri": "https://localhost:8080/", "height": 662} id="USrLjVeVtTSm" executionInfo={"status": "ok", "timestamp": 1771896281193, "user_tz": 300, "elapsed": 27, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="691390a3-fc2b-4429-fca2-166ecfaa3b98"
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

# %% colab={"base_uri": "https://localhost:8080/", "height": 130} id="a647f474" executionInfo={"status": "ok", "timestamp": 1771896281213, "user_tz": 300, "elapsed": 16, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="76c73dbc-cd23-49cc-d441-e6fe933aaaa2"
# ID what categories have values in multiple funds
# ie. ID multi-fund entries
dfr_non_single_fund = grouped_dfr.with_columns(
    pl.sum_horizontal(cs.contains('fund') != 0).alias('multifund_cat_count')
).filter(pl.col('multifund_cat_count') > 1)

print(f'{dfr_non_single_fund.shape=}')
dfr_non_single_fund.to_pandas(use_pyarrow_extension_array=True)

# %% [markdown] id="e2QZ1Km4c7NU"
# ### Pivot Revenue by FY, indexed on category (value = total rev.)

# %% colab={"base_uri": "https://localhost:8080/", "height": 645} id="FHK3MrQ5RDvG" executionInfo={"status": "ok", "timestamp": 1771896281240, "user_tz": 300, "elapsed": 23, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="7d760c8e-5eb7-46c9-8b60-0223b0476079"
dfr_pivot = dfr.pivot("fiscal_year", index="category", values="total")
dfr_pivot.to_pandas(use_pyarrow_extension_array=True).fillna(0) # display as pd df

# %% [markdown] id="CcnQBQB_QuLy"
# Good - no null values

# %% [markdown] id="OH6cBg4mAg8b"
# ## Explore Payments

# %% colab={"base_uri": "https://localhost:8080/", "height": 255} id="Sr_gL6GXAiFJ" executionInfo={"status": "ok", "timestamp": 1771896281259, "user_tz": 300, "elapsed": 15, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="29f75fe6-0b2b-4957-c41c-a8013a990f50"
dfe.head(5)

# %% [markdown] id="LZyZXv3dhipI"
# ### Pivot Payments by Category and FY

# %% colab={"base_uri": "https://localhost:8080/", "height": 825} id="TrM1J9fBh1X3" executionInfo={"status": "ok", "timestamp": 1771896281279, "user_tz": 300, "elapsed": 27, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="33be569e-7343-4e18-8884-ae09bdbea974"
# Pivot by Category and FY
dfe_pivot_cat_pd = (dfe.group_by(['category', 'fiscal_year'])
 .agg(pl.col('amount').sum())
 .sort('fiscal_year', 'amount', descending=True)
 .pivot(on='fiscal_year', index='category', values='amount')
 .to_pandas(use_pyarrow_extension_array=True)
 .sort_values('2025', ascending=False)
#  .fillna(0)
)
pl.write_csv('', dfe_pivot_cat_pd)
dfe_pivot_cat_pd
dfe_pivot_cat_pd

# %% [markdown] id="8a31HNVKYh_a"
# ### Pivot Payments by Vendor and FY

# %% id="kcU3skOR6fD0"
# CLEAN DATA
# would have to cast vendor to str, then back to cat - really not needed for our analysis
# without this, the below code won't work, but gives an idea of what this would look like
# dfe = dfe.with_columns(
#     pl.col('vendor').str.replace_all('SAUL EWING ARNSTEIN & LEHR LLP', 'SAUL EWING LLP')
# )

# %% colab={"base_uri": "https://localhost:8080/", "height": 645} id="C80iNeO1Pz3w" executionInfo={"status": "ok", "timestamp": 1771896281450, "user_tz": 300, "elapsed": 159, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="f9345438-7b76-4f33-dd6c-e26f22370084"
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
