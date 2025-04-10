#!/usr/bin/env python

import sys

commit_msg_filepath = sys.argv[1]

with open(commit_msg_filepath, "w", newline="\n") as handle:
    handle.write("commit message")
