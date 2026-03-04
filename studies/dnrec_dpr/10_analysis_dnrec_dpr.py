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

# %% [markdown] id="Y4eIhr2QPBon"
# # DNREC Division of Parks and Recreation ASF Analyses
#
# compiled by Joseph Tricarico, 3 Mar 2026
#     
# **Sample analyses using Delaware Open Vendor Expense and Revenue Data Engine (DOVERDE)**
#
# *   Seasonal variation in DPR benefits-to-wages ratio
#
# *   List item
#
#

# %% [markdown] id="mWWo64nRweOg"
# ## Setup

# %% colab={"base_uri": "https://localhost:8080/"} id="o7bEEtIDAlgU" executionInfo={"status": "ok", "timestamp": 1772585572086, "user_tz": 300, "elapsed": 8780, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="28fb7964-1a68-4013-efa5-067989768d14"
#SETUP
import sys
from datetime import date
from pathlib import Path

# !pip -q install adjustText
from adjustText import adjust_text
from google.colab import data_table, drive
import matplotlib.pyplot as plt
import polars as pl
import polars.selectors as cs
import seaborn as sns
from scipy import stats

__author__ = "Joseph R. Tricarico"

drive.mount('/content/drive')
sys.path.append('/content/drive/MyDrive/doverde/doverde')
from config import cfg, FISC_PD_TO_CAL_MO

# --- SETTINGS FOR THIS FILE ---
CURRENT_FY = 2026 #TODO make dynamic function
LAST_FY_STR = str(CURRENT_FY - 1)
DATA_DIR = Path(cfg.paths.raw_dir)
FIG_DIR = Path('/content/drive/MyDrive/doverde/studies/dnrec_dpr/figs')
SALARY_CATS = [
    'SALARIES/WAGES-EMPLOYEES',
    'CASUAL & SEASONAL SALS',
    'TEMPORARY EMPLOYMENT SERVICE',
    'OVERTIME SALARIES',
    'HOLIDAY PAY - PREMIUM',
    'STIPENDS',
    'SHIFT DIFFERENTIAL SALARY',
    'HAZARDOUS DUTY SALARIES',
    'CALLBACK PAY',
    'STANDBY PAY',
    'TERMINATION SALS-VAC LEAVE',
    'TERMINATION SALS-SICK LEAVE',
    'ONE-TIME SUPPLEMENTAL SALARY',
]
BENEFITS_CATS = [
    "PENSIONS/EMPLOYER'S SHARE",
    "HEALTH INS/EMPLOYERS' SH",
    'EMPLYR SH/SOCIAL SECURITY',
    "WORKMEN'S COMPENSATION",
    "EMPLOYER'S SHARE-MEDICARE",
    'UNEMPLOYMENT INS BENEFITS',
    'HEALTH INSURANCE',
    'ACA PENALTY',
    'FMLY CARE LVE BNFTS EMPLR SHR',
    'DENTAL PLAN',
    'GROUP LIFE INSURANCE',
    'FLEX CREDIT VISION',
    'OTHER EMPLOYEE BENEFITS',
]
COLORS = {
    'seashore_blue': '#004b87', # primary
    'grass_green': '#43b02a', # primary
    'sunset_orange': '#EF9600', # secondary
    'park_sign_brown': '#693F23', # secondary
    'bay_blue': '#007398',
    'sunrise_yellow': '#FAE053',
    'bark_brown': '#31261D',
    'sand_tan': '#DDCBA4',
}

 # use Colab data tables (must convert to Pandas before displaying)
data_table.enable_dataframe_formatter()

# %% [markdown] id="fcUfu1yXwgGi"
# ## Filter and load data

# %% id="4DbhjVXTwaSI" executionInfo={"status": "ok", "timestamp": 1772585572145, "user_tz": 300, "elapsed": 14, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
# --- FILTER AND LOAD DATA ---
fy_range_cond = pl.col('fiscal_year') != CURRENT_FY
# load dfr "data frame: revenue"
dfr = (pl.read_parquet(DATA_DIR / 'rev.parquet')
    .filter(fy_range_cond)
    .filter(pl.col('special_fund') > 0) # ASF only
    .filter(pl.col('category') != 'MICROFILM SALES') # obvious error
    .drop(['general_fund', 'federal_fund', 'capital_fund'])
)# load dfe "data frame: expenses" - really payments; a bit of a misnomer
dfe = (pl.read_parquet(DATA_DIR / 'ex.parquet')
    .filter(fy_range_cond)
    .filter(pl.col('fund_type') == 'SPECIAL') #ASF only
    .drop('fund_type') # all 'SPECIAL' now, so no need for this col
    .drop('check_number') # not used (could also comment out on config.yaml)
    .drop('vendor') # not used (could also comment out on config.yaml)
)

