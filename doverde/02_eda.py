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
# # EDA & Classification: DNREC DPR Revenue and Expenses

# %% [markdown] id="IG85ghvsAcJx"
# ## Setup

# %% id="LvLzrQitlfh_" colab={"base_uri": "https://localhost:8080/"} executionInfo={"status": "ok", "timestamp": 1771883056626, "user_tz": 300, "elapsed": 1885, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="c08f780d-a527-4dbd-abc2-5e7a858b5fe8"
import sys
from datetime import date
from pathlib import Path

from google.colab import data_table, drive
# import missingno as msno
import polars as pl
import polars.selectors as cs

drive.mount('/content/drive')
sys.path.append('/content/drive/MyDrive/dnrec_dpr_revex_engine/dpr_revex')
from config import cfg, FISC_PD_TO_CAL_MO

data_table.enable_dataframe_formatter()

# %% [markdown] id="30aBKmeUAWqI"
# ## Load files to DataFrames

# %% id="bWLLM-cw6XpQ" executionInfo={"status": "ok", "timestamp": 1771883056792, "user_tz": 300, "elapsed": 136, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
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

# %% id="n3Gb5D6PFTk6" executionInfo={"status": "ok", "timestamp": 1771883056845, "user_tz": 300, "elapsed": 32, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
_conditional = pl.col('fiscal_year') != 2026
dfr = dfr.filter(_conditional)
dfe = dfe.filter(_conditional)

# %% [markdown] id="UKTaGZKdAfrA"
# ## Explore Revenue
#
# clean null data; add sum col; view shape, dtypes and data

# %% colab={"base_uri": "https://localhost:8080/", "height": 700} id="dYG4Z8pj_J6m" executionInfo={"status": "ok", "timestamp": 1771883058617, "user_tz": 300, "elapsed": 1769, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="40996c42-0b58-4780-aa9d-6c2d4b6d8fc1"
dfr = (dfr
    .fill_nan(0)
    .with_columns(pl.sum_horizontal(cs.ends_with('fund')).alias('total'))
)

print(f'{dfr.dtypes=}')
print(f'{dfr.shape=}')

dfr_pd = dfr.to_pandas(use_pyarrow_extension_array=True) # don't have time to learn Polars | also Colab data_table only takes Pandas
dfr_pd

# %% [markdown] id="3hlnnWn4Ol2x"
# ### Casually observed anomalies
#
# *   \$1.4M revenue in FY22 - microfilm sales
# *   $9K in revenuein FY22 - Medicare Part A
# *   No workshops in FY21 (expected)
#
#

# %% [markdown] id="d_QDqAsTtVMt"
# ### Group and aggregate by category, ignoring FY

# %% colab={"base_uri": "https://localhost:8080/", "height": 662} id="USrLjVeVtTSm" executionInfo={"status": "ok", "timestamp": 1771883058653, "user_tz": 300, "elapsed": 31, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="4b9c16b8-65b7-48ce-a24f-19e7c1b70808"
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

# %% colab={"base_uri": "https://localhost:8080/", "height": 130} id="a647f474" executionInfo={"status": "ok", "timestamp": 1771883058982, "user_tz": 300, "elapsed": 326, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="450082b9-59eb-4075-82bb-2db4a16761bc"
# ID what categories have values in multiple funds
# ie. ID multi-fund entries
dfr_non_single_fund = grouped_dfr.with_columns(
    pl.sum_horizontal(cs.contains('fund') != 0).alias('multifund_cat_count')
).filter(pl.col('multifund_cat_count') > 1)

print(f'{dfr_non_single_fund.shape=}')
dfr_non_single_fund.to_pandas(use_pyarrow_extension_array=True)

# %% [markdown] id="e2QZ1Km4c7NU"
# ### Pivot Revenue by FY, indexed on category (value = total rev.)

# %% colab={"base_uri": "https://localhost:8080/", "height": 645} id="FHK3MrQ5RDvG" executionInfo={"status": "ok", "timestamp": 1771883058997, "user_tz": 300, "elapsed": 10, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="aa3781bb-eb93-4ab8-9e29-01f0b8644237"
dfr_pivot = dfr.pivot("fiscal_year", index="category", values="total")
dfr_pivot.to_pandas(use_pyarrow_extension_array=True).fillna(0) # display as pd df

