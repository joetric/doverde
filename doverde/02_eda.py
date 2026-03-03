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

# %% id="LvLzrQitlfh_" colab={"base_uri": "https://localhost:8080/"} executionInfo={"status": "ok", "timestamp": 1772562845963, "user_tz": 300, "elapsed": 1279, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="4f4cb212-1884-486b-8df1-ccfc433b33b0"
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

LAST_FY_STR = '2025'

data_table.enable_dataframe_formatter()

# %% [markdown] id="30aBKmeUAWqI"
# ## Load files to DataFrames

# %% id="bWLLM-cw6XpQ" executionInfo={"status": "ok", "timestamp": 1772562847663, "user_tz": 300, "elapsed": 1691, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
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

# %% id="n3Gb5D6PFTk6" executionInfo={"status": "ok", "timestamp": 1772562847733, "user_tz": 300, "elapsed": 67, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
_conditional = pl.col('fiscal_year') != 2026
dfr = dfr.filter(_conditional)
dfe = dfe.filter(_conditional)

# %% [markdown] id="UKTaGZKdAfrA"
# ## Explore Revenue
#
# clean null data; add sum col; view shape, dtypes and data

# %% id="dYG4Z8pj_J6m" executionInfo={"status": "ok", "timestamp": 1772562848839, "user_tz": 300, "elapsed": 1104, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/", "height": 787} outputId="446fda25-d13e-4524-8618-197bbe3412ac"
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
# **Example**: Observations in DNREC DPR data. **Replace with your own observations**.
# *   \$1.4M revenue in FY22 - microfilm sales
# *   $9K in revenue in FY22 - Medicare Part A
# *   No workshops in FY21 (expected - COVID-19)
#
#

# %% [markdown] id="d_QDqAsTtVMt"
# ### Group and aggregate by category, ignoring FY

# %% id="USrLjVeVtTSm" executionInfo={"status": "ok", "timestamp": 1772562848852, "user_tz": 300, "elapsed": 10, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/", "height": 931} outputId="9a3b05b6-5e48-4241-a310-c607f16c25a5"
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

# %% id="a647f474" executionInfo={"status": "ok", "timestamp": 1772562848863, "user_tz": 300, "elapsed": 9, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/", "height": 157} outputId="295a7214-e50f-4317-cf84-43b3e72b030c"
# ID what categories have values in multiple funds
# ie. ID multi-fund entries
dfr_non_single_fund = grouped_dfr.with_columns(
    pl.sum_horizontal(cs.contains('fund') != 0).alias('multifund_cat_count')
).filter(pl.col('multifund_cat_count') > 1)

print(f'{dfr_non_single_fund.shape=}')
dfr_non_single_fund.to_pandas(use_pyarrow_extension_array=True)

# %% [markdown] id="e2QZ1Km4c7NU"
# ### Pivot Revenue by FY, indexed on category (value = total rev.)

# %% id="FHK3MrQ5RDvG" executionInfo={"status": "ok", "timestamp": 1772562848880, "user_tz": 300, "elapsed": 16, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/", "height": 732} outputId="1d583c69-e9c5-46ce-9980-1be35e690269"
dfr_pivot = dfr.pivot("fiscal_year", index="category", values="total")
dfr_pivot.to_pandas(use_pyarrow_extension_array=True).fillna(0) # display as pd df

# %% [markdown] id="CcnQBQB_QuLy"
# Good - no null values

# %% [markdown] id="OH6cBg4mAg8b"
# ## Explore Payments

# %% id="Sr_gL6GXAiFJ" executionInfo={"status": "ok", "timestamp": 1772562848887, "user_tz": 300, "elapsed": 5, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/", "height": 483} outputId="7931bf9c-1510-460f-f430-1c4a0a8b46e5"
dfe.head(5)

# %% [markdown] id="LZyZXv3dhipI"
# ### Pivot Payments by Category and FY

# %% id="TrM1J9fBh1X3" executionInfo={"status": "ok", "timestamp": 1772562848938, "user_tz": 300, "elapsed": 49, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/", "height": 864} outputId="bd36e56c-b8c6-4af3-9892-549a09fb1db2"
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

# %% id="kcU3skOR6fD0" executionInfo={"status": "ok", "timestamp": 1772562848945, "user_tz": 300, "elapsed": 3, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
# CLEAN DATA
# would have to cast vendor to str, then back to cat - really not needed for our analysis
# without this, the below code won't work, but gives an idea of what this would look like
# dfe = dfe.with_columns(
#     pl.col('vendor').str.replace_all('SAUL EWING ARNSTEIN & LEHR LLP', 'SAUL EWING LLP')
# )

# %% id="C80iNeO1Pz3w" executionInfo={"status": "ok", "timestamp": 1772562849303, "user_tz": 300, "elapsed": 356, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/", "height": 1260} outputId="b66200ed-4746-46b7-8319-cb4aa290c96e"
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
