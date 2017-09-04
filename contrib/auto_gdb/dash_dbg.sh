#!/bin/bash
dash_pid=$(<~/.dashcore/testnet3/dashd.pid)
sudo gdb -ex "source used_size.py" -ex "source test_used_size.gdb" -ex "test_used_size mnodeman.vMasternodes" dashd ${dash_pid}