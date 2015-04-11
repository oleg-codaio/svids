#!/bin/bash
#
# Explores all valid paths through the executable and creates an HMM that can be
# used for intrusion detection.
#
# Authors: sakharov.t@husky.neu.edu (Timothy Sakharov)
#          vaskevich.o@husky.neu.edu (Oleg Vaskevich)
#

UPDATE_MODEL="$(dirname $(realpath $0))/update_model.py"

set -e

if [[ $# -ne 2 || ! -f $1 ]]; then
    echo "usage: trainer.sh <SVIDS file> <HMM model output file>"
    exit 1
fi

file="$1"
file_dir="$(dirname $(realpath "$file"))"
output="$2"
touch "$output"
output_dir="$(dirname $(realpath "$output"))"
strace_tmp="$output_dir/strace.tmp"

# Delete any existing HMM output file and replace it with a blank one.
rm -f "$output"
touch "$output"

# Parse the SVIDS file.
lineno=0
while read line; do
    # The first line must always be "SVIDS".
    if [ $lineno -eq 0 ]; then
        if [ $line != "SVIDS" ]; then
            echo "Invalid SVIDS file"
            exit 1
        fi

    # The second line contains the name of the executable in the same
    # directory.
    elif [ $lineno -eq 1 ]; then
         program="$line"

    # The remaining lines contain the arguments with which we want to invoke
    # update_model.py.
    else
        strace -o "$strace_tmp" "$file_dir/$program" > /dev/null 2>&1
        $UPDATE_MODEL "$strace_tmp" "$output_dir/$output"
        rm "$strace_tmp"
    fi
    lineno=$[$lineno + 1]
done < "$file"

