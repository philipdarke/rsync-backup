# rsync-backup
Tools to simplify using `rsync`

## Summary

[`rsync`](https://rsync.samba.org/) is a fast file copying tool that is well suited to creating system backups.  It supports incremental file transfers and the flexible selection of files and directories using pattern rules.  Unfortunately these rules quickly get complicated if you wish to selectively backup multiple directories.  See *include/exclude pattern rules* in the [documentation](https://download.samba.org/pub/rsync/rsync.html) and [many questions](https://api.duckduckgo.com/?q=rsync+filter+rules+site:stackoverflow.com) on Stack Overflow.

This repository contains two tools to simplify using `rsync`:

* `rsync_rules.py` builds a list of pattern rules from a simplified input file.  This can then be used with `rsync` by passing the file using the `--include-from` argument.
* Alternatively, `rsync_backup.py` builds the pattern rules and carries out a backup using `rsync` in one step.

The pattern rule file generated is deliberately verbose to simplify debugging.  Every directory included in the backup is included on a separate line in the file.

The tools can be used under the [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/about) to backup a Windows system.  See [below](#wsl) for more information.

:warning: **As with any backup tool, carry out detailed testing first.  Use at own risk!**

## Instructions for use

1. Clone or download the repository.
1. Add the paths for the files and directories you wish to backup in `input_rules.rsync`.  See [Input file](#input) for how to structure the input file.
1. Run `./rsync_rules.py` to generate the pattern rules file for use with `rsync`.
1. Alternatively, run `./rsync_backup.py PATH -b [OPTIONAL PARAMETERS]` to carry out the backup.  `PATH` is the location you wish to backup to.

### <a name="input">Input file</a>

A [template `input_rules.rsync` file](https://github.com/philipdarke/rsync-backup/blob/master/input_rules.rsync) is provided.  See the [tutorial](https://github.com/philipdarke/rsync-backup/blob/master/TUTORIAL.md) for usage examples.

1. Individual files or directories to include in the backup should start with "+" e.g. `+ ~/notes.md` or `+ ~/`.  When a directory is included, all subdirectories will also be included.
1. Individual directories to exclude from the backup should start with "-" e.g. `- ~/gems/`.  All subdirectories will also be excluded. It is not possible to exclude a specific file, only a directory and its subdirectories.
1. If you want to exclude every instance of a named directory, start with "*" with no closing back/forward slash. For example, adding the line `* .venv` will exclude from the backup **all** paths that include `/.venv/`.
1. All directories must end in a forward-slash.
1. Blank lines and lines starting with `#` (e.g. for comments) are ignored.
1. Windows paths can also be provided if using the Windows Subsystem for Linux (see [below](#wsl)).

### rsync_rules

`rsync_rules` generates the pattern rules file only.

The syntax is `./rsync_rules.py [OPTIONAL PARAMETERS]`.  The parameters are:

Parameter              | Description
---------------------- | -----------------------------------------------------------
`-i` or `--input`      | Path for the input file (default `./input_rules.rsync`).
`-o` or `--output`     | Where to save the `include-from` file containing the `rsync` filter rules (default `./pattern_rules.rsync`).
`-v` or `--verbose`    | Print the pattern rules to the console as they are generated.
`-h` or `--help`       | Display help message and exit.

### rsync_backup

`rsync_backup` generates the pattern rules file and passes it to `rsync` to carry out a backup.

The syntax is `./rsync_backup.py PATH [OPTIONAL PARAMETERS]`.  Note that `-b` or `--backup` must be passed to carry out a backup, otherwise a dry run takes place.

`PATH` is the location where the backup will be made.  See [below](#path) for more information.  The parameters are:

Parameter                  | Description
-------------------------- | -----------------------------------------------------------
`-i` or `--input`          | Path for the input file (default `./input_rules.rsync`).
`-o` or `--output`         | Where to save the `include-from` file containing the `rsync` filter rules (default `./pattern_rules.rsync`).
**`-b` or `--backup`**     | **Perform backup.  If `-b` is not specified, a dry run is performed where no files are copied.**
`-a` or `--args`           | Set custom arguments[*](#params) for `rsync` (default `aPmv`).
`-l` or `--log-file`       | Path to save the `rsync` log file.  A log file is not generated unless a path is passed.
`-k` or `--keep`           | Do not delete the `include-from` file after the backup is made.
`-h` or `--help`           | Display help message and exit.

<a name="params">\*<a> See the [`rsync` documentation](https://download.samba.org/pub/rsync/rsync.html) for a full list of parameters.  The default parameters used are `a` (archive mode), `P` (show progress), `m` (do not create empty directories) and `v` (verbose console output).

### <a name="path">Path</a>

`PATH` is the location where the backup will be made.

If the path ends in a forward-slash (e.g. `~/backups/`) the backup will be made to this location.  This allows sequential backups to be made to the same location using the incremental file transfer features of `rsync`.

If the path does not end in a forward-slash (e.g. `~/backups`) the backup will be made to a subdirectory with the current date and time i.e. `~/backups/dd.mm.yyyy-hh.mm.ss/` (or a numbered subdirectory if this already exists).

### <a name="wsl">Windows Subsystem for Linux</a>

The [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/about) (WSL) neatly provides a Linux development environment in Windows 10 without the overhead of a virtual machine.  This opens the way to using Linux tools on Windows files.  

The input file will accept both Windows and Linux paths, therefore `rsync_rules` and `rsync_backup` let WSL users use the Linux utility `rsync` to make system backups.

#### Using the tools under the WSL

*Input file*

Paths can be provided in Windows format including the drive letter.  For example `+ C:\Users\` or `- C:\temp\`.

*`PATH` argument for `rsync_backup`*

Windows paths is must be passed as a string or by escaping the back-slashes.  For example `/mnt/c/backups/`, `"C:\Backups\"` and `C:\\Backups\\` will all backup to `C:\Backups\`.

*Mounting external drives*

By default, WSL mounts all fixed drives when launching Bash.  External storage (e.g. removeable drives or USB sticks) and network locations can be mounted manually by creating a directory under `/mnt/` and mapping the Windows drive.

For example, the following mounts an external drive with the Windows letter `E:` under `/mnt/e/`:

```
$ sudo mkdir /mnt/e
$ sudo mount -t drvfs E: /mnt/e
```

See further details [here](https://blogs.msdn.microsoft.com/wsl/2017/04/18/file-system-improvements-to-the-windows-subsystem-for-linux/).

## Licence

Made available under the [MIT licence](https://github.com/philipdarke/rsync-backup/blob/master/LICENSE)
