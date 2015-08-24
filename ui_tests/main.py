# from testsite.tornado_main import main as server_main
# from browser import main as browser_main

# from multiprocessing import Process
#
# if __name__ == '__main__':
#   server_process = Process(target=server_main)
#   server_process.start()
#   server_process.join()
#
#   browser_process = Process(target=browser_main)
#   browser_process.start()
#   browser_process.join()

import subprocess

server_command = ['PYTHONPATH=. DJANGO_SETTINGS_MODULE=testsite.settings python testsite/tornado_main.py']
p = subprocess.Popen(server_command, shell=True)
