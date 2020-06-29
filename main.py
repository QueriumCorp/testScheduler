###############################################################################
# main.py
# The main module

# Requirements
# Python >= 3.4
# Git 1.7.0 or newer

# Need the following modules
# python3 -m pip install python-dotenv
# python3 -m pip install requests

# To run
# python3 main.py

###############################################################################
import time
import jql
import test

###############################################################################
#   Main
###############################################################################
if __name__ == '__main__':
    print ("\nSTART:", time.strftime("%c"))

    ### testing code
    # test.issueSearch()

    print ("\nEND:", time.strftime("%c"))