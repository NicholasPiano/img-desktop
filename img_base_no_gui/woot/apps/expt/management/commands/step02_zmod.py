# expt.command: step03_zmod

# django
from django.core.management.base import BaseCommand, CommandError

# local
from apps.img.models import Composite
from apps.expt.util import *

# util
from optparse import make_option

spacer = ' ' *  20

### Command
class Command(BaseCommand):
  option_list = BaseCommand.option_list + (

    make_option('--expt', # option that will appear in cmd
      action='store', # no idea
      dest='expt', # refer to this in options variable
      default='050714-test', # some default
      help='Name of the experiment to import' # who cares
    ),

    make_option('--series', # option that will appear in cmd
      action='store', # no idea
      dest='series', # refer to this in options variable
      default='13', # some default
      help='Name of the series' # who cares
    ),

  )

  args = ''
  help = ''

  def handle(self, *args, **options):
    '''
    1. What does this script do?
    > Make images that can be recognized by CellProfiler by multiplying smoothed GFP with the flattened Brightfield

    2. What data structures are input?
    > Channel

    3. What data structures are output?
    > Channel

    4. Is this stage repeated/one-time?
    > One-time

    Steps:

    1. Select composite
    2. Call pmod mod on composite
    3. Run

    '''

    # 1. select composite
    composite = Composite.objects.get(experiment__name=options['expt'], series__name=options['series'])

    # 2. Call zmod mod
    if composite.channels.filter(name='-zmod').count()==0:
      mod = composite.mods.create(id_token=generate_id_token('img', 'Mod'), algorithm='mod_zmod')

      # 3. Run mod
      print('step02 | processing mod_zmod...', end='\r')
      mod.run()
      print('step02 | processing mod_zmod... done.{}'.format(spacer))

    else:
      print('step02 | zmod already exists...')
