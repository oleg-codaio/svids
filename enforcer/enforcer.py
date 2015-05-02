#!/usr/bin/env python
#
# Monitors all invocations of a given program and verifies that they run within
# the expectations of our model.

# Some pseudocode follows.

# Forever:
#     Construct an n-gram of the most recent syscalls;
#     Define a as a suspicion metric, and k as a suspicion threshold;
#     For each syscall:
#         Check if it's an open;
#         If it is:
#             Extract the path argument to variable P;
#             Use a modified Viterbi algorithm to determine the probability p of
#               the the path being handled by the model as well as the most
#               likely path q;
#             Merge p into a;
#     If p > k:
#         Interdict the program;

raise NotImplementedError

