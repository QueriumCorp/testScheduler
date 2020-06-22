###############################################################################
# xxx

# Requirements
# Python >= 3.4
# Git 1.7.0 or newer

# Need the following modules
# python3 -m pip install python-dotenv

###############################################################################
import time
import os
import sys
from dotenv import load_dotenv
load_dotenv()

###############################################################################
#   Support functions
###############################################################################

###############################################################################
#   Testing
###############################################################################
def testing():
    print ("testing")

    ## testing environment variables
    print (os.environ.get('USER'))
    print (os.environ.get('api-token'))


    sys.exit(0)


###############################################################################
#   Main
###############################################################################
if __name__ == '__main__':
    print ("\nSTART:", time.strftime("%c"))
    testing()

    print ("\nEND:", time.strftime("%c"))