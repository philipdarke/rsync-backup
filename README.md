# rsync-backup
Quickly backup your Windows machine using `rsync` and the Windows Subsystem for Linux

## Summary

The [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/about) (WSL) neatly provides a Linux development environment in Windows 10 without the overhead of a virtual machine.  This opens the way to using Linux tools on Windows files.  `rsync-backup` helps you use the WSL with the Linux utility `rsync` to make system backups.

[`rsync`](https://rsync.samba.org/) is a fast file copying tool that is well suited to creating system backups.  `rsync` supports incremental file transfers and the flexible selection of files and directories using filter rules.

Unfortunately these filter rules quickly get complicated if you wish to selectively backup multiple directories.  See *include/exclude pattern rules* in the [`rsync` documentation](https://download.samba.org/pub/rsync/rsync.html) and many questions on [Stack Overflow](https://www.google.com/search?q=rsync+filter+rules+site:stackoverflow.com).

`rsync-backup` builds a list of these filter rules from a simple input file and carries out the backup using `rsync`.  **As with any backup tool, carry out detailed testing before using `rsync-backup`.  Use at own risk!**

## Instructions for use

1. Clone or download to a Windows folder or a WSL directory.
2. Add the paths for the files and directories you wish to backup in `input.rsync`.
3. Run `./rsync_backup PATH -b PARAMETERS` from the WSL to carry out the backup.  `PATH` is the location you wish to backup to (if using a Windows path it must be passed as a string or by escaping the back-slashes e.g. `"C:\Backups\"` or `C:\\Backups\\`).

**See further details below and the [tutorial](https://github.com/philipdarke/rsync-backup/blob/master/TUTORIAL.md) for usage examples.**

### `PATH`

`PATH` is the location where the backup will be made.  If it is a Windows path is must be passed as a string or by escaping the back-slashes.  For example `/mnt/c/backups/`, `"C:\Backups\"` and `C:\\Backups\\` will all backup to `C:\Backups\`.

If the path ends in a forward-slash (e.g. `/mnt/c/backups/`) the backup will be made to this location.  This allows sequential backups to be made to the same location using the incremental file transfer features of `rsync`.

If the path does not end in a forward-slash (e.g. `/mnt/c/backups`) the backup will be made to a subdirectory with the current date and time i.e. `/mnt/c/backups/dd.mm.yyyy-hh.mm.ss/`.

Note that if `/mnt/c/backups/dd.mm.yyyy-hh.mm.ss/` already exists, then the backup will be made to a numbered subdirectory that does not already exist e.g. `/mnt/c/backups/dd.mm.yyyy-hh.mm.ss/0/`.

### `PARAMETERS`

Parameter          | Description
------------------ | -----------------------------------------------------------
`-b` or `--backup` | Perform backup.  If `-b` is not specified, a dry run is performed but no files are copied.
`-a` or `--args`   | Set custom arguments[*](#note1) for `rsync` (default `aR`).
`-i` or `--input`  | Path for the input file (default `input.rsync`).
`-o` or `--output` | Path for the `include-from` file containing the filter rules for `rsync` (default `backup.rsync`).
`-k` or `--keep`   | Do not delete the `include-from` file after the backup is made.
`-q` or `--quiet`  | Quiet mode i.e. do not show `rsync` progress during a backup.
`-h` or `--help`   | Display help message and exit.

<a name="note1">\*<a> See the [`rsync` documentation](https://download.samba.org/pub/rsync/rsync.html) for a full list of parameters.

### `input.rsync`

A [template `input.rsync` file](https://github.com/philipdarke/rsync-backup/blob/master/input.rsync) is provided.  See the [tutorial](https://github.com/philipdarke/rsync-backup/blob/master/TUTORIAL.md) for usage examples.

1. Individual files/directories to include in the backup should start with `+` e.g. `+ /home/`.  All subdirectories will also be included.

2. Individual directories to exclude from backup should start with `-` e.g. `- /home/gems/`.  All subdirectories will also be excluded. It is not possible to exclude a specific file, only a directory and its subdirectories.

3. If you want to exclude multiple directories with the same name, start the directory name with `*` with no closing back/forward slash. For example, adding the line `* .venv` will result in all paths including `/.venv/` (plus their subdirectories) being excluded.

4. Paths can be Windows format (starting with the drive letter) or Linux format (starting with a forward-slash).

5. All directories must end in a forward-slash (Linux paths) or a backward-slash (Windows paths).

6. Blank lines and lines starting with `#` are ignored.

## Licence

Made available under the [MIT licence](https://github.com/philipdarke/rsync-backup/blob/master/LICENSE)
