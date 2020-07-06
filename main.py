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
    # test.mkFilter()
    # sys.exit()

    ### Get request input
    req = input.getRequest()

    ### Search jira based on the req
    search = jql.issueSearch(req, flatten=True)
    result = {
        "keys": search["result"]
    }

    ### Export a filter based on a search jql
    if "makeFilter" in req:
        filterStts = filter.mkFilter(req["makeFilter"], search["jql"])
        result["filter"] = filterStts

    ### Dump result as a json
    # jql.printJson(result)
    print (json.dumps(result))

    # print ("\nEND:", time.strftime("%c"))