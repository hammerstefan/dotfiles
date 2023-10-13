source ~/Canonical/git/build_publish_test/cpc_build_tools/human_scripts/bakeportato.sh
myportato() {
    target_branches=$@
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    find_branch_point() {
        echo $(diff -u <(git rev-list --first-parent HEAD) \
                    <(git rev-list --first-parent origin/devel) | \
                    sed -ne 's/^ //p' | head -1)
    }

    echo "Backporting from $current_branch to $target_branch"
    branch_point=$(find_branch_point)
    commits_to_backport=$(git rev-list --reverse ${branch_point}..HEAD | tr "\r\n" " ")

    echo "Commits needing backporting"
    echo $commits_to_backport

    echo "bakeportato -u origin -f hammerstefan -b ${current_branch/#devel-/} $target_branches -- $commits_to_backport"
    bakeportato -u origin -f hammerstefan -b ${current_branch/#devel-/} $target_branches -- "$commits_to_backport"
}
