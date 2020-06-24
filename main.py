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

def jqLIssueSearch(data):
    jqlAll = "summary ~ \""+data["summary"]+"\""
    if "labels" in data:
        jqlLbls = "Labels=\"" + ("\" AND Labels=\"".join(data["labels"])+"\"")
        jqlAll += " AND "+jqlLbls
    if "qstnType" in data:
        jqlAll += " AND \"Question Type\"=\""+data["qstnType"]+"\""
    print("jqlAll:", jqlAll)

    return jqlAll

def buildJql(type, data):
    if (type == "issueSearch"):
        return ("/rest/api/3/search", jqLIssueSearch(data))
    if (type == "issue"):
        return ("/rest/api/3/issue/", data["issue"])

    print ("buildJql: invalid type")
    return False

def fieldToCust(field):
    switcher = {
        "MD5 Spec Hash" : "customfield_11300",
        "UDB Update" : "customfield_11301",
        "Math Class" : "customfield_11101",
        "ID Number" : "customfield_10900",
        "Mathematica Specification" : "customfield_10905",
        "LaTeX" : "customfield_10906",
        "QSH1" : "customfield_10907",
        "QSH2" : "customfield_10908",
        "QSH3" : "customfield_10909",
        "Question Launch" : "customfield_11007",
        "Source" : "customfield_11700",
        "Question Type" : "customfield_11706",
        "question stimumus" : "customfield_10904",
        "description" : "customfield_10910",
        "StepWise label" : "customfield_11000",
        "Querium product ID" : "customfield_11500",
        "EdX Specification" : "customfield_11709"
    }

    return switcher.get(field, field)

###############################################################################
#   Get a jira question
#   arguments:
#       - object with issue: jiraID: {"issue": "QUES-6019"}
#   returns:
#       json
###############################################################################
def getQuestion(data):
    route, jql = buildJql("issue", data)

    url = os.environ.get('companyUrl')+route+jql
    auth = HTTPBasicAuth(
        os.environ.get('jiraUser'),
        os.environ.get('api-token')
    )
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.request(
        "GET",
        url,
        headers=headers,
        auth=auth
    )

    if response.status_code != 200:
        return response.status_code

    return json.loads(response.text)

###############################################################################
#   Issue search
#   arguments:
#       - summary: "OSCAG"
#       - labels: ["label1", "label2"]
#   returns:
#       json
###############################################################################
def issueSearch(data):
    route, jql = buildJql("issueSearch", data)

    url = os.environ.get('companyUrl')+route
    auth = HTTPBasicAuth(
        os.environ.get('jiraUser'),
        os.environ.get('api-token')
    )
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payloadObj = {
        "jql": jql,
        "fieldsByKeys": False,
        "startAt": 0,
        "maxResults": 10
    }
    if("fields" in data):
        payloadObj["fields"] = data["fields"]

    gotEverythingQ = False
    rsltAll = []
    while not gotEverythingQ:
        payload = json.dumps( payloadObj )
        response = requests.request(
            "POST",
            url,
            data=payload,
            headers=headers,
            auth=auth
        )

        if response.status_code != 200:
            return response.status_code

        rsltPrt = json.loads(response.text)
        if "total" not in rsltPrt:
            gotEverythingQ = True
        if "startAt" not in rsltPrt:
            gotEverythingQ = True
        if "maxResults" not in rsltPrt:
            gotEverythingQ = True
        if (rsltPrt["startAt"]+rsltPrt["maxResults"]) < rsltPrt["total"]:
            payloadObj["startAt"] = rsltPrt["startAt"]+rsltPrt["maxResults"]
        else:
            gotEverythingQ = True

        print("maxResults:", rsltPrt["maxResults"])
        print("startAt:", rsltPrt["startAt"])
        print("total:", rsltPrt["total"])
        if "issues" in rsltPrt:
            # rsltAll.extend(rsltPrt["issues"])
            if("fields" in data):
                rsltAll.extend([
                    {k:issue[fieldToCust(k)] for k in data["fields"]}
                    for issue in rsltPrt["issues"]
                ])
            else:
                rsltAll.extend(rsltPrt["issues"])

    return rsltAll

###############################################################################
#   Testing
###############################################################################
def testing():
    print ("testing")

    ## issueSearch
    tmpData = {
        "summary": "OSCAGc07s01*",
        "labels": ["CSULAWeek01"],
        "fields": ["key", "Question Type", "MD5 Spec Hash"],
        # "fields": ["key", "Question Type", "MD5 Spec Hash"],
        # "fields": ["key"],
        "qstnType": "StepWise"
    }
    tmp = issueSearch(tmpData)
    printJson(tmp)
    print("total len: ", len(tmp))

    sys.exit(0)

    ## fieldToCust
    tmpField = "ID Number"
    print(tmpField, ":", fieldToCust(tmpField))
    tmpField = "Querium product ID"
    print(tmpField, ":", fieldToCust(tmpField))
    tmpField = "rand"
    print(tmpField, ":", fieldToCust(tmpField))
    sys.exit(0)

    ## test: buildJql
    tmpData = {
        "summary": "OSCAGc07s01*",
        "labels": ["CSULAWeek01"],
        "qstnType": "StepWise",
        "filds": ["key", "summary", "labels", "Question Type"]
    }
    print (buildJql("issueSearch", tmpData))
    print (buildJql("xxx", {"a": "one", "b": "two"}))
    sys.exit(0)


    ## get a jira question
    tmp = getQuestion({"issue": "QUES-6019"})
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