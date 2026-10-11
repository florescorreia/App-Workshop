"""Cross-runtime lock, timeout and cancellation checks without model costs."""
import subprocess,time
from pathlib import Path
assert Path('/run-gate').exists()
p=subprocess.Popen(['flock','-n','/run-gate/active.lock','sleep','20'])
time.sleep(.3)
assert subprocess.run(['flock','-n','/run-gate/active.lock','true']).returncode==1
p.terminate();p.wait(timeout=3)
# The subprocess may retain the open file description until it exits; kill the process group via timeout in real harness.
q=subprocess.run(['timeout','--kill-after=1s','1','sleep','20'])
assert q.returncode==124
print('Exclusive file lock contention and bounded timeout passed; real Paperclip cancellation checked separately.')
