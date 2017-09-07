#!/usr/bin/python

try:
    import gdb
except ImportError as e:
    raise ImportError("This script must be run in GDB: ", str(e))
    
logFileName = "memlog.txt"


class DashdBreaksCommand (gdb.Command):
    """Dumps memory operations : malloc, realloc, calloc and free"""

    def __init__ (self):
        super (DashdBreaksCommand, self).__init__ ("dashd_breaks", gdb.COMMAND_USER)
        self.breaks = ["exit", "__libc_malloc" , "__libc_free", \
                                "__libc_calloc", "__libc_realloc"]

    def invoke (self, arg, from_tty):
        gdb.execute("set confirm off")
        gdb.execute("set pagination off")
        gdb.execute("set non-stop on")
        gdb.execute("set breakpoint pending on")
        # Setup breakpoints for memory functions
        for breakpoint in self.breaks:
            gdb.execute("b " + breakpoint)
        # Continue execution
        gdb.execute("cont")
        while True:
            frame = gdb.selected_frame()
            current_frame_name = str(frame.name())
            ##########################################################################
            #EXIT
            if "exit" in current_frame_name:
                Utility.writeInfoMessage("\n")
                break
            ##########################################################################
        # Remove breakpoints
        for breakpoint in self.breaks:
            gdb.execute("clear " + breakpoint)
        gdb.execute("cont")

DashdBreaksCommand()
