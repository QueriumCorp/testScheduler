###############################################################################
# filter.py
# Jira API module

# Requirements
# Python >= 3.4
# Git 1.7.0 or newer

# Need the following modules
# python3 -m pip install python-dotenv
# python3 -m pip install requests

###############################################################################
from dotenv import load_dotenv
load_dotenv()
import requests
from requests.auth import HTTPBasicAuth
import os
import json
import jql
import util
from urllib.parse import urlencode

###############################################################################
#   Support functions
###############################################################################

#######################################
#   Does filter already exists
#   parameters:
#       - name: name of a new filter
#       - jql: Jira Query Language
#######################################
def filterExistsQ(name):
    route, _ = jql.buildJql("filterNameSearch", name)
    urlRoot = os.environ.get('companyUrl')+route
    auth = HTTPBasicAuth(
        os.environ.get('jiraUser'),
        os.environ.get('api-token')
    )
    headers = {
    "Accept": "application/json"
    }

    urlNext = urlRoot
    terminateQ = False
    while not terminateQ:
        response = requests.request(
            "GET",
            urlNext,
            headers=headers,
            auth=auth
        )
        # If request fails, return the error code. Need a better way to handle?
        if response.status_code != 200:
            # return {"status": False, "result": response.status_code}
            return True

        rsltPart = json.loads(response.text)
        for val in rsltPart["values"]:
            if val["name"] == name:
                return True

        nextPage = util.nextPageQ(rsltPart)
        terminateQ = nextPage["isLast"]
        urlNext = urlRoot+"&"+urlencode({"startAt": nextPage["startAt"]})

    return False


###############################################################################
#   Main logic
###############################################################################

#######################################
#   mkFilter
#   parameters:
#       - name: name of a new filter
#       - jql: Jira Query Language
#######################################
def mkFilter(name, jql):
    print ("mkFilter")
    ## check the filter name already exists in Jira
    if len(filterExistsQ(name)):
        return {
            "status": False,
            "result": "already exists"
        }

    START HERE
