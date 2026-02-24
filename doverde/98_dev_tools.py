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

# %% id="4Mna7DKmvSgF" colab={"base_uri": "https://localhost:8080/"} executionInfo={"status": "ok", "timestamp": 1771906050061, "user_tz": 300, "elapsed": 1263, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="fdfbfc02-d631-4bcc-dd84-7d8a2c1ce7b0"
import os, subprocess, sys
from pathlib import Path
from google.colab import drive, userdata

drive.mount('/content/drive')
PROJ = Path('/content/drive/MyDrive/doverde')
SRC_PATH = str(PROJ / 'doverde')
sys.path.append(SRC_PATH)

REPO = 'joetric/doverde'
GITHUB_TOKEN = userdata.get('GITHUB_TOKEN')


# %% id="noACbGrpv5XK" executionInfo={"status": "ok", "timestamp": 1771906050183, "user_tz": 300, "elapsed": 89, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}}
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

# %% id="f9QtbH1Ru16o" executionInfo={"status": "ok", "timestamp": 1771906074916, "user_tz": 300, "elapsed": 9500, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/"} outputId="23675ecb-e1a0-41a5-b1c2-52400abac071"
import subprocess

nb_dir = PROJ / 'doverde'
for nb in nb_dir.glob('*.ipynb'):
    result = subprocess.run(['jupytext', '--to', 'py', str(nb)], capture_output=True, text=True)
    print(f'{"✓" if result.returncode == 0 else "✗"} {nb.name}')

# %% [markdown] id="kN7nPAEN0nyQ"
# ## Git commit

# %% id="gkSjkskybFVE" executionInfo={"status": "ok", "timestamp": 1771906079662, "user_tz": 300, "elapsed": 27, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/"} outputId="eb17f709-8d2b-4923-e334-3b829c2200ca"
print("--- PRE-COMMIT STATUS ---")
# !git -C {PROJ} status

# %% id="bgHuOEu5vt74" executionInfo={"status": "ok", "timestamp": 1771906102730, "user_tz": 300, "elapsed": 7844, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} colab={"base_uri": "https://localhost:8080/"} outputId="715d63e5-ec64-48be-fb76-f1f6f454d58f"
# !git config --global user.email "joseph.tricarico@delaware.gov"
# !git config --global user.name "Joseph Tricarico"
# !git -C {PROJ} pull origin main
# !git -C {PROJ} add *.py *.yaml *.toml *.csv .gitignore
# !git -C {PROJ} status

msg = input('Commit message: ')
# !git -C {PROJ} commit -m "{msg}"
# !git -C {PROJ} push origin main
