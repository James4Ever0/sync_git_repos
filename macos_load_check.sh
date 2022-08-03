# before that make necessary directories? builtin with double_sync_macos?
cd /Volumes/CaseSensitive/pyjom

tmux kill-session -t double_sync_Volumes_CaseSensitive_pyjom

# python3 /Users/jamesbrown/Desktop/works/sync_git_repos/double_sync_macos.py # change test.
python3 /Users/jamesbrown/Desktop/works/sync_git_repos/create_lock_macos.py # change test.

tmuxp load /Users/jamesbrown/Desktop/works/sync_git_repos/double_sync_macos.yml

# python3 /root/Desktop/works/sync_git_repos/sync_logic.py --init git@github.com:James4Ever0/pyjom.git