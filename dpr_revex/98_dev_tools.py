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

# %% colab={"base_uri": "https://localhost:8080/"} id="4Mna7DKmvSgF" executionInfo={"status": "ok", "timestamp": 1771632334999, "user_tz": 300, "elapsed": 22904, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="18424070-f200-4775-90df-81c11e964202"
import os, subprocess, sys
from pathlib import Path
from google.colab import drive, userdata

drive.mount('/content/drive')
PROJ = Path('/content/drive/MyDrive/dnrec_dpr_revex_engine')
sys.path.append(str(PROJ / 'dpr_revex'))

REPO = 'joetric/dnrec-dpr-revex-engine'
GITHUB_TOKEN = userdata.get('GITHUB_TOKEN')


# %% id="noACbGrpv5XK" executionInfo={"status": "ok", "timestamp": 1771632335036, "user_tz": 300, "elapsed": 30, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
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

# %% colab={"base_uri": "https://localhost:8080/"} id="f9QtbH1Ru16o" outputId="a16e9842-b87a-46a7-dcfa-f817d0f05b45"
import subprocess

nb_dir = PROJ / 'dpr_revex'
for nb in nb_dir.glob('*.ipynb'):
    result = subprocess.run(['jupytext', '--to', 'py', str(nb)], capture_output=True, text=True)
    print(f'{"✓" if result.returncode == 0 else "✗"} {nb.name}')

# %% [markdown] id="kN7nPAEN0nyQ"
# ## Git commit

# %% id="bgHuOEu5vt74"
msg = input('Commit message: ')
# !git config --global user.email "joseph.tricarico@delaware.gov"
# !git config --global user.name "Joseph Tricarico"
# !git -C {PROJ} pull origin main
# !git -C {PROJ} add *.py *.yaml *.toml .gitignore
# !git -C {PROJ} commit -m "{msg}"
# !git -C {PROJ} push origin main

# %% id="x7_IHIhkhTnc"
# !git -C {PROJ} fetch
# !git -C {PROJ} pull