# %% [markdown] id="RHdPLWU6i8qW"
# ## EDA

# %% [markdown] id="v_vGN5J9hfjz"
# ### Explore revenue by category

# %% colab={"base_uri": "https://localhost:8080/", "height": 0} cellView="form" id="nqPN2sR3gpYj" executionInfo={"status": "ok", "timestamp": 1772585572225, "user_tz": 300, "elapsed": 78, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="ef51c103-4cbf-4329-d236-b794fed9b2fe"
# @title
dfr.group_by('category').agg(pl.sum('special_fund')).sort('special_fund', descending=True).to_pandas()

# %% [markdown] id="2w1NXB3ghI5H"
# ### Explore payments by category

# %% colab={"base_uri": "https://localhost:8080/", "height": 0} id="25776306" executionInfo={"status": "ok", "timestamp": 1772585572260, "user_tz": 300, "elapsed": 33, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="ca2c8a51-5105-46db-be49-b59adf8f191e"
category_amounts = dfe.group_by('category').agg(pl.sum('amount').alias('total_amount')).sort('total_amount', descending=True)
display(category_amounts.to_pandas())

# %% [markdown] id="Px1GBKOdjfAa"
# ## Benefits-to-wages ratio analysis
#
# *   t-test: summer v. offseason
# *   ANOVA: across 12 months

# %% colab={"base_uri": "https://localhost:8080/", "height": 284} id="8FoRg8ZbDgzW" executionInfo={"status": "ok", "timestamp": 1772585572280, "user_tz": 300, "elapsed": 19, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="74dced65-0249-4359-9858-e648c073ea1a"
# make new column for labor expense type: SALARY|BENEFITS or null
dfe = dfe.with_columns(
    pl.when(pl.col.category.is_in(SALARY_CATS)).then(pl.lit('salary'))
    .when(pl.col.category.is_in(BENEFITS_CATS)).then(pl.lit('benefits'))
    # .otherwise(pl.lit('OTHER')) # removed--confusing because not labor expense
    .alias('labor_exp_type')
    .cast(pl.Categorical)
)

# group / pivot labor costs by month and type
labor = dfe.filter(pl.col('labor_exp_type').is_not_null())
mo_lab = (
    labor
    .with_columns(pl.col('check_date').dt.year().alias('yr'),
                  pl.col('check_date').dt.month().alias('mo'))
    .group_by(['yr', 'mo', 'labor_exp_type'])
    .agg(pl.col('amount').sum())
    .pivot(on='labor_exp_type', index=['yr', 'mo'], values='amount')
    .fill_null(0)
    .with_columns(
        (100 * pl.col('benefits') / pl.col('salary')).alias('ratio_pct')
    )
    .sort(['yr', 'mo'])
)

mo_lab.describe().to_pandas().round(1) # show descriptive stats

# %% [markdown] id="netXb3MktlRI"
# ### Summer v. offseason test
#
# Distribution of summer monthly benefit-to-wage ratio
#
# #### Definitions
# **Summer** is June through August.
# **Offseason** is the rest of the year.
# **Wages** are salaries and wages.
#
# #### Hypotheses
# H<sub>0</sub>: Mean monthly benefit-to-salary ratio is the same in summer and offseason months.
#
# H<sub>1</sub>: Mean monthly benefit-to-salary is lower in summer months.

# %% id="croQ1vW9wEau" executionInfo={"status": "ok", "timestamp": 1772585572289, "user_tz": 300, "elapsed": 2, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
summer_cond = pl.col.mo.is_between(6, 8)
summer = mo_lab.filter(summer_cond)['ratio_pct'].cast(pl.Float64) # need to cast for some stats test to work
offseason = mo_lab.filter(~summer_cond)['ratio_pct'].cast(pl.Float64)

