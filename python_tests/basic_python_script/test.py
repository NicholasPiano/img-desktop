# The purpose of this script is to test compilation of a basic python program on windows. The most reliable way
# is to write a string to a file. The command line will be suppressed during compilation.

import os
import datetime

self_path = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(self_path, 'test.txt'), 'w+') as f:
  f.write(str(datetime.datetime.now()) + '\n')
