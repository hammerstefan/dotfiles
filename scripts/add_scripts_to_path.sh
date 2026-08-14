#!/bin/bash
script_dir="$HOME/scripts"
source $script_dir/functions
if ! echo "$PATH" | grep "$script_dir"
then
    export PATH="$script_dir:$PATH"
fi
