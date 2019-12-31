# rsync-backup tutorial
Tools to simplify using `rsync`

## Linux

Consider the contents of a simplified Linux drive:

```
 - bin
 - boot
 - dev
 - home
   - USER_NAME
     - Documents
       - fileA.py
       - fileB.md
       - .venv
         - lots of stuff...
       - Project
         - file1.py
         - file2.py
         - .venv
           - lots of stuff...
     - Downloads
 - lib
 - usr
 - var
```

You wish to backup `home` and `usr`, but not `~/Downloads` or any virtual environment directories (i.e. `.venv`).

`input_rules.rsync` should therefore contain the following:

```
+ /home/
+ /usr/
- ~/Downloads/
* .venv
```

Running `./rsync_backup.py /mnt/e/backup/ -b` will copy the following files to `mnt/e/backup/`:

```
 - home
   - USER_NAME
     - Documents
       - fileA.py
       - fileB.md
       - Project
         - file1.py
         - file2.py
 - usr
```

Alternatively, `./rsync_rules.py` will generate the pattern rules file `pattern_rules.rsync` for use directly with `rsync`.

## Windows Subsystem for Linux

Consider the contents of a simplified `C:` drive:

```
 - Program Files
 - Users
   - USER_NAME
     - Documents
       - fileA.py
       - fileB.md
       - Project
         - file1.py
         - file2.py
     - Downloads
 - Windows
```

You wish to backup `Program Files` and `Users`, but not `Users\USER_NAME\Downloads` or `Windows`. In addition, you wish to back up the Windows Subsystem for Linux home directory.

`input_rules.rsync` should therefore contain the following:

```
+ ~/
+ C:\Program Files\
+ C:\Users\USER_NAME\
- C:\Users\USER_NAME\Downloads\
- C:\Windows\
```

Note that paths can be Windows format (starting with the drive letter) or Linux format (starting with a forward-slash), but all directories must end in a backward-slash (Windows paths) or a forward-slash (Linux paths).

Running `./rsync_backup.py "E:\backup\" -b` will copy the WSL home drive to `E:\backup\home\USER_NAME\` and the following files to `E:\backup\mnt\c\`:

```
 - Program Files
 - Users
   - USER_NAME
     - Documents
       - fileA.py
       - fileB.md
       - Project
         - file1.py
         - file2.py
```

Alternatively, `./rsync_rules.py` will generate the pattern rules file `pattern_rules.rsync` for use directly with `rsync`.
