#!/usr/bin/env python
#
# Updates the given HMM model file based on an strace output file.
#

import argparse
import json
import re

# This regex captures the name of the syscall as well as the first string
# argument.
# TODO: capture additional arguments as necessary.
# old SYSCALL_REGEX = '^\w*\s*(\w*)\((?:(".*?"))?.*'
SYSCALL_REGEX = '^\w+\([^,]+[,\)]'

# Indicates that strace's output has changed to a fork created by the program.
FORK_DELIMETER = "+++ exited with"

def main(args):
    model = readModel(args.output)
    
    calls = []
    # TODO: consider n-sequences of system calls when defining our model in
    # order to give context to each syscall (i.e., we may want to provide
    # distinction in our model between an "mmap" followed by an "open" or a
    # "munmap" followed by an "open").
    for line in args.strace:
        
        call = re.findall(SYSCALL_REGEX, line)
        if call and not FORK_DELIMETER in call:
            # We only capture the name of the syscall and the first string
            # argument. Example call: open /tmp/foo
            #calls.append(call[0][0] \
            #    + ((" " + call[0][1][1:-1]) if call[0][1] else ""))
            calls.append(call)
        
    # TODO: at this point, calls contains a list of all the valid system calls
    # with their respective first arguments.
    print calls
    # Split up the array of calls into (syscall, arg) tuples (the first space)

    # Update our model at each syscall based on the argument, if there is one

def readModel(output):
    contents = output.read()
    if not contents:
        contents = "{}"
    return json.loads(contents)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Updates the given HMM model file based on an strace output file.")
    parser.add_argument('strace', type=argparse.FileType('r'),\
        help="strace output file")
    parser.add_argument('output', type=argparse.FileType('rw'),\
        help="HMM output file")
    main(parser.parse_args())
    

