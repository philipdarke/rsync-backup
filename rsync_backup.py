#!/usr/bin/env python3

# Parse files/folders for use by rsync
# Philip Darke (January 2019)
# philipdarke.com

# Import packages --------------------------------------------------------------

import sys
import os
import argparse

# Parse arguments --------------------------------------------------------------

parser = argparse.ArgumentParser(prog="rsync_backup",
                                 description="Parses files/folders for use by rsync")
parser.add_argument("-i", "--include", help="Path to include.rsync file",
                    type=str, default="include.rsync", dest="INCLUDE_FILE")
parser.add_argument("-e", "--exclude", help="Path to exclude.rsync file",
                    type=str, default="exclude.rsync", dest="EXCLUDE_FILE")
parser.add_argument("-o", "--output", help="Path for output file", type=str,
                    default="backup.rsync", dest="OUTPUT_FILE")
parser.add_argument("-v", "--verbose", help="Show more console output",
                    action="store_true", dest="LOG")
parser.add_argument("--version", action="version", version="%(prog)s b2.0")
args = parser.parse_args()

# Input and output files -------------------------------------------------------

#HOME = ["/home/", "/home/philipdarke/", "/home/philipdarke/*"]

# Functions --------------------------------------------------------------------

# logger()
# Prints raw string to file and also to console if LOG is True
def logger(raw_text):
    output.write(raw_text)
    if args.LOG == True:
        sys.stdout.write(raw_text)
        sys.stdout.flush()

# convert_path()
# Convert Windows path to Unix path
def convert_path(path):
    # Remove colon and convert back-slashes to forward-slashes
    unix_path = path.replace(":", "", 1).replace("\\", "/")
    # Add mnt/ and convert drive letter to lower case
    unix_path = "/mnt/" + unix_path[0].lower() + unix_path[1:]
    return(unix_path)

# get_subdirs()
# Generates a list of all subdirectories for a path (includes the path/file)
def get_subdirs(path):
    subdirs = []
    if path[-1:] != "/":
        subdirs.append(path)  # If path points to a file, add path to list
    else:
        # Otherwise walk down the tree and append subdirectory names to list
        for dir, subdir, file in os.walk(path):
            fwd_slash = "/" if dir[-1:] != "/" else ""
            subdirs.append(dir + fwd_slash)
            subdirs.append(dir + fwd_slash + "*")
    print(subdirs)
    return(subdirs)

# get_parentdirs()
# Generates a list of all parent directories for a path (includes the path)
def get_parentdirs(path):
    # Split path into a list for each level
    path_split = [x + "/" for x in path.split("/")[:-1]]
    # Build up all parent directories and return as a list
    parentdirs = []
    for path in path_split[1:]:
        parentdirs.append("".join(path_split))
        path_split = path_split[:-1]
    return(parentdirs)

# process_file()
# Read each path of input file into a list of Linux format paths
def process_file(file):
    paths = []
    with open(file) as input_file:
        for line in input_file:
            # Remove trailing whitespaces
            line = line.rstrip()
            # Skip line if is blank or commented out
            if line[:1] == "" or line[:1] == "#": continue
            # Add directory to global_exclude list if line is not a path
            if line[:1] == "\\": global_exclude.append(line.replace("\\", "/"))
            # Add to list of paths if is a Linux path
            elif line[:1] == "/": paths.append(line)
            # Otherwise convert to Linux path and add
            else: paths.append(convert_path(line))
    return(paths)

# Main -------------------------------------------------------------------------

# Variables to hold path lists
included_paths = []
excluded_paths = []
global_exclude = []

# Process input files
print("Processing input files...")
paths_inc = process_file(args.INCLUDE_FILE)
paths_exc = process_file(args.EXCLUDE_FILE)

# Get directories (sub and parent) to include in backup
print("Finding all paths to include...")
for path in paths_inc:
    included_paths.extend(get_subdirs(path))
    included_paths.extend(get_parentdirs(path))

# Get subdirectories to exclude in backup
print("Finding all paths to exclude...")
for path in paths_exc:
    excluded_paths.extend(get_subdirs(path))

# Remove excluded subdirectories
print("Generating list of paths to backup...")
paths_final = [path for path in included_paths if path not in excluded_paths]

# Remove directories in global_exclude
for exclude in global_exclude:
    paths_final = [path for path in paths_final if exclude not in path]

# Remove any duplicate directories, sort and print results to file
print("Writing results to", args.OUTPUT_FILE)
with open(args.OUTPUT_FILE, "w") as output:
    for path in sorted(set(paths_final)):
        logger("+ " + path + "\n")
    logger("- *\n")
