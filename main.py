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
# or
# python3 main.py '{"makeFilter": "aNewFilterName", "jql": "project = QUES AND Labels = CSULAWeek01 AND Labels != NotRoverReady AND Labels != HasStepWiseVariants AND \"Mathematica Specification\" !~ MatchSpec", "fields":["key"]}'
# or
# python3 main.py '{"useFilter": "filterTest1", "fields":["key"]}'
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

    ### testing code
    # test.mkFilter()
    # sys.exit()

    ### Get request input
    req = input.getRequest()
    # print("req:", req)
    # sys.exit()

    ### Search jira based on the req
    if "useFilter" in req:
        searchFilter = jql.searchByFilter(req, flatten=True)
        if len(searchFilter) < 1:
            print(searchFilter)
            sys.exit()
        result = {
            "filter": searchFilter["filter"],
            "keys": searchFilter["issueSearch"]["result"]
        }
    else:
        search = jql.issueSearch(req, flatten=True)
        result = {
            "keys": search["result"]
        }

    ### Create a new filter based on the given jql
    if "makeFilter" in req and "useFilter" not in req:
        filterStts = filter.mkFilter(req["makeFilter"], search["jql"])
        filterStts["name"] = req["makeFilter"]
        result["filter"] = filterStts

    ### Dump result as a json
    # jql.printJson(result)
    print (json.dumps(result))