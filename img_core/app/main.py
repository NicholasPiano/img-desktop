# python wrapper to start tornado server process and thrust browser window.

import os
import subprocess

env = os.environ.copy()
env['PYTHONPATH'] = '.'
env['DJANGO_SETTINGS_MODULE'] = 'testsite.settings'

# 1. open tornado process
# maybe find some way to capture stderr and stdout

tornado_proc = subprocess.Popen(['python3.4', './testsite/tornado_main.py'], env=env)
print('tornado id: {}'.format(tornado_proc.pid)) # always do this or you lose it. Maybe look for python3.4 in top if lost.

# maybe I have to wait for a bit
import time
time.sleep(1)

thrust_proc = subprocess.Popen(['node', './start.js'])
print('thrust id: {}'.format(thrust_proc.pid))
