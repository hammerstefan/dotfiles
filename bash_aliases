# GIT
alias gs="git status"
alias ga="git add"
alias gc="git commit"


alias codei="code-insiders"
alias dc="docker-compose"
alias fixssh='eval $(tmux showenv -s SSH_AUTH_SOCK)'
alias tmux="tmux -2"
#alias pycharm="/home/shammer/pycharm-2022.2.4/bin/pycharm.sh"
alias fzfp="fzf --preview 'bat --color=always --style=numbers --line-range=:500 {}'"
# persistent history check
alias phgrep='cat ~/.persistent_history|grep --color'
gvimd() {
    curdir=${PWD##*/}
    gvim -c "Ctitle ${curdir}"
}
alias mkcd='_mkcd(){ mkdir -p "$1"; cd "$1"; }; _mkcd'
alias mkcdtoday='_mkcdd(){ d="$(date +%Y%m%d)"; mkcd "$d"; }; _mkcdd'
alias fzfy="fzf --tac --print0 --bind 'enter:become(echo {} | wl-copy)'"
alias oc="uv run opencode"
alias bfs="butterfish shell"
