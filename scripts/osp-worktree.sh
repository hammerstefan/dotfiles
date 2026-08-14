CHANGE="${1:-$(openspec list --changes --json | jq -r '.changes[].name' | fzf)}"
git worktree add "../$CHANGE"
cp opencode.json "../$CHANGE" || true
cp -r .opencode "../$CHANGE" || true
cp .test-env  "../$CHANGE" || true
cd "../$CHANGE"
if [ -f "pyproject.toml" ]; then
    uv venv
    uv sync --all-extras --prerelease=allow
fi
tmux new-window -c "../$CHANGE" "uv run opencode"

