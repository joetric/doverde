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

# %% id="4Mna7DKmvSgF" colab={"base_uri": "https://localhost:8080/"} executionInfo={"status": "ok", "timestamp": 1771879408155, "user_tz": 300, "elapsed": 30307, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="b7bb1c41-9df8-4027-dc26-14e72370ad97"
import os, subprocess, sys
from pathlib import Path
from google.colab import drive, userdata

drive.mount('/content/drive')
PROJ = Path('/content/drive/MyDrive/dnrec_dpr_revex_engine')
sys.path.append(str(PROJ / 'dpr_revex'))

REPO = 'joetric/dnrec-dpr-revex-engine'
GITHUB_TOKEN = userdata.get('GITHUB_TOKEN')


# %% id="noACbGrpv5XK"
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

# %% colab={"base_uri": "https://localhost:8080/"} id="f9QtbH1Ru16o" executionInfo={"status": "ok", "timestamp": 1771879442768, "user_tz": 300, "elapsed": 11059, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="5fb57adb-7884-4dc9-b332-e48ecf7823ed"
import subprocess

nb_dir = PROJ / 'dpr_revex'
for nb in nb_dir.glob('*.ipynb'):
    result = subprocess.run(['jupytext', '--to', 'py', str(nb)], capture_output=True, text=True)
    print(f'{"✓" if result.returncode == 0 else "✗"} {nb.name}')

# %% [markdown] id="kN7nPAEN0nyQ"
# ## Git commit

# %% colab={"base_uri": "https://localhost:8080/"} id="bgHuOEu5vt74" executionInfo={"status": "ok", "timestamp": 1771632985927, "user_tz": 300, "elapsed": 6081, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="98c378a1-aaa7-4686-8172-d26434bb5e1e"
msg = input('Commit message: ')
# !git config --global user.email "joseph.tricarico@delaware.gov"
# !git config --global user.name "Joseph Tricarico"
# !git -C {PROJ} pull origin main
# !git -C {PROJ} add *.py *.yaml *.toml .gitignore
# !git -C {PROJ} commit -m "{msg}"
# !git -C {PROJ} push origin main
