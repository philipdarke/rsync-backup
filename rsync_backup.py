#!/usr/bin/env python3

# Backup selected files/folders using rsync
# Philip Darke (January 2019)
# philipdarke.com

# Import packages --------------------------------------------------------------

import sys
import os
import argparse
import subprocess
import time

# Main -------------------------------------------------------------------------

def main(argv):

    # Parse arguments
    parser = argparse.ArgumentParser(prog="rsync_backup",
                                     description="Backup selected files/folders using rsync")
    parser.add_argument("path", help="Path for backup")
    parser.add_argument("-b", "--backup", help="Make backup (else does a dry run)",
                        action="store_false", dest="DRYRUN")
    parser.add_argument("-a", "--args", help="Arguments for rsync (default ar)",
                        type=str, default="ar", dest="rsync_args")
    parser.add_argument("-i", "--input", help="Path to input.rsync file",
                        type=str, default="input.rsync", dest="INPUT_FILE")
    parser.add_argument("-o", "--output", help="Path for include-from file",
                        type=str, default="backup.rsync", dest="OUTPUT_FILE")
    parser.add_argument("-k", "--keep", help="Retain include-from file",
                        action="store_false", dest="DELETE_OUTPUT")
    parser.add_argument("-q", "--quiet", help="Show less console output",
                        action="store_false", dest="LOG")
    parser.add_argument("--version", action="version", version="%(prog)s b5.0")
    args = parser.parse_args()

    # Process input file
    print("Processing input file...")
    paths = process_file(args.INPUT_FILE)

    # Get directories (sub and parent) to include in backup
    print("Finding all paths to include...")
    included_paths = []
    for inc_path in paths[0]:
        included_paths.extend(get_subdirs(inc_path))
        included_paths.extend(get_parentdirs(inc_path))

    # Get subdirectories to exclude in backup
    print("Finding all paths to exclude...")
    excluded_paths = []
    for exc_path in paths[1]:
        excluded_paths.extend(get_subdirs(exc_path))

    # Remove excluded subdirectories
    print("Generating list of paths to backup...")
    paths_final = [path for path in included_paths if path not in excluded_paths]

    # Remove paths containing directories in the "partial exclude" list
    for exc_path in paths[2]:
        paths_final = [path for path in paths_final if exc_path not in path]

    # Remove any duplicate directories, sort and print results to output file
    print("Writing path list to", args.OUTPUT_FILE)
    with open(args.OUTPUT_FILE, "w") as output:
        for path in sorted(set(paths_final)):
            logger("+ " + path + "\n", output, args.LOG)
        logger("- *\n", output, args.LOG)

    # Set backup path
    if args.path.endswith("/"): backup_path = args.path
    else:
        backup_path = args.path + "/" + time.strftime("%d.%m.%Y") + "/"
        # Test if backup_path already exists...
        test_path = backup_path
        loop_index = 0
        while os.path.isdir(test_path):
            # ...if so, backup to a subfolder /loop_index/ which does not exist
            test_path = backup_path + str(loop_index) + "/"
            loop_index += 1
        backup_path = test_path

    # Form arguments for rsync
    if args.DRYRUN: args.rsync_args += "n"
    rsync_call = "rsync -" + args.rsync_args + " --include-from=" \
                 + args.OUTPUT_FILE + " / " + backup_path
    if args.LOG: rsync_call = rsync_call + " --progress --verbose"

    # Run rsync and delete temporary file if DELETE_OUTPUT is True
    print(rsync_call)
    subprocess.run(rsync_call, shell=True)
    if args.DELETE_OUTPUT: os.remove(args.OUTPUT_FILE)

# Functions --------------------------------------------------------------------

# logger()
# Prints raw string to file and also to console if log is True
def logger(raw_text, output, log):
    output.write(raw_text)
    if log:
        sys.stdout.write(raw_text)
        sys.stdout.flush()

# convert_path()
# Convert Windows path to Linux path
def convert_path(path):
    # Assume path is Linux if starts with a forward-slash
    if path.startswith("/"): return(path)
    else:
        # Remove colon and convert back-slashes to forward-slashes
        linux_path = path.replace(":", "", 1).replace("\\", "/")
        # Add initial "mnt/" and convert drive letter to lower case
        linux_path = "/mnt/" + linux_path[0].lower() + linux_path[1:]
    return(linux_path)

# get_subdirs()
# Generates a list of all subdirectories for a path (includes the path/file)
def get_subdirs(path):
    subdirs = []
    if path.endswith("/"):
        # Walk down the tree and append subdirectory names to list
        for dir, subdir, file in os.walk(path):
            fwd_slash = "/" if dir[-1:] != "/" else ""
            subdirs.append(dir + fwd_slash)
            subdirs.append(dir + fwd_slash + "*")
    else:
        # If path points to a file, add path to list
        subdirs.append(path)
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
# Process each path in input file to form lists of Linux format paths
def process_file(file):
    # Variables to hold path lists
    include = []
    exclude = []
    partial_exclude = []
    # Populate path lists
    with open(file) as input_file:
        for line in input_file:
            # Skip line if it is blank or commented out
            if len(line) == 0 or line.startswith("#"): continue
            # Remove trailing whitespaces
            line = line.rstrip()
            # Add directory to partial_exclude list if line starts with ":"
            if line.startswith(":"):
                temp_exclude = line[1:].replace("\\", "/")
                if not temp_exclude.startswith("/"): temp_exclude = "/" + temp_exclude
                if not temp_exclude.endswith("/"): temp_exclude += "/"
                partial_exclude.append(temp_exclude)
            # Add directory to include list if line starts with "+"
            elif line.startswith("+"):
                include.append(convert_path(line[1:]))
            # Add directory to exclude list if line starts with "-"
            elif line.startswith("-"):
                exclude.append(convert_path(line[1:]))
    return(include, exclude, partial_exclude)

# Run program if main ----------------------------------------------------------

if __name__ == "__main__":
    main(sys.argv)
