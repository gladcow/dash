#!/bin/bash
dash_pid=$(<~/.dashcore/testnet3/dashd.pid)
sudo gdb -ex "source used_size.py" -ex "source dashd_breaks.gdb" -ex "set_dashd_breaks" dashd ${dash_pid}