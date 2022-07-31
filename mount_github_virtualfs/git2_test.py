import pygit2

repoPath = "/root/Desktop/works/sync_git_repos/mount_github_virtualfs/toyProject"

repo = pygit2.init_repository(repoPath, False) # do not create bare repository.

index = repo.index
index.add(".")
index.write()