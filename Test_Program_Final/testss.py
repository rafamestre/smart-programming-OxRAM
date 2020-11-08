
from shutil import copyfile
FILE = "launcher.py"

copyfile(FILE,'auxfile.py')

from auxfile import test_die

test_die()