# %% [markdown] id="ryO7AhaRuPcv"
# #### Check t-test assumptions

# %% [markdown] id="S5cNOcjY3I9B"
# ##### Normality
#
# Shapiro-Wilk test indicates summer months are *not* normal (p < 0.05)

# %% colab={"base_uri": "https://localhost:8080/", "height": 514} id="tIzTb7hSwkTW" executionInfo={"status": "ok", "timestamp": 1772585572955, "user_tz": 300, "elapsed": 664, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="b1e55651-6062-4e0f-93da-e7f0254825e0"
# --- CHECK NORMALITY ---

# PLOT HISTOGRAMS
fig = plt.figure(figsize=(5, 4))
# Uncomment for side-by-side (use plt.sublots)
# sns.histplot(summer, ax=axes[0], kde=True).set_title('Summer')
# sns.histplot(offseason, ax=axes[1], kde=True).set_title('Offseason')
bins = range(15, 40, 1)
plot_kws = {'alpha': 0.4, 'kde': True, 'bins': bins}
sns.histplot(summer, color=COLORS['sunset_orange'], label='June-August', **plot_kws)
sns.histplot(offseason, color=COLORS['bay_blue'], label='Offseason', **plot_kws)
plt.xlabel('Benefits-to-wages ratio (%)')
plt.ylabel('Frequency')
plt.legend()
plt.title('DNREC DPR monthly benefits-to-wages distribution\nFY 2018-2025')
plt.tight_layout()
plt.savefig(FIG_DIR / '01_hist.png', dpi=300, bbox_inches='tight')
plt.show()

print('\n\nSHAPIRO-WILK TESTS')
print(f'{stats.shapiro(summer)=}')
print(f'{stats.shapiro(offseason)=}')

# %% [markdown] id="tDLwheCA3Pvx"
# #### Mann-Whitney U test
#
# A Mann-Whitney U test indicated that the benefits-to-salary ratio was significantly lower in summer months (Jun–Aug) (*Mdn* = 18.8%) than non-summer months (*Mdn* = 28.4%), U = 49.5, *p* < .001. This is consistent with the hypothesis that seasonal workers receive wages but limited employer-paid benefits, reducing the overall benefits share during peak staffing months.
#

# %% colab={"base_uri": "https://localhost:8080/"} id="liI8jjhe79Cr" executionInfo={"status": "ok", "timestamp": 1772585572965, "user_tz": 300, "elapsed": 8, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="8218ac62-38d2-4440-d04c-e535de5c4d60"
u, p = stats.mannwhitneyu(
    summer.to_list(), # function takes list but not Polars structure
    offseason.to_list(),
    alternative='less', # tests 1st arg is less than 2nd
)
# p-value (regular and rounded print)
print(f'{p=}') # added this to make sure 0.000000 wasn't some error
print(f'{p=:.6f}')

# times summer value is less than on-summer when all 1,728 possible pairs are tests
print(f'{u=:.1f}')

# compare measurements of central tendency
print(f'{summer.mean()=:.1f}; {offseason.mean()=:.1f}')
print(f'{summer.median()=:.1f}; {offseason.median()=:.1f}')


# %% [markdown] id="s0VzoMXttoVB"
# ### Monthly ANOVA
#
# This section reserved for future use.

# %% [markdown] id="H0xr5UkjE7tD"
# ## State minimum wage v. casual and seasonal wages
#
#

# %% colab={"base_uri": "https://localhost:8080/", "height": 611} id="dLjNE7_BHjp2" executionInfo={"status": "ok", "timestamp": 1772585697902, "user_tz": 300, "elapsed": 1045, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="74344076-3ff7-4804-f342-538e2815a23b"
def get_de_min_wage(yr, mo):
    """Takes year and month, returns DE state min wage

    Federal Reserve (FRED) data is wrong.
    It shows the min wage for the 1st of each year,
    but even this is wrong (e.g. 1/1/19 was 8.75, not 9.25)
    https://fred.stlouisfed.org/data/STTMINWGDE

    2019 increases:
    https://news.delaware.gov/2018/12/18/minimum-wage-increases-january-1st/

    2022-2025 increases: 2021 Senate Bill 15
    """
    if (yr, mo) >= (2025, 1): return 15.00
    if (yr, mo) >= (2024, 1): return 13.25
    if (yr, mo) >= (2023, 1): return 11.75
    if (yr, mo) >= (2022, 1): return 10.50
    if (yr, mo) >= (2019, 10): return 9.25
    if (yr, mo) >= (2019, 1): return 8.75 # Federal Reserve gets this wrong!
    return 8.25

