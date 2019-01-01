#!/usr/bin/env python3

# Parse Windows files/folders for use by rsync
# Philip Darke (January 2019)
# philipdarke.com

# Import packages --------------------------------------------------------------

import sys
import os

# Input and output files -------------------------------------------------------

INCLUDE_FILE = "include.rsync"
EXCLUDE_FILE = "exclude.rsync"
OUTPUT_FILE = "backup.rsync"
HOME = ["/home/", "/home/philipdarke/", "/home/philipdarke/*"]
LOG = False

# Functions --------------------------------------------------------------------

# logger()
# Prints raw string to file and also to console if LOG is True
def logger(raw_text):
    output.write(raw_text)
    if LOG == True:
        sys.stdout.write(raw_text)
        sys.stdout.flush()

# convert_path()
# Convert Windows path to Unix path
def convert_path(path):
    # Remove colon, convert \ to / and remove trailing whitespaces
    unix_path = path.replace(":", "", 1).replace("\\", "/").rstrip()
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
            # Add directory to global_exclude list if line is not a path
            if line[:1] == "\\":
                global_exclude.append(line.replace("\\", "/").rstrip())
            # Otherwise add to list of paths (check if commented out or blank)
            elif line[:1] != "#" and line[:1] != "":
                paths.append(convert_path(line))
    return(paths)

# Main -------------------------------------------------------------------------

# Variables to hold path lists
included_paths = HOME
excluded_paths = []
global_exclude = []

# Process input files
print("Processing input files...")
paths_inc = process_file(INCLUDE_FILE)
paths_exc = process_file(EXCLUDE_FILE)

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
print("Writing results to", OUTPUT_FILE)
with open(OUTPUT_FILE, "w") as output:
    for path in sorted(set(paths_final)):
        logger("+ " + path + "\n")
    logger("- *\n")
