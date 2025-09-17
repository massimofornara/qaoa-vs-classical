# quantum-finance-api-auth
QAOA vs Classical  Comparison between Quantum Approximate Optimization Algorithm (QAOA) and classical algorithms for optimization problems.   This repository contains Python notebooks and scripts to test and benchmark performance.  Requirements  - Git ≥ 2.30   - Python ≥ 3.10 (recommended: 3.11)   - pip and venv  - (Optional) Jupyter Notebook Quick Installation  Ubuntu/Debian ```bash sudo apt update sudo apt install -y git python3 python3-venv python3-pip ` 
macOS
 `brew install git python ` 
Windows
 
 
- Install [Git for Windows](https://git-scm.com/download/win)
 
- Install [Python 3.11](https://www.python.org/downloads/)
 
- Or use WSL (Ubuntu) and follow the Linux commands.
 

 
Android (Termux)
 `pkg update pkg install -y git python `  
 Clone the repository
 `git clone https://github.com/massimofornara/qaoa-vs-classical.git cd qaoa-vs-classical ` 
Check the remote:
 `git remote -v ` 
If incorrect:
 `git remote set-url origin https://github.com/massimofornara/qaoa-vs-classical.git ` 
Note for Android (Termux) If you see a `safe.directory` warning, use the absolute path:
 `git config --global --add safe.directory /storage/emulated/0/Documents/qaoa-vs-classical `  
 Python Environment Setup
 
From the project root:
 `python3 -m venv .venv  Linux/macOS/WSL/Termux source .venv/bin/activate  Windows CMD .venv\Scripts\activate ` 
Upgrade `pip`:
 `python -m pip install --upgrade pip ` 
Install dependencies:
 `pip install -r requirements.txt ` 
If no `requirements.txt` is present, install the main packages:
 `pip install jupyter numpy scipy matplotlib networkx qiskit `  
 Run
 
Jupyter Notebook
 `jupyter notebook ` 
Then open the `.ipynb` files.
 
 Python Script
 
Example:
 `python main.py `  
 Git Workflow
 
Check repo status:
 `git status ` 
Update from remote:
 `git pull origin main --rebase ` 
Stage and commit:
 `git add . git commit -m "Project updates" ` 
First push:
 `git push -u origin main ` 
Subsequent pushes:
 `git push `  
Troubleshooting
 
1. `error: cannot pull with rebase: You have unstaged changes`
 
You have local uncommitted changes.
 
 
- Keep changes
 

 `git add . git commit -m "save local changes" git pull origin main --rebase ` 
 
- Discard changes
 

 `git reset --hard git pull origin main --rebase ` 
 
- Stash temporarily
 

 `git stash git pull origin main --rebase git stash pop `  
2. `rejected: fetch first` / “Updates were rejected…”
 
Remote has commits you don’t have locally:
 `git pull origin main --rebase git push ` 
If you want to completely overwrite the remote:
 `git push origin main --force `  
3. `remote: Repository not found`
 
Make sure the URL is correct:
 `git remote set-url origin https://github.com/massimofornara/qaoa-vs-classical.git git fetch origin `  
 4. `safe.directory not absolute`
 
On Termux/Android use:
 `git config --global --add safe.directory /storage/emulated/0/Documents/qaoa-vs-classical `  
📌 Notes
 
 
- Prefer `git pull --rebase` instead of `git pull` to keep history cleaner.
 
- If using GitHub over HTTPS, you must use your username and a Personal Access Token (PAT) instead of a password. Create a token at [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens).
 

  
Author: Massimo Fornara
