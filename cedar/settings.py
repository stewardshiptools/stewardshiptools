from platform import node

from cedar.settings_base import *

server = node()

if 'prod2' in server:
    from cedar.settings_prod2 import *
elif 'badger' in server:
    from cedar.settings_badger import *
elif 'cnbMBP.local' in server:
    from cedar.settings_cnbMBP import *
else:
    from cedar.settings_local import *
    #raise Exception("Problem in settings.py. Please run lines 1 & 3 of settings.py in python shell"
    #                " to see if outcome is covered in settings.py")
