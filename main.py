###############################################################################
# xxx

# Requirements
# Python >= 3.4
# Git 1.7.0 or newer

# Need the following modules
# python3 -m pip install python-dotenv
# python3 -m pip install requests

###############################################################################
import time
import os
import sys
from dotenv import load_dotenv
load_dotenv()
import requests
from requests.auth import HTTPBasicAuth
import json


###############################################################################
#   Support functions
###############################################################################
def printJson(data):
    print(json.dumps(data, sort_keys=True, indent=4, separators=(",", ": ")))

###############################################################################
#   Get a jira question
#   arguments:
#       - jira ID: "QUES-6019"
#   returns:
#       json
###############################################################################
def getQuestion(jiraId):
    url = os.environ.get('companyUrl')+"/rest/api/3/issue/"+jiraId
    auth = HTTPBasicAuth(
        os.environ.get('jiraUser'),
        os.environ.get('api-token')
    )

    headers = {
        "Accept": "application/json"
    }

    response = requests.request(
        "GET",
        url,
        headers=headers,
        auth=auth
    )

    return json.loads(response.text)

###############################################################################
#   Testing
###############################################################################
def testing():
    print ("testing")

    ## get a jira question
    tmp = getQuestion("QUES-6019")
    printJson(tmp)

    sys.exit(0)

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