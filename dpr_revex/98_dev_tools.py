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

# %% colab={"base_uri": "https://localhost:8080/"} id="4Mna7DKmvSgF" executionInfo={"status": "ok", "timestamp": 1771620060407, "user_tz": 300, "elapsed": 1631, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="0dd873f3-19c0-46fc-ec9a-12e92118e772"
import os, subprocess, sys
from pathlib import Path
from google.colab import drive, userdata

drive.mount('/content/drive')
PROJ = Path('/content/drive/MyDrive/dnrec_dpr_revex_engine')
sys.path.append(str(PROJ / 'dpr_revex'))

REPO = 'joetric/dnrec-dpr-revex-engine'
GITHUB_TOKEN = userdata.get('GITHUB_TOKEN')


# %% colab={"base_uri": "https://localhost:8080/"} id="noACbGrpv5XK" executionInfo={"status": "ok", "timestamp": 1771620157452, "user_tz": 300, "elapsed": 821, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="b2096747-9073-4ee8-a477-6b582331702e"
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

# %% colab={"base_uri": "https://localhost:8080/"} id="f9QtbH1Ru16o" executionInfo={"status": "ok", "timestamp": 1771620758680, "user_tz": 300, "elapsed": 9327, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="98b3fe27-ac35-4fb2-b710-596ff8652055"
import subprocess

nb_dir = PROJ / 'dpr_revex'
for nb in nb_dir.glob('*.ipynb'):
    result = subprocess.run(['jupytext', '--to', 'py', str(nb)], capture_output=True, text=True)
    print(f'{"✓" if result.returncode == 0 else "✗"} {nb.name}')

# %% [markdown] id="kN7nPAEN0nyQ"
# ## Git commit

# %% colab={"base_uri": "https://localhost:8080/"} id="bgHuOEu5vt74" executionInfo={"status": "ok", "timestamp": 1771621286120, "user_tz": 300, "elapsed": 5091, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="069dc6c3-ff3b-41cc-b3ac-5940161b95c7"
msg = input('Commit message: ')
# # !git config --global user.email "your.name@delaware.gov"
# # !git config --global user.name "Firstname Lastname"
# !git -C {PROJ} add *.py *.yaml *.toml .gitignore
# !git -C {PROJ} commit -m "{msg}"
# !git -C {PROJ} push origin main
