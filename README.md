# sync all your code automatically, with filters of huge files.

filters may not work. since some file may grow large before we get it.

first delete the cached file only from index(`git rm -r --cached [file]`), then just add it to `.gitignore`(https://www.atlassian.com/git/tutorials/saving-changes/gitignore)

usage for vscode:

```bash
#!/bin/sh

set -e

# printf '┏━(\033[1;31mMessage from Kali developers\033[00m)\n'
# printf '┃ vscode is not the binary you may be expecting.\n'
# printf '┃ You are looking for \"code-oss\"\n'
# printf '┃ Starting code-oss for you...\n'
# printf '┗━\n'

sync_git_repos_basepath=/root/Desktop/works/sync_git_repos

# remember to config ssh keypath in sync_logic.py!

# python3 $sync_git_repos_basepath/create_lock.py

# python3 $sync_git_repos_basepath/main.py &
# gnome-terminal tmuxp $sync_git_repos_basepath/double_sync.yml
# python3 $sync_git_repos_basepath/main_nongit_sync.py &
python3 $sync_git_repos_basepath/double_sync.py

/usr/lib/code-oss/code-oss --no-sandbox --unity-launch $@


python3 $sync_git_repos_basepath/check_attached.py

echo "________________VSCODE LAUNCHED________________"

# python3 $sync_git_repos_basepath/delete_lock.py

```