# %% [markdown] id="CcnQBQB_QuLy"
# Good - no null values

# %% [markdown] id="OH6cBg4mAg8b"
# ## Explore Payments

# %% colab={"base_uri": "https://localhost:8080/", "height": 255} id="Sr_gL6GXAiFJ" executionInfo={"status": "ok", "timestamp": 1771883059008, "user_tz": 300, "elapsed": 13, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="63541801-eb30-4b21-82bf-c0ec8af490bd"
dfe.head(5)

# %% [markdown] id="8a31HNVKYh_a"
# ### Pivot Payments by Vendor and FY

# %% id="kcU3skOR6fD0" executionInfo={"status": "ok", "timestamp": 1771883059038, "user_tz": 300, "elapsed": 28, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
# CLEAN DATA
# would have to cast vendor to str, then back to cat - really not needed for our analysis
# without this, the below code won't work, but gives an idea of what this would look like
# dfe = dfe.with_columns(
#     pl.col('vendor').str.replace_all('SAUL EWING ARNSTEIN & LEHR LLP', 'SAUL EWING LLP')
# )

# %% colab={"base_uri": "https://localhost:8080/", "height": 645} id="C80iNeO1Pz3w" executionInfo={"status": "ok", "timestamp": 1771883059765, "user_tz": 300, "elapsed": 721, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="7a6c8de1-139d-4015-9ae8-1b7feabc644e"
# Pivot by Vendor and FY
dfe_pivot_pd = (dfe.group_by(['vendor', 'fiscal_year'])
 .agg(pl.col('amount').sum())
 .sort('fiscal_year', 'amount', descending=True)
 .pivot(on='fiscal_year', index='vendor', values='amount')
 .to_pandas(use_pyarrow_extension_array=True)
 .sort_values('2025', ascending=False)
#  .fillna(0)
)
#TODO: automatically save Excel file to Google Drive
dfe_pivot_pd

# %% [markdown] id="zf92uDM_5NJf"
# ### Classify Vendors (Payees)
#
# Vendor pivot table was exported to Excel for manual tagging. Pareto analysis was used to only tag "vendors" that comprised the top 95% of total spending. (~200/1200).
#
# Note: "Vendor" can be a misnomer in this table as it includes items like payroll expenses and benefits. Vendors also include other agencies outside of DPR.
#
# The following script loads the Excel file and merges it to the payment data frame.

# %% colab={"base_uri": "https://localhost:8080/"} id="CBAhMXf3B-Bu" executionInfo={"status": "ok", "timestamp": 1771883067406, "user_tz": 300, "elapsed": 7634, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="c337c204-5e02-4487-eee0-0b499327aa4e"
# load Excel to Polars
# merge on idx
# !pip install -q fastexcel
df_exp_class = (
    pl.read_excel('/content/drive/MyDrive/dnrec_dpr_revex_engine/data/classified/manual-exp-classification.xlsx')
    .select([
        # 'index',
        'vendor',
        'my_classification',
    ])
)
# explore new loaded DF just as a sanity check
print(f'{df_exp_class.shape=}')
print(f'{df_exp_class.dtypes=}')

dfe = (dfe.with_columns(pl.col('vendor').cast(pl.String))
    .join(df_exp_class, on='vendor')
    .with_columns(pl.col('my_classification').cast(pl.Categorical))
)

dfe.write_csv('/content/drive/MyDrive/dnrec_dpr_revex_engine/data/processed/exp.csv') #for tableau

# %% colab={"base_uri": "https://localhost:8080/", "height": 443} id="tldoVh2ZKFFa" executionInfo={"status": "ok", "timestamp": 1771883067452, "user_tz": 300, "elapsed": 38, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="d413aec6-6d6c-40e2-a26d-c846318db21f"
dfe # too many rows for Google data_table (20K limit)

# %% [markdown] id="_sLC2W2rcyHQ"
# ### View unique payment classifications
#
# Helps verify that we are using the correct copy of the Excel file. Session restart required if Excel file updated.

# %% colab={"base_uri": "https://localhost:8080/", "height": 680} id="r_0xr9rCcaN-" executionInfo={"status": "ok", "timestamp": 1771883067463, "user_tz": 300, "elapsed": 8, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="52efdffc-32b9-42b4-9638-0525dd4e3703"
dfe['my_classification'].unique().to_pandas()
