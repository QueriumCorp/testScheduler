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
#   Issue search
#   arguments:
#       - summary: "OSCAG"
#       - labels: ["label1", "label2"]
#   returns:
#       json
###############################################################################
def issueSearch(summ, labels=[], qstnType="StepWise"):
    jqlSumm = "summary ~ \""+summ+"\""
    jqlLbls = "Labels=\"" + ("\" AND Labels=\"".join(labels)+"\"")
    jqlAll = jqlSumm
    if len(labels)>0:
        jqlAll += " AND "+jqlLbls
    if len(qstnType)>0:
        jqlAll += " AND \"Question Type\"=\""+qstnType+"\""
    print("jqlAll:", jqlAll)
    # sys.exit()

    url = os.environ.get('companyUrl')+"/rest/api/3/search"
    auth = HTTPBasicAuth(
        os.environ.get('jiraUser'),
        os.environ.get('api-token')
    )

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = json.dumps( {
        "jql": jqlAll,
        "maxResults": 15,
        "fieldsByKeys": False,
        "fields": [
            "key"
            "summary",
            "labels",
            "Question Type"
        ],
        "startAt": 0
    } )

    response = requests.request(
        "POST",
        url,
        data=payload,
        headers=headers,
        auth=auth
    )

    return json.loads(response.text)

###############################################################################
#   Testing
###############################################################################
def testing():
    print ("testing")

    ## issueSearch
    tmp = issueSearch("OSCAGc07s01*", ["CSULAWeek01"])
    printJson(tmp)

    sys.exit(0)


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