monthly_casual_seasonal_salaries = (dfe
    .filter(pl.col('category') == 'CASUAL & SEASONAL SALS')
    .with_columns(pl.col('check_date').dt.year().alias('yr'),
                  pl.col('check_date').dt.month().alias('mo'))
    .group_by(['yr', 'mo', 'fiscal_year'])
    .agg(pl.col('amount').sum())
    .sort(['yr', 'mo'])
    .with_columns(
        pl.struct('yr', 'mo')
        .map_elements(lambda x: get_de_min_wage(x['yr'], x['mo']))
        .alias('de_min_wage')
    )
)
annual_casual_seasonal_salaries = (monthly_casual_seasonal_salaries
    # .filter(pl.col('yr') < 2025) #
    .group_by('fiscal_year').agg([
        pl.col('amount').sum().alias('annual_wages'),
        pl.col('de_min_wage').mean().alias('de_min_wage'),
    ]).sort('fiscal_year')
)

# explore data
# print('\n\nmonthly_casual_seasonal_salaries')
# display(monthly_casual_seasonal_salaries.to_pandas())
# print('\n\nannual_casual_seasonal_salaries')
# display(annual_casual_seasonal_salaries.to_pandas())

# make scatterplot
fig = plt.figure(figsize=(5, 4))
sns.relplot(
    data=annual_casual_seasonal_salaries.to_pandas(),
    x='de_min_wage', y='annual_wages', kind='scatter')
plt.title('State minimum wage v.\nFY annual casual/seasonal salary spend')

texts = []
for row in annual_casual_seasonal_salaries.iter_rows(named=True):
    texts.append(
        plt.annotate(f"FY{row['fiscal_year'] % 100}",
            (row['de_min_wage'], row['annual_wages']),
            color=COLORS['seashore_blue'],
            fontfamily='sans-serif', # close to Lato
            fontsize=9, xytext=(5, 5), textcoords='offset points')
    )
# adjust_text(texts)

plt.xlabel('Average annual state minimum wage (USD)')
plt.ylabel('Annual casual/seasonal salary/wage spend (millions/USD)')
plt.savefig(FIG_DIR / '10_min_wg_v_yrly_cas_salary.png', dpi=300, bbox_inches='tight')
plt.tight_layout()
plt.show()

# run Pearson's correlation coefficient
r, p = stats.pearsonr(
    annual_casual_seasonal_salaries['de_min_wage'].cast(pl.Float64),
    annual_casual_seasonal_salaries['annual_wages'].cast(pl.Float64)
)
print('\n\nPearson\'s correlation coefficient')
print(f'{r=}')
print(f'{p=}')

# %% [markdown] id="CvT_o7g9YXkS"
# ## Revenue analysis
#
# Descriptive statistics across fiscal years

# %% colab={"base_uri": "https://localhost:8080/", "height": 637} id="4fCxKHBzYc1b" executionInfo={"status": "ok", "timestamp": 1772587240782, "user_tz": 300, "elapsed": 339, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="a0068c7a-be1d-4d2c-b647-a659ff64a20b"
# SUPER IMPORTANT STEP!
# Not all categories are in every year...
# In years where they are missing, we need to fill in zero.
rev_pivot = dfr.pivot(on='fiscal_year', index='category', values='special_fund').fill_null(0)
rev_melt = rev_pivot.unpivot(
    index='category', variable_name='fiscal_year', value_name='special_fund'
)
rev_melt.to_pandas()

rev_stats = (rev_melt.group_by('category').agg([
        pl.col('special_fund').mean().alias('mean'),
        pl.col('special_fund').median().alias('median'),
        pl.col('special_fund').std().alias('std'),
        pl.col('special_fund').min().alias('min'),
        pl.col('special_fund').max().alias('max'),
    ])
    # use integers for all values
    .with_columns(pl.all().exclude('category').cast(pl.Int64))
    .sort('median', descending=True).to_pandas()
)

display(rev_stats)

# %% id="h_fNXeotaBKI"
