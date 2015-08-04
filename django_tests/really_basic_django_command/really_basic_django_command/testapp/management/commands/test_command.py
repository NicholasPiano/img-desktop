# testapp.command: test_command.py

# django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# util
import os
from optparse import make_option

### Command
class Command(BaseCommand):
  option_list = BaseCommand.option_list + (

    make_option('--expt', # option that will appear in cmd
      action='store', # no idea
      dest='expt', # refer to this in options variable
      default='050714-test', # some default
      help='Name of the experiment to import' # who cares
    ),

  )

  args = ''
  help = ''

  def handle(self, *args, **options):
    # 1. print to command line
    print(options['expt'])

    # 2. output to file in manage.py directory
