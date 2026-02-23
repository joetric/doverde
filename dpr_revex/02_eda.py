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
# # EDA: DNREC DPR Revenue and Expenses

# %% [markdown] id="IG85ghvsAcJx"
# ## Setup

# %% id="LvLzrQitlfh_" colab={"base_uri": "https://localhost:8080/"} executionInfo={"status": "ok", "timestamp": 1771629742317, "user_tz": 300, "elapsed": 784, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="1305134c-dcde-417c-e62c-9d939cca7735"
import sys
from pathlib import Path

from google.colab import data_table, drive
import polars as pl
import polars.selectors as cs

drive.mount('/content/drive')
sys.path.append('/content/drive/MyDrive/dnrec_dpr_revex_engine/dpr_revex')
from config import cfg, FISC_PD_TO_CAL_MO

data_table.enable_dataframe_formatter()

# %% [markdown] id="30aBKmeUAWqI"
# ## Load files to DataFrames

# %% id="bWLLM-cw6XpQ" executionInfo={"status": "ok", "timestamp": 1771629742363, "user_tz": 300, "elapsed": 36, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
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

# %% id="n3Gb5D6PFTk6" executionInfo={"status": "ok", "timestamp": 1771629933870, "user_tz": 300, "elapsed": 5, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
_conditional = pl.col('fiscal_year') != 2026
dfr = dfr.filter(_conditional)
dfe = dfe.filter(_conditional)

# %% [markdown] id="UKTaGZKdAfrA"
# ## Explore Revenue

# %% colab={"base_uri": "https://localhost:8080/", "height": 641} id="dYG4Z8pj_J6m" executionInfo={"status": "ok", "timestamp": 1771629934265, "user_tz": 300, "elapsed": 389, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="73a00f2d-c7d3-4c4a-8736-5313c8ff4c9c"
dfr = (dfr
    .with_columns(
        pl.sum_horizontal(cs.ends_with('fund')).alias('total')
    )
)

dfr.to_pandas()

# %% [markdown] id="3hlnnWn4Ol2x"
# ### Casually observed anomalies
#
# *   \$1.4M revenue in FY22 - microfilm sales
# *   $9K in revenuein FY22 - Medicare Part A
# *   No workshops in FY21 (expected)
#
#

# %% [markdown] id="OH6cBg4mAg8b"
# ## Explore Payments

# %% colab={"base_uri": "https://localhost:8080/", "height": 255} id="Sr_gL6GXAiFJ" executionInfo={"status": "ok", "timestamp": 1771630125471, "user_tz": 300, "elapsed": 34, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="4c9194dd-e1f8-4f25-ef16-df3161af1283"
dfe.head(5)

# %% [markdown] id="8a31HNVKYh_a"
# ### Pivot by Vendor and FY

# %% colab={"base_uri": "https://localhost:8080/", "height": 821} id="C80iNeO1Pz3w" executionInfo={"status": "ok", "timestamp": 1771630254395, "user_tz": 300, "elapsed": 521, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="b4ed5069-834e-4f7a-f15d-e2f2c9f3b08d"
(dfe.group_by(['vendor', 'fiscal_year'])
 .agg(pl.col('amount').sum())
 .sort('fiscal_year', 'amount', descending=True)
 .pivot(on='fiscal_year', index='vendor', values='amount')
 .to_pandas(use_pyarrow_extension_array=True)
)
