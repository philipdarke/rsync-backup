#!/usr/bin/env python3
#
# Generate filter rules for rsync
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

import sys
import os
import argparse
from datetime import datetime

# Date/time format for output
FORMAT = '%H.%M.%S'


def logger(raw_text, output, log):
    """Writes output to file

    :param raw_text: String to write.
    :param output: File to write output to.
    :param log: Prints string to console if True.
    :return:
    """
    output.write(raw_text)
    if log:
        sys.stdout.write(raw_text)
        sys.stdout.flush()


def convert_path(path):
    """Convert from Windows path to Linux path.

    :param path: Path to convert.
    :return: Path in Linux format.
    """
    # Assume path is Linux if starts with a forward-slash
    if path.startswith('/'):
        return path
    else:
        # Remove colon and convert back-slashes to forward-slashes
        linux_path = path.replace(':', '', 1).replace('\\', '/')
        # Add initial "mnt/" and convert drive letter to lower case
        linux_path = '/mnt/' + linux_path[0].lower() + linux_path[1:]

    return linux_path


def get_subdirs(path):
    """Generate a list of all subdirectories for a path.

    :param path: Path containing subdirectories.
    :return: List of all subdirectories in the path (including the path).
        If path is a filepath, returns the filepath in a list of length one.
    """
    subdirs = []

    if path.endswith('/'):
        # Walk down the tree and append subdirectory names to list
        for dir, subdir, file in os.walk(path):
            fwd_slash = '/' if dir[-1:] != '/' else ''
            subdirs.append(dir + fwd_slash)
            subdirs.append(dir + fwd_slash + '*')
    else:
        # If path points to a file, add path to list
        subdirs.append(path)

    return subdirs


def get_parentdirs(path):
    """Generate a list of all parent directories for a path.

    :param path: Path to find parent directories for.
    :return: List of all parent directories for the path (including the path).
    """
    # Split path into a list for each level
    path_split = [x + '/' for x in path.split('/')[:-1]]

    # Build up all parent directories and return as a list
    parentdirs = []
    for path in path_split[1:]:
        parentdirs.append(''.join(path_split))
        path_split = path_split[:-1]

    return parentdirs


def pattern_rules(input, output, verbose):
    """Process input file and write pattern rules to output file.

    :param input: Input file to process.
    :param output: Output file path.
    :param verbose: Print all file output to console.
    """
    include = []
    exclude = []
    partial_exclude = []

    # Populate path lists
    print('[', datetime.now().strftime(FORMAT), ']: ',
          'Processing rules file...', sep='')
    with open(input) as input_file:
        for line in input_file:
            # Skip line if it is blank or commented out
            if len(line) == 0 or line.startswith('#'):
                continue
            # Remove trailing whitespaces
            line = line.rstrip()
            # Add directory to partial_exclude list if line starts with "* "
            if line.startswith('* '):
                temp_exclude = line[2:].replace('\\', '/')
                if not temp_exclude.startswith('/'):
                    temp_exclude = '/' + temp_exclude
                if not temp_exclude.endswith('/'):
                    temp_exclude += '/'
                partial_exclude.append(temp_exclude)
            # Add directory to include list if line starts with "+"
            elif line.startswith('+ '):
                include.append(convert_path(line[2:]))
            # Add directory to exclude list if line starts with "-"
            elif line.startswith('- '):
                exclude.append(convert_path(line[2:]))

    # Get directories (sub and parent) to include in backup
    print('[', datetime.now().strftime(FORMAT), ']: ',
          'Finding all paths to include...', sep='')
    included_paths = []
    for inc_path in include:
        included_paths.extend(get_subdirs(inc_path))
        included_paths.extend(get_parentdirs(inc_path))

    # Get subdirectories to exclude in backup
    print('[', datetime.now().strftime(FORMAT), ']: ',
          'Finding all paths to exclude...', sep='')
    excluded_paths = []
    for exc_path in exclude:
        excluded_paths.extend(get_subdirs(exc_path))

    # Remove excluded subdirectories
    print('[', datetime.now().strftime(FORMAT), ']: ',
          'Generating pattern rules...', sep='')
    paths_final = [path for path in included_paths if path not in excluded_paths]

    # Remove paths containing directories in the "partial exclude" list
    for exc_path in partial_exclude:
        paths_final = [path for path in paths_final if exc_path not in path]

    # Remove any duplicate directories, sort and write to output file
    print('[', datetime.now().strftime(FORMAT), ']: ',
          'Writing pattern rules to ', output, '...', sep='')
    with open(output, 'w') as outfile:
        for path in sorted(set(paths_final)):
            logger('+ ' + path + '\n', outfile, verbose)
        logger('- *\n', outfile, verbose)


# Main -------------------------------------------------------------------------

if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(prog='rsync_rules',
                                     description='Generate filter rules for rsync.')
    parser.add_argument('-v', '--verbose',
                        help='print pattern rules to console',
                        action='store_true',
                        dest='VERBOSE')
    parser.add_argument('-i', '--input',
                        help='path to rules file (default "./input_rules.rsync")',
                        type=str,
                        default='input_rules.rsync',
                        dest='INPUT')
    parser.add_argument('-o', '--output',
                        help='path for output file (default "./pattern_rules.rsync")',
                        type=str,
                        default='pattern_rules.rsync',
                        dest='OUTPUT')
    args = parser.parse_args()

    # Generate pattern rule file
    pattern_rules(args.INPUT, args.OUTPUT, args.VERBOSE)
