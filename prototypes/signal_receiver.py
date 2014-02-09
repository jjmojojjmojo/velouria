"""
Basic Signal Communication - Receiver

Receives signals, use the kill command.
"""

import os, signal

def handler(signum, frame):
    """
    Generic handler
    """
    print 'Signal handler called with signal', signum
    

def write_pid():
    """
    Writes the current process id to ./signal_reciever.pid
    """
    fh = open("./signal_reciever.pid", "w")
    fh.write(os.getpid())
    fh.close()
    

signal.signal(signal.SIGHUP, handler)
signal.signal(signal.SIGUSR1, handler)
signal.signal(32456, handler)

print "Current PID: %s" % (os.getpid())
write_pid()


while 1:
    True
