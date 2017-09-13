#!/bin/bash
dash_pid=$(<~/.dashcore/testnet3/dashd.pid)
sudo gdb --batch -ex "source debug.gdb" dashd ${dash_pid}