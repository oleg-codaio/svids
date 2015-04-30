#!/usr/bin/env python
#
# Updates the given HMM model file based on an strace output file.
# TODO: Handle prob > 1 and prob < 0
#

import argparse
import json
import re

# This regex captures the name of the syscall as well as the first string
# argument.
# TODO: capture additional arguments as necessary.
# old SYSCALL_REGEX = '^\w*\s*(\w*)\((?:(".*?"))?.*'
SYSCALL_REGEX = '^\w+\([^,]+[,\)]'

# Smoothing constants to ensure nonzero probabilities
# ADD_SMOOTH is used when raising a probability,
# SUB_SMOOTH is used when lowering one
ADD_SMOOTH = .005
SUB_SMOOTH = .01

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
        
    # At this point, calls contains a list of all the valid system calls
    # with their respective first arguments.

    # Split up the array of calls into (syscall, arg) tuples (the first space)
    syscalls = []
    for i in calls:
        splitstring = re.split('[\(,]',i[0])
        syscalls.append((splitstring[0],splitstring[1],))
    print syscalls
    # Update our model at each syscall based on the argument, if there is one
    for s in syscalls:
        callname = s[0]
        callarg = s[1]
        # Currently, the implementation is limited to 'open' system calls,
        # although this could easily be expanded by wrapping the
        # transitionmatrix, emissions, and initprob of each syscall in a JSON object
        if (callname == 'open'):
            # Initialize an nxn matrix  TODO: Clean up n's?
            n = len(emissionstates)
            emptymatrix = [[0]*n]*n
            emissionstates = re.split('/',callarg[1:])
            # If our given HMM is empty, we need to initialize and populate it
            if (model == {}):
                model = {'transitionmatrix':emptymatrix, 'emissions':dict(), 'initprob':dict()}
                # Loop through the observed emissions
                initsmooth = (ADD_SMOOTH / (len(emissionstates)-1))
                for i in range(len(emissionstates)):
                    # set initial probabilities
                    if (i == 0):
                        model['initprob'][str(i)] = (1 - ADD_SMOOTH)
                    else:
                        model['initprob'][str(i)] = (initsmooth)
                    # set emissions
                    model['emissions'][str(i)] = emissionstates[i]
                    # set transition matrix
                    for j in range(len(emissionstates)):
                        # Observed probability = 1, smoothed down
                        if ((j - i) == 1):
                            model['transitionmatrix'][i][j] = (1 - ADD_SMOOTH)
                        else:
                            # Matrix is nxn, so initsmooth can still be used
                            model['transitionmatrix'][i][j] = initsmooth
            else: # our HMM is not empty
                initsmooth = (SUB_SMOOTH / (len(model['emissions'])-1))
                initsmooth2 = (ADD_SMOOTH / (len(model['emissions'])-1))
                # Loop through our observed emissions
                for i in range(len(emissionstates)):
                    seenemission = False
                    keylist = []
                    # Has an emission been seen by the model before?
                    for k in model['emissions'].keys():
                        # Keep track of the numerical key values we've seen
                        keylist.append(int(k))
                        # Yes, it has been seen before
                        if (emissionstates[i] == model['emissions'][k]):
                            seenemission = True
                            statenum = k
                    keylist.sort()
                    # If we have not yet seen this emission
                    if (not seenemission):
                        # Add it to the emissions list
                        newstate = str(len(keylist))
                        model['emissions'][newstate] = emissionstates[i]
                        oldrows = len(model['transitionmatrix'])
                        oldcols = len(model['transitionmatrix'][0])
                        # Set its initial probability and update the transition matrix
                        if (i == 0):
                            # If it's the initial observed emission, increase
                            # its initial probability
                            model['initprob'][newstate] = SUB_SMOOTH
                            for x in model['initprob'].keys():
                                # and lower all others
                                if (x != newstate):
                                    model['initprob'][x] -= initsmooth
                            
                        else: # if it's not the initial observed emission
                            # set its initial probability to a smoothed-up 0
                            model['initprob'][newstate] = ADD_SMOOTH
                            for x in model['initprob'].keys():
                                # and slightly lower all others
                                if (x != newstate):
                                    model['initprob'][x] -= initsmooth2
                        # Update the transition matrix
                        # TODO: Consider adding look-ahead step to preemptively set the transition
                        # probability to emission[i+1] (especially if it has already been encountered
                        # by the model), rather than simply initializing a naive, uniform row
                        
                        # Add new row
                        newrow = [0]*len(model['transitionmatrix'][0])
                        model['transitionmatrix'].append(newrow)
                        uniformprob = (ADD_SMOOTH / (len(model['transitionmatrix'][0])))
                        # Add new column
                        for r in range(len(model['transitionmatrix'])):
                            model['transitionmatrix'][r].append(ADD_SMOOTH)
                            # If this is the new column, set uniformly distributed probabilities
                            if ((r+1) == len(model['transitionmatrix'])):
                                for s in range(len(model['transitionmatrix'][0]) - 1):
                                    model['transitionmatrix'][r][s] += uniformprob
                            else:
                                for c in range(len(model['transitionmatrix'][0]) - 1):
                                    model['transitionmatrix'][r][c] -= uniformprob
                    else: # If we have seen the emission before
                        # statenum is the (most probable) state associated with this emission.
                        # No need to change model['emissions']
                        
                        # If it was just observed as a starting emission,
                        # raise its initprob value
                        if (i == 0):
                            model['initprob'][statenum] += SUB_SMOOTH
                            # and lower all others
                            for (n in keylist):
                                if (n != statenum):
                                    model['initprob'][k] -= initsmooth
                        else:
                            # current emission (i) is not the first observed (i is nonzero)
                            
                            # Update the transition matrix using a forward-backward procedure
                            # Invariant: emission i-1 has already been seen
                            # (this is enforcfed in the if (not seenemission) clause)
                            
                            # Search for the previous emission in our model
                            for z in model['emissions'].keys():
                                if (emissionstates[i-1] == model['emissions'][z]):
                                    fromstate = z
                            model['transitionmatrix'][int(fromstate)][int(statenum)] += ADD_SMOOTH
                            for y in range(len(model['transitionmatrix'][int(fromstate)]])):
                                if (y != int(statenum)):
                                    model['transitionmatrix'][int(fromstate)][y] -= initsmooth2
    json.dumps(model)
                        
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
    

