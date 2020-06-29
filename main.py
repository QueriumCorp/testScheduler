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
import input
import jql
import test

###############################################################################
#   Main
###############################################################################
if __name__ == '__main__':
    print ("\nSTART:", time.strftime("%c"))

    ### testing code
    # test.issueSearch()

    ### Get filter input
    filter = input.getFilter()
    print ("input:", filter)

    ### Search jira based on the filter
    result = jql.issueSearch(filter, flatten=True)
    print ("result:", result)

    print ("\nEND:", time.strftime("%c"))