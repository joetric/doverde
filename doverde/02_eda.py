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

# %% id="LvLzrQitlfh_" colab={"base_uri": "https://localhost:8080/"} executionInfo={"status": "ok", "timestamp": 1772563728778, "user_tz": 300, "elapsed": 678, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="481d6ab4-6a10-4ecc-f4ad-ca13a10b9199"
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

CURRENT_FY = 2026
LAST_FY_STR = '2025' #TODO: make dynamic function for current FY (then can just do -1)
DATA_DIR = Path(cfg.paths.raw_dir)

data_table.enable_dataframe_formatter()

# %% [markdown] id="30aBKmeUAWqI"
# ## Load files to DataFrames; filter tables

# %% id="bWLLM-cw6XpQ" executionInfo={"status": "ok", "timestamp": 1772563728860, "user_tz": 300, "elapsed": 86, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
# create conditional to include current, incomplete FY
_conditional = pl.col('fiscal_year') != CURRENT_FY

dfr = pl.read_parquet(DATA_DIR / 'rev.parquet').filter(_conditional)
dfe = pl.read_parquet(DATA_DIR / 'ex.parquet').filter(_conditional)

# %% [markdown] id="UKTaGZKdAfrA"
# ## Explore Revenue
#
# clean null data; add sum col; view shape, dtypes and data

# %% id="dYG4Z8pj_J6m" executionInfo={"status": "ok", "timestamp": 1772563729490, "user_tz": 300, "elapsed": 615, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/", "height": 692} outputId="0f5660a6-e23a-4647-90d3-afcc2bda4e63"
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

# %% id="USrLjVeVtTSm" executionInfo={"status": "ok", "timestamp": 1772563729548, "user_tz": 300, "elapsed": 54, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/", "height": 704} outputId="c5c47023-0ece-4ee4-e880-a5ce60929eb9"
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

# %% id="a647f474" executionInfo={"status": "ok", "timestamp": 1772563729558, "user_tz": 300, "elapsed": 7, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/", "height": 157} outputId="c74790c6-c305-48d8-cbd2-08f1c6b7e80f"
# ID what categories have values in multiple funds
# ie. ID multi-fund entries
dfr_non_single_fund = grouped_dfr.with_columns(
    pl.sum_horizontal(cs.contains('fund') != 0).alias('multifund_cat_count')
).filter(pl.col('multifund_cat_count') > 1)

print(f'{dfr_non_single_fund.shape=}')
dfr_non_single_fund.to_pandas(use_pyarrow_extension_array=True)

# %% [markdown] id="e2QZ1Km4c7NU"
# ### Pivot Revenue by FY, indexed on category (value = total rev.)

# %% id="FHK3MrQ5RDvG" executionInfo={"status": "ok", "timestamp": 1772563729576, "user_tz": 300, "elapsed": 16, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/", "height": 732} outputId="5538a743-b051-4397-a7c0-845906d4b175"
dfr_pivot = dfr.pivot("fiscal_year", index="category", values="total")
dfr_pivot.to_pandas(use_pyarrow_extension_array=True).fillna(0) # display as pd df

# %% [markdown] id="CcnQBQB_QuLy"
# Good - no null values

# %% [markdown] id="OH6cBg4mAg8b"
# ## Explore Payments

# %% id="Sr_gL6GXAiFJ" executionInfo={"status": "ok", "timestamp": 1772563729583, "user_tz": 300, "elapsed": 5, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/", "height": 411} outputId="39222846-0797-4958-e823-9cbf0bf1b468"
dfe.head(5)

# %% [markdown] id="LZyZXv3dhipI"
# ### Pivot Payments by Category and FY

# %% id="TrM1J9fBh1X3" executionInfo={"status": "ok", "timestamp": 1772563729725, "user_tz": 300, "elapsed": 140, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/", "height": 864} outputId="9dd725c0-90d6-4203-a8ee-dabdf710332d"
# Pivot by Category and FY
dfe_pivot_cat_pd = (dfe.group_by(['category', 'fiscal_year'])
 .agg(pl.col('amount').sum())
 .sort('fiscal_year', 'amount', descending=True)
 .pivot(on='fiscal_year', index='category', values='amount')
 .to_pandas(use_pyarrow_extension_array=True)
 .sort_values(LAST_FY_STR, ascending=False)
#  .fillna(0)
)
# pl.write_csv('', dfe_pivot_cat_pd)
dfe_pivot_cat_pd

# %% [markdown] id="8a31HNVKYh_a"
# ### Pivot Payments by Vendor and FY

# %% id="kcU3skOR6fD0" executionInfo={"status": "ok", "timestamp": 1772563729755, "user_tz": 300, "elapsed": 4, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
# CLEAN DATA
# would have to cast vendor to str, then back to cat - really not needed for our analysis
# without this, the below code won't work, but gives an idea of what this would look like
# dfe = dfe.with_columns(
#     pl.col('vendor').str.replace_all('SAUL EWING ARNSTEIN & LEHR LLP', 'SAUL EWING LLP')
# )

# %% id="C80iNeO1Pz3w" executionInfo={"status": "ok", "timestamp": 1772563731143, "user_tz": 300, "elapsed": 1385, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/", "height": 1166} outputId="a79e406f-ac22-4b4f-a53f-39a26b65300d"
# Pivot by Vendor and FY
dfe_pivot_vend_pd = (dfe.group_by(['vendor', 'fiscal_year'])
 .agg(pl.col('amount').sum())
 .sort('fiscal_year', 'amount', descending=True)
 .pivot(on='fiscal_year', index='vendor', values='amount')
 .to_pandas(use_pyarrow_extension_array=True)
 .sort_values(LAST_FY_STR, ascending=False)
#  .fillna(0)
)
dfe_pivot_vend_pd
