#!/bin/bash
script_dir=/home/shammer/scripts
if ! echo "$PATH" | grep "$script_dir"
then
    export PATH="$script_dir:$PATH"
fi
