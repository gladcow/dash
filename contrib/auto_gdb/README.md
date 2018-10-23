# Contents
This directory contains tools to automatically get data about the memory consumption by some objects in dashd process with the help of GDB debugger.

## dash_dbg.sh
This shell script attaches GDB to the running dashd process (should be built with debug info), executes debug.gdb script and detaches.
By default it uses testnet settings, see script comments to attach it to mainnet dashd.

## debug.gdb
Contains debugger instructions to execute during attach: loads python code and executes it for the objects we want to investigate.

## log_size.py
Contains definition of the gdb command log_size. After loading of this script it can be called from gdb command line or other gdb scripts.
Command params:
`log_size arg0 arg1`
`arg0` - name of object whose memory will be written in log file
`arg1` - name of the log file
Example:
```
log_size mnodeman "memlog.txt"
```

## used_size.py
Contains definition of the gdb command used_size. After loading of this script it can be called from gdb command line or other gdb scripts.
Command params:
`used_size arg0 arg1`
`arg0` - variable to store memory used by the object
`arg1` - name of object whose memory will be calculated and stored in the first argument
Example:
```
>(gdb) set $size = 0
>(gdb) used_size $size mnodeman
>(gdb) p $size
```

## stl_containers.py
Contains helper classes to calculate memory used by the STL containers (list, vector, map, set, pair)

## simple_class_obj.py
Contains helper class to calculate memory used by the object as a sum of the memory used by its fields.
All processed objects of such type are listed in the this file,  you can add new types you are interested in to this list.
If some type is not listed here,  his size is calculated as sizeof result (except STL containers which are processed in stl_containers.py).

## common_helpers.py
Several helper functions that are used in other python code.

