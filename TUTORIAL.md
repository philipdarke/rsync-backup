# rsync-backup tutorial
Quickly backup your Windows machine using `rsync` and the Windows Subsystem for Linux

## Example usage

Consider the contents of a simplified `C:` drive:

```
 - Program Files
 - Users
   - Documents
     - fileA.R
     - fileB.Rmd
     - Project
       - file1.py
       - file2.py
   - Downloads
 - Windows
```

Say you wish to backup the `Program Files` and `Users` folders, but not the `Users\Downloads` or `Windows` folders.

`backup.rsync` should therefore contain the following:

```
+C:\Program Files\
+C:\Users\
-C:\Users\Downloads\
-C:\Windows\
```

Note that paths can be Windows format (starting with the drive letter) or Linux format (starting with a forward-slash), but all directories must end in a backward-slash (Windows paths) or a forward-slash (Linux paths).

Running `./rsync_backup /mnt/c/backup/ -b` will copy the following files to `C:\backup\`:

```
 - Program Files
 - Users
   - Documents
     - fileA.R
     - fileB.Rmd
     - Project
       - file1.py
       - file2.py
```
