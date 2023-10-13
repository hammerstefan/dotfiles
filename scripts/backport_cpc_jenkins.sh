set -x
target_branch=$1
current_branch=$(git rev-parse --abbrev-ref HEAD)
find_branch_point() {
    echo $(diff -u <(git rev-list --first-parent HEAD) \
                <(git rev-list --first-parent origin/devel) | \
                sed -ne 's/^ //p' | head -1)
}

echo "Backporting from $current_branch to $target_branch"
branch_point=$(find_branch_point)
commits_to_backport=$(git rev-list ${branch_point}..HEAD)

echo "Commits needing backporting"
echo $commits_to_backport

git fetch origin
git checkout -b backport-${current_branch/#devel-/}-${target_branch} origin/${target_branch} --no-track
if [[ $? != 0 ]]; then
    echo "Failed to check out branch. Please correct"
    exit 1
fi
git cherry-pick -x $commits_to_backport
if [[ $? != 0 ]]; then
    echo "Conflict detected. Please merge and and run 'git cherry-pick -x --continue'"
    exit 1
    #git mergetool
    #git commit -v
fi
git push-me --no-verify
git lp-propose origin/${target_branch}
git checkout -
