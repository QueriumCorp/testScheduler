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

def combContents(content):
    allText = ""
    if isinstance(content, dict) and "content" in content:
        allText += combContents(content["content"])
    elif isinstance(content, list):
        for part in content:
            allText += combContents(part)
    else:
        return content["text"] if content["type"]=="text" else ""

    return allText

def flattenValue(field, item, dfltValue=None):
    if item is None:
        return dfltValue
    if field == "Question Type":
        return item["value"] if "value" in item else dfltValue
    if field in [
        "LaTeX", "QSH1", "QSH2", "QSH3", "question stimumus", "EdX Specification"
    ]:
        if "content" not in item:
            return dfltValue

        return combContents(item)

    return item

def getFieldValue(field, item, dfltValue=None, flatten=False):
    customFields = [
        "MD5 Spec Hash", "UDB Update", "Math Class", "ID Number",
        "Mathematica Specification", "LaTeX", "QSH1", "QSH2", "QSH3",
        "Question Launch", "Source", "Question Type", "question stimumus",
        "description", "StepWise label", "Querium product ID",
        "EdX Specification"
    ]
    if field in customFields and "fields" in item:
        # print("getFieldValueV2 - 2")
        if fieldToCust(field) in item["fields"]:
            # print("getFieldValueV2 - 3")
            if flatten==True:
                return flattenValue(field, item["fields"][fieldToCust(field)])
            return item["fields"][fieldToCust(field)]
        else:
            return dfltValue

    # print("getFieldValueV2 - 4")
    if fieldToCust(field) in item:
        # print("getFieldValueV2 - 5")
        return item[fieldToCust(field)]

    return dfltValue

# flds: ["a", "b"]
# arr: [{"a": "one", "b": "two", "c":"three"}, {"a": "four", "b": "five"}]
def getFields(flds, arr, flatten=False):
    result = []
    for item in arr:
        itemResult = {}
        for f in flds:
            itemResult[f] = getFieldValue(f, item, flatten=flatten)

        result.append(itemResult)

    return result

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
#       - [flatten]: False means return without postprocessing the value
#   returns:
#       json
###############################################################################
def issueSearch(data, flatten=False):
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
        "maxResults": 100
    }
    if("fields" in data):
        payloadObj["fields"] = [fieldToCust(i) for i in data["fields"]]


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

        # If request fails, return the error code
        if response.status_code != 200:
            return response.status_code

        # Exiting the while loop conditions
        rsltPrt = json.loads(response.text)
        if "total" not in rsltPrt:
            gotEverythingQ = True
        if "startAt" not in rsltPrt:
            gotEverythingQ = True
        if "maxResults" not in rsltPrt:
            gotEverythingQ = True
        # If there are more data to retrieve increment the startAt value
        if (rsltPrt["startAt"]+rsltPrt["maxResults"]) < rsltPrt["total"]:
            payloadObj["startAt"] = rsltPrt["startAt"]+rsltPrt["maxResults"]
        else:
            gotEverythingQ = True

        if "issues" in rsltPrt:
            if("fields" in data):
                rsltAll.extend(getFields(data["fields"], rsltPrt["issues"],
                flatten=flatten))
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
        # "labels": ["CSULAWeek01"],
        "fields": [
            "key", "Question Type", "MD5 Spec Hash",
            "UDB Update", "Math Class", "ID Number",
            "Mathematica Specification", "LaTeX", "QSH1", "QSH2", "QSH3",
            "Question Launch", "Source", "question stimumus",
            "description", "StepWise label", "Querium product ID",
            "EdX Specification"
        ],
        # "fields": ["key", "Question Type", "MD5 Spec Hash"],
        # "fields": ["key"],
        "qstnType": "StepWise"
    }
    tmp = issueSearch(tmpData, flatten=True)
    printJson(tmp)
    print("total len: ", len(tmp))

    sys.exit(0)

    ## combContents
    tmp = {
        "content": [
            {
                "content": [
                    {
                        "text": "Solve  by any method.  (\\begin{array}{c}",
                        "type": "text"
                    },
                    {
                        "type": "hardBreak"
                    },
                    {
                        "text": "6x-8y=-0.6 ",
                        "type": "text"
                    }
                ],
                "type": "paragraph"
            },
            {
                "content": [
                    {
                        "text": "3x+2y=0.9",
                        "type": "text"
                    },
                    {
                        "type": "hardBreak"
                    },
                    {
                        "text": "\\end{array})",
                        "type": "text"
                    }
                ],
                "type": "paragraph"
            }
        ]
    }
    rslt = combContents(tmp)
    print(rslt)

    sys.exit()

    ##getFieldValueV2
    tmpField = "MD5 Spec Hash"
    # tmpField = "Question Type"
    tmp = getFieldValue(tmpField,
        {
            'expand': 'operations,versionedRepresentations,editmeta,changelog,renderedFields',
            'id': '47356',
            'self': 'https://querium.atlassian.net/rest/api/3/issue/47356',
            'key': 'QUES-12889',
            'fields': {
                'customfield_11300': '569b8f88d5a3e3021ea4ead6b243b91a',
                'customfield_11706': {
                    'self': 'https://querium.atlassian.net/rest/api/3/customFieldOption/10704',
                    'value': 'StepWise',
                    'id': '10704'
                }
            }
        })
    print (tmp)

    sys.exit()

    ## fieldToCust
    tmp = [fieldToCust(i) for i in ["key", "Question Type", "MD5 Spec Hash"]]
    print(tmp)
    sys.exit()

    ## getFields
    flds = ["a", "c"]
    arr = [{"a": "one", "b": "two", "c":"three"}, {"a": "four", "b": "five"}]
    print (getFields(flds, arr))

    sys.exit()

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