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

# %% colab={"base_uri": "https://localhost:8080/"} executionInfo={"elapsed": 1540, "status": "ok", "timestamp": 1772562944112, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}, "user_tz": 300} id="4Mna7DKmvSgF" outputId="9eab1d62-3854-4f51-e9fc-0b6599f7e4ad"
import os, subprocess, sys
from pathlib import Path
from google.colab import drive, userdata

drive.mount('/content/drive')
PROJ = Path('/content/drive/MyDrive/doverde')
SRC_PATH = str(PROJ / 'doverde')
sys.path.append(SRC_PATH)

REPO = 'joetric/doverde'
#TODO: move these settings to config; not everyone may use Colab
GITHUB_TOKEN = userdata.get('GITHUB_TOKEN')
GH_EMAIL = userdata.get('GH_EMAIL')
GH_FULL_NAME = userdata.get('GH_FULL_NAME')

# %cd {PROJ}

# %% executionInfo={"elapsed": 13, "status": "ok", "timestamp": 1772562944130, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}, "user_tz": 300} id="noACbGrpv5XK"
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
# ## Convert Jupyter notebooks to .py; compile TODOs

# %% colab={"base_uri": "https://localhost:8080/"} executionInfo={"elapsed": 11435, "status": "ok", "timestamp": 1772562955557, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}, "user_tz": 300} id="f9QtbH1Ru16o" outputId="22166ea9-ec3a-46ed-edbd-065330f342a1"
nb_dir = PROJ / 'doverde'
for nb in nb_dir.glob('*.ipynb'):
    result = subprocess.run(['jupytext', '--to', 'py', str(nb)], capture_output=True, text=True)
    print(f'{"✓" if result.returncode == 0 else "✗"} {nb.name}')

#TODO: write some header for the TODO.md
# !grep -r "#TODO" --include='*.py' . > TODO.md

# %% [markdown] id="kN7nPAEN0nyQ"
# ## Git commit

# %% colab={"base_uri": "https://localhost:8080/"} executionInfo={"elapsed": 471, "status": "ok", "timestamp": 1772563089845, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}, "user_tz": 300} id="gkSjkskybFVE" outputId="cb2cfa7d-0521-4d03-c50a-2839d0a4c92f"
print("--- PRE-COMMIT STATUS ---")
# !git status

# %% colab={"base_uri": "https://localhost:8080/"} executionInfo={"elapsed": 10843, "status": "ok", "timestamp": 1772563079990, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}, "user_tz": 300} id="bgHuOEu5vt74" outputId="76494dcc-3fd3-44d1-fe80-3e1b2e6801ab"
# !git config --global user.email "{GH_EMAIL}"
# !git config --global user.name "{GH_FULL_NAME}"
# !git pull origin main
# !git add *.py *.yaml *.toml *.md .gitignore # *.csv
# !git status

msg = input('Commit message: ')
# !git commit -m "{msg}"
# !git push origin main

# %% executionInfo={"elapsed": 19, "status": "ok", "timestamp": 1772562987933, "user": {"displayName": "Joseph Tricarico", "userId": "06693078329233897993"}, "user_tz": 300} id="6_o8yoar5XRm"
# # !git pull --rebase origin main
