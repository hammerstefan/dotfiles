import os
import sys

import click
import git
from git import GitCommandError
from launchpadlib.launchpad import Launchpad

launchpad = Launchpad.login_with('get_mp', 'production', version='devel')

def do_setup(url):
    mp_api_url = url.replace('code.launchpad.net', 'api.launchpad.net/devel')
    mp_id = url.split('/')[-1]
    mp = launchpad.load(mp_api_url)
    repo = git.Repo(os.getcwd(), search_parent_directories=True)
    source_branch: str = mp.source_git_path.removeprefix('refs/heads/')
    try:
        git_remote = repo.create_remote(f'mp-{mp_id}', mp.source_git_repository.git_ssh_url)
        git_remote.fetch(refspec=source_branch)
    except GitCommandError as e:
        if 'already exists' in e.stderr:
            pass
        else:
            raise e

    try:
        repo.git.worktree('remove', f'mp-{mp_id}')
    except GitCommandError as e:
        if 'is not a working tree' in e.stderr:
            pass
        else:
            raise e
    try:
        repo.git.worktree('add', f'mp-{mp_id}', f'mp-{mp_id}/{source_branch}')
    except GitCommandError as e:
        if 'already exists' in e.stderr:
            pass
        else:
            raise e
    worktree_dir = os.path.join(repo.working_dir, f'mp-{mp_id}')
    repo = git.Repo(worktree_dir)
    print(worktree_dir)
    print(f'Checkout {source_branch} to worktree {worktree_dir}\nExit subshell with "exit" when done.', file=sys.stderr)


def do_cleanup(url):
    mp_id = url.split('/')[-1]
    repo = git.Repo(os.getcwd(), search_parent_directories=True)
    repo.git.worktree('remove', f'mp-{mp_id}')
    repo.delete_remote(repo.remote(f'mp-{mp_id}'))





@click.command()
@click.option('--cleanup', is_flag=True)
@click.argument('url')
def main(cleanup: bool, url: str):
    if cleanup:
        do_cleanup(url)
    else:
        do_setup(url)


main()
