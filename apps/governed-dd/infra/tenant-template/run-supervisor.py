"""Bound remote execution to the SSH session, including detached tool children."""
import ctypes
import os
import signal
import subprocess
import sys
import time

ctypes.CDLL(None).prctl(36, 1, 0, 0, 0)  # Adopt orphaned descendants on Linux.
parent = os.getppid()
stopping = False

def stop(*_):
    global stopping
    stopping = True

signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGHUP, stop)
signal.signal(signal.SIGINT, stop)
child = subprocess.Popen(['flock', '-w', '300', '/run-gate/active.lock',
                          'timeout', '--signal=TERM', '--kill-after=15s', '1800',
                          'codex', *sys.argv[1:]])

def descendants():
    parents = {}
    for item in os.listdir('/proc'):
        if not item.isdigit():
            continue
        try:
            tail = open('/proc/' + item + '/stat').read().rsplit(')', 1)[1].split()
            parents[int(item)] = int(tail[1])
        except (OSError, ValueError, IndexError):
            pass
    found = {os.getpid()}
    while True:
        expanded = found | {pid for pid, ppid in parents.items() if ppid in found}
        if expanded == found:
            return found - {os.getpid()}
        found = expanded

while child.poll() is None and not stopping:
    if os.getppid() != parent or parent == 1:
        stopping = True
        break
    time.sleep(0.25)

# Clean all process sessions, including Codex tools that create their own groups.
for sig in (signal.SIGTERM, signal.SIGKILL):
    for pid in descendants():
        try:
            os.kill(pid, sig)
        except ProcessLookupError:
            pass
    time.sleep(1)
sys.exit(143 if stopping else child.returncode)
