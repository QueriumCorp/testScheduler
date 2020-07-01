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
# python3 main.py '{"summary":"OSCAGc07s01*", "labels": ["CSULAWeek01"], "qstnType":"StepWise", "fields":["key"]}'
# or
# python3 main.py '{"jql": "project = QUES AND Labels = CSULAWeek01 AND Labels != NotRoverReady AND Labels != HasStepWiseVariants AND \"Mathematica Specification\" !~ MatchSpec", "fields":["key"]}'

###############################################################################
import time
import input
import jql
import filter
import test
import sys
import json


###############################################################################
#   Main
###############################################################################
if __name__ == '__main__':
    # print ("\nSTART:", time.strftime("%c"))

    ### testing code
    test.filterExistsQ()
    sys.exit()

    ### Get request input
    req = input.getRequest()
    # print ("input:", req)

    ### Search jira based on the req
    result = jql.issueSearch(req, flatten=True)
    # print ("result:", result)

    ### Export a filter based on a search jql
    if "makeFilter" in req:
        filter.mkFilter(req.makeFilter, result.jql)

    ### Dump result as a json
    print (json.dumps(result["result"]))

    # print ("\nEND:", time.strftime("%c"))