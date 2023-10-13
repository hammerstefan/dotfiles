#! /bin/bash
PYTHON=/home/shammer/.pyenv/versions/3.11.0/envs/get_mp/bin/python
dir="$($PYTHON ~/scripts/get_mp $1)"
bash --init-file <(echo ". \"$HOME/.bashrc\"; cd $dir")
$PYTHON ~/scripts/get_mp --cleanup $1
