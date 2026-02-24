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

# %% [markdown] id="8lP7mci0vqPa"
# # Dev Tools
#
# Designed to work with GITHUB_TOKEN set in Google Colab settings.
#
# ### Setup
#
# Run init_repo() and clone_repo() as needed.
#
# ### Workflow
#
# 1.   Converts IPython / Jupyter notebooks to .py files
# 2.   Displays repo status (with git status)
# 3.   Fetches origin and merges into main branch
# 4.   Prompts for commit message
# 5.   Pushes new commit
#
#
#

# %% id="4Mna7DKmvSgF" colab={"base_uri": "https://localhost:8080/", "height": 356} executionInfo={"status": "error", "timestamp": 1771955377232, "user_tz": 300, "elapsed": 121679, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="2c3f325a-d1cd-4e40-b033-f4351d6f90c9"
import os, subprocess, sys
from pathlib import Path
from google.colab import drive, userdata

drive.mount('/content/drive')
PROJ = Path('/content/drive/MyDrive/doverde')
SRC_PATH = str(PROJ / 'doverde')
sys.path.append(SRC_PATH)

REPO = 'joetric/doverde'
GITHUB_TOKEN = userdata.get('GITHUB_TOKEN')


# %% id="noACbGrpv5XK" executionInfo={"status": "aborted", "timestamp": 1771955377215, "user_tz": 300, "elapsed": 121857, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
def clone_repo():
    token = userdata.get('GITHUB_TOKEN') # get GitHub token for colab; repo and content scoped
    result = subprocess.run(
        f'git clone https://{GITHUB_TOKEN}@github.com/{REPO}.git {PROJ}',
        shell=True, capture_output=True, text=True
    )
    print(result.stdout or result.stderr)


def init_repo():
    url = f'https://{GITHUB_TOKEN}@github.com/{REPO}.git'
    cmds = [
        f'git -C {PROJ} init',
        f'git -C {PROJ} remote add origin {url}',
        f'git -C {PROJ} fetch origin',
        f'git -C {PROJ} checkout -b main origin/main --force',
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout or result.stderr)


# init_repo() # uncomment only once to init repo.
# clone_repo() # uncomment only once to clone repo.

# %% [markdown] id="FXd2d8XSvnkv"
# ## Convert Jupyter notebooks to .py

# %% id="f9QtbH1Ru16o" executionInfo={"status": "aborted", "timestamp": 1771955377222, "user_tz": 300, "elapsed": 121860, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
import subprocess

nb_dir = PROJ / 'doverde'
for nb in nb_dir.glob('*.ipynb'):
    result = subprocess.run(['jupytext', '--to', 'py', str(nb)], capture_output=True, text=True)
    print(f'{"✓" if result.returncode == 0 else "✗"} {nb.name}')

# %% [markdown] id="kN7nPAEN0nyQ"
# ## Git commit

# %% id="gkSjkskybFVE" executionInfo={"status": "aborted", "timestamp": 1771955377225, "user_tz": 300, "elapsed": 121860, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
print("--- PRE-COMMIT STATUS ---")
# !git -C {PROJ} status

# %% id="bgHuOEu5vt74" executionInfo={"status": "aborted", "timestamp": 1771955377227, "user_tz": 300, "elapsed": 121859, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
# !git config --global user.email "joseph.tricarico@delaware.gov"
# !git config --global user.name "Joseph Tricarico"
# !git -C {PROJ} pull origin main
# !git -C {PROJ} add *.py *.yaml *.toml *.csv .gitignore
# !git -C {PROJ} status

msg = input('Commit message: ')
# !git -C {PROJ} commit -m "{msg}"
# !git -C {PROJ} push origin main

# %% id="6_o8yoar5XRm" executionInfo={"status": "aborted", "timestamp": 1771955377259, "user_tz": 300, "elapsed": 121888, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
# !git -C {PROJ} pull --rebase origin main
