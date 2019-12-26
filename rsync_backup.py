#!/usr/bin/env python3
#
# Backup selected files/folders using rsync
# Philip Darke (December 2019)
# philipdarke.com
#
# MIT License
#
# Copyright (c) 2019 Philip Darke (philipdarke.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import rsync_rules
import os
import argparse
import subprocess
from datetime import datetime

# Date/time format for backup location
FORMAT = '%Y.%m.%d-%H.%M.%S'

if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(prog='rsync-backup',
                                     description='Backup selected files/folders using rsync.')
    parser.add_argument("path",
                        help="path for backup")
    parser.add_argument('-v', '--verbose',
                        help='print pattern rules to console',
                        action='store_true',
                        dest='VERBOSE')
    parser.add_argument('-i', '--input',
                        help='path to rules file (default "./rules.rsync")',
                        type=str,
                        default='rules.rsync',
                        dest='INPUT')
    parser.add_argument('-o', '--output',
                        help='path for output file (default "./pattern_rules.rsync")',
                        type=str,
                        default='pattern_rules.rsync',
                        dest='OUTPUT')
    parser.add_argument("-b", "--backup",
                        help="perform backup (else a dry run)",
                        action="store_false",
                        dest="DRYRUN")
    parser.add_argument("-a", "--args",
                        help="custom arguments for rsync (default aPmv)",
                        type=str,
                        default="aPmv",
                        dest="rsync_args")
    parser.add_argument("-l", "--no-log",
                        help="do not log rsync progress",
                        action="store_false",
                        dest="LOG")
    args = parser.parse_args()

    # Generate pattern rule file for rsync
    rsync_rules.pattern_rules(args.INPUT, args.OUTPUT, args.VERBOSE)

    # Get backup path (see documentation)
    if args.path.endswith("/"):
        backup_path = args.path
    else:
        backup_path = args.path + "/" + datetime.now().strftime(FORMAT) + "/"
        # Test if backup_path already exists...
        test_path = backup_path
        loop_index = 0
        while os.path.isdir(test_path):
            # ...if so, backup to /[DATE-TIME]/X/ where X does not exist
            test_path = backup_path + str(loop_index) + "/"
            loop_index += 1
        backup_path = test_path

    # Generate arguments for rsync
    rsync_call = 'rsync -' + args.rsync_args + ' --include-from="' \
                 + args.OUTPUT + '" / ' + backup_path
    if args.LOG:
        rsync_call += ' --log-file="rsync.log"'
    if args.DRYRUN:
        rsync_call += ' --dry-run'

    # Run rsync backup
    print('Running "', rsync_call, '"', sep='')
    subprocess.run(rsync_call, shell=True)
