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

# %% colab={"base_uri": "https://localhost:8080/"} executionInfo={"elapsed": 5563, "status": "ok", "timestamp": 1772564837628, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}, "user_tz": 300} id="4Mna7DKmvSgF" outputId="7ab66d0c-2426-4479-da2b-d25e9114a26b"
# !pip -q install pipreqs

import os, subprocess, sys
from pathlib import Path
from google.colab import drive, userdata

drive.mount('/content/drive')
PROJ = Path('/content/drive/MyDrive/doverde')
SRC_PATH = str(PROJ / 'doverde')
sys.path.append(SRC_PATH)

# --- SETTINGS FOR THIS MODULE ---
REPO = 'joetric/doverde'
#TODO: move these settings to config.yaml; not everyone may use Colab
GITHUB_TOKEN = userdata.get('GITHUB_TOKEN')
GH_EMAIL = userdata.get('GH_EMAIL')
GH_FULL_NAME = userdata.get('GH_FULL_NAME')
# path to notebooks to convert
#TODO: use list instead of single dir, or allow for recursive dir notebook search
NB_DIR = PROJ / 'doverde'
# NB_DIR = PROJ / 'studies/dnrec_dpr'

# %cd {PROJ}

# %% executionInfo={"elapsed": 6, "status": "ok", "timestamp": 1772564840299, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}, "user_tz": 300} id="noACbGrpv5XK"
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
# ## Convert Jupyter notebooks to .py; compile TODOs; update requirements

# %% colab={"base_uri": "https://localhost:8080/"} executionInfo={"elapsed": 12475, "status": "ok", "timestamp": 1772564854153, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}, "user_tz": 300} id="f9QtbH1Ru16o" outputId="d37fe7b0-2501-4565-bae8-23f1ec667be5"
for nb in NB_DIR.glob('*.ipynb'):
    result = subprocess.run(['jupytext', '--to', 'py', str(nb)], capture_output=True, text=True)
    print(f'{"✓" if result.returncode == 0 else "✗"} {nb.name}')

#TODO: write some header for the TODO.md
# !grep -r "#TODO" --include='*.py' . > TODO.txt

# make/update requirements.txt
# !pipreqs {PROJ} --force

# %% [markdown] id="kN7nPAEN0nyQ"
# ## Git commit

# %% colab={"base_uri": "https://localhost:8080/"} executionInfo={"elapsed": 323, "status": "ok", "timestamp": 1772564854489, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}, "user_tz": 300} id="gkSjkskybFVE" outputId="fa4f8700-5d10-4a21-f226-a9530ede6b24"
print("--- PRE-COMMIT STATUS ---")
# !git status

# %% colab={"base_uri": "https://localhost:8080/"} executionInfo={"elapsed": 20050, "status": "ok", "timestamp": 1772564874541, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}, "user_tz": 300} id="bgHuOEu5vt74" outputId="ecf59fd2-ecb8-4e38-846a-dbebf55cac1c"
# !git config --global user.email "{GH_EMAIL}"
# !git config --global user.name "{GH_FULL_NAME}"
# !git pull origin main
# !git add *.py *.yaml *.toml *.md .gitignore requirements.txt # *.csv
# !git status

msg = input('Commit message: ')
# !git commit -m "{msg}"
# !git push https://{GITHUB_TOKEN}@github.com/{REPO}.git main

# %% executionInfo={"elapsed": 1, "status": "aborted", "timestamp": 1772564806597, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}, "user_tz": 300} id="6_o8yoar5XRm"
# # !git pull --rebase origin main

# %% [markdown] id="V-my0n5HFyam"
# ## Show current requirements.txt

# %% colab={"base_uri": "https://localhost:8080/"} id="BBekoq7FF1CW" executionInfo={"status": "ok", "timestamp": 1772564878314, "user_tz": 300, "elapsed": 15, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}} outputId="ad1bdd31-a00a-4c7b-c064-5a37b1e0f108"
with open(f'{PROJ}/requirements.txt', 'r') as f:
    print(f.read())
