# woot.expt.exec

'''
Stores scripts that would be run in steps, but need to be called from the interface. Hopefully, can hook into interface
feedback or be chopped up into repeatable sections per image or series.
'''

# django

# local

# util

### SCRIPTS
def run():
  from django.core.management import call_command
  call_command('syncdb', interactive=False)
