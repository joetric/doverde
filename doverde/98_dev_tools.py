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

# %% id="4Mna7DKmvSgF" colab={"base_uri": "https://localhost:8080/"} executionInfo={"status": "ok", "timestamp": 1771906712208, "user_tz": 300, "elapsed": 950, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="4fed1478-9e55-493f-b051-f63b732c8b99"
import os, subprocess, sys
from pathlib import Path
from google.colab import drive, userdata

drive.mount('/content/drive')
PROJ = Path('/content/drive/MyDrive/doverde')
SRC_PATH = str(PROJ / 'doverde')
sys.path.append(SRC_PATH)

REPO = 'joetric/doverde'
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

# %% id="f9QtbH1Ru16o" executionInfo={"status": "ok", "timestamp": 1771906721719, "user_tz": 300, "elapsed": 9517, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="78cec1ae-68f7-4d8e-db44-f95b564f995a" colab={"base_uri": "https://localhost:8080/"}
import subprocess

nb_dir = PROJ / 'doverde'
for nb in nb_dir.glob('*.ipynb'):
    result = subprocess.run(['jupytext', '--to', 'py', str(nb)], capture_output=True, text=True)
    print(f'{"✓" if result.returncode == 0 else "✗"} {nb.name}')

# %% [markdown] id="kN7nPAEN0nyQ"
# ## Git commit

# %% id="gkSjkskybFVE" executionInfo={"status": "ok", "timestamp": 1771906721942, "user_tz": 300, "elapsed": 221, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="22533ea0-2448-44ac-d7e1-1682881ed6c7" colab={"base_uri": "https://localhost:8080/"}
print("--- PRE-COMMIT STATUS ---")
# !git -C {PROJ} status

# %% id="bgHuOEu5vt74" outputId="335a14d5-c28a-4976-e65f-28d0a22bfe99" colab={"base_uri": "https://localhost:8080/"} executionInfo={"status": "ok", "timestamp": 1771906931749, "user_tz": 300, "elapsed": 16399, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
# !git config --global user.email "joseph.tricarico@delaware.gov"
# !git config --global user.name "Joseph Tricarico"
# !git -C {PROJ} pull origin main
# !git -C {PROJ} add *.py *.yaml *.toml *.csv .gitignore
# !git -C {PROJ} status

msg = input('Commit message: ')
# !git -C {PROJ} commit -m "{msg}"
# !git -C {PROJ} push origin main
