###############################################################################
# jql.py
# Jira API module

# Requirements
# Python >= 3.4
# Git 1.7.0 or newer

# Need the following modules
# python3 -m pip install python-dotenv
# python3 -m pip install requests

###############################################################################
import os
import sys
from dotenv import load_dotenv
load_dotenv()
import requests
from requests.auth import HTTPBasicAuth
import json
from urllib.parse import quote
import logging

###############################################################################
#   Support functions
###############################################################################
def printJson(data):
    print(json.dumps(data, sort_keys=True, indent=4, separators=(",", ": ")))

def jqlIssueSearch(data):
    ## if data contains jql, return its value. It is a jira query
    if "jql" in data:
        return data["jql"]

    ## make sure summary and labels fields in the data
    assert "summary" in data
    assert "labels" in data

    jqlAll = "summary ~ \""+data["summary"]+"\""
    if "labels" in data:
        jqlLbls = "Labels=\"" + ("\" AND Labels=\"".join(data["labels"])+"\"")
        jqlAll += " AND "+jqlLbls
    if "qstnType" in data:
        jqlAll += " AND \"Question Type\"=\""+data["qstnType"]+"\""
    # print("jqlAll:", jqlAll)

    return jqlAll

def buildJql(type, data):
    if (type == "issueSearch"):
        return ("/rest/api/3/search", jqlIssueSearch(data))
    if (type == "issue"):
        return ("/rest/api/3/issue/", data["issue"])
    if (type == "filterSearch"):
        return ("/rest/api/3/filter/search", "")
    if (type == "filterNameSearch"):
        return ("/rest/api/3/filter/search?filterName="+quote(data), "")
    if (type == "createFilter"):
        return ("/rest/api/3/filter", "")

    logging.warning (f"buildJql: invalid type {type}")
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

#######################################
#   Get a jira filter by name
#   Parameter:
#   - object with issue: jiraID: {"issue": "QUES-6019"}
#   returns:
#   -
#######################################
def getJiraFilter(route):
    url = os.environ.get('companyUrl')+route
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
    filter = json.loads(response.text)
    if len(filter["values"]) == 0:
        return {"status": False, "result": "invalid filter"}
    if len(filter["values"]) > 1:
        return {"status": False, "result": "multiple filters were found"}

    return {
        "status": True,
        "result": filter["values"][0]
    }

#######################################
#   Get a jira filter by name
#   Parameter:
#   - object with issue: jiraID: {"issue": "QUES-6019"}
#   returns:
#   -
#######################################
def getJiraFilterByUrl(url):
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
    filter = json.loads(response.text)
    # print("filter:", filter)

    if "errorMessages" in filter or "errors" in filter:
        return {"status": False, "result": "invalid url"}

    return {
        "status": True,
        "jql": filter["jql"],
        "searchUrl": filter["searchUrl"],
        "id": filter["id"],
        "name": filter["name"]
    }

#######################################
#  Get a json file
#######################################
def fileToJson(file):
    with open(file) as json_file:
        data = json.load(json_file)

    return data

#######################################
#  Save data into a json file
#######################################
def jsonToFile(file, data):
    with open(file, 'w') as outfile:
        json.dump(data, outfile)

#######################################
#  Get only key fields
#######################################
def getFld(fld, data):
    rslt = map(lambda x: x[fld], data["result"])
    return list(rslt)


###############################################################################
#   Get a jira question
#   Parameter:
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
#   parameters:
#   - data: is a dictionary of jql or (summar and labels) and fields to return
#   jql: {"jql": "project = QUES AND Labels = CSULAWeek01", "fields":["key"]}
#   (summar and labels): {"summary": "OSCAGc07s01*", labels: ["CSULAWeek01"], "fields":["key"]}
#   - [flatten]: False means return without postprocessing the value
#   example: {"jql": "project = QUES AND Labels = CSULAWeek01 AND Labels != NotRoverReady AND Labels != HasStepWiseVariants AND \"Mathematica Specification\" !~ MatchSpec", "fields":["key"]}
#   returns:
#   If the return field is key and result is flattend, the function returns
#   [{"key": "QUES-XXX1"}, {"key": "QUES-XXX2"}, ...]
###############################################################################
def issueSearch(data, flatten=False):
    route, jql = buildJql("issueSearch", data)
    result = {
        "jql": jql
    }

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
    jqlRslt = []
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
            return {"status": False, "result": response.status_code}

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
                jqlRslt.extend(getFields(data["fields"], rsltPrt["issues"],
                flatten=flatten))
            else:
                jqlRslt.extend(rsltPrt["issues"])
    result["status"] = True
    result["result"] = jqlRslt

    return result

###############################################################################
#   searchByFilter
#   parameters:
#   arg: {"useFilter": "anExistingFilterName", "fields":["key"]}'
#   - useFilter: make sure the filter exists in Jira
#   - fields: jira fields to be returned
#   returns:
#   The function returns filter information and issueSearch
###############################################################################
def searchByFilter(arg, flatten=False):
    route, _ = buildJql("filterNameSearch", arg["useFilter"])
    filterMeta1 = getJiraFilter(route)
    ## If invalid filter
    if not filterMeta1["status"]:
        return {}
    filterMeta2 = getJiraFilterByUrl(filterMeta1["result"]["self"])
    ## If searchURL fails
    if not filterMeta2["status"]:
        return {}

    arg["jql"] = filterMeta2["jql"]
    return {
        "filter": {
            "name": filterMeta2["name"],
            "result": filterMeta2["id"],
            "status": filterMeta2["status"]
        },
        "issueSearch": issueSearch(arg, flatten)
    }

if __name__ == '__main__':
    if len(sys.argv)<2:
        print("Provide full path to a json:")
        print("python3 jql.py /path/to/file.json")
        sys.exit(1)

    ## Get filter argument
    data = fileToJson(sys.argv[1])

    ## Get the filter result from Jira
    jqlRslt = issueSearch(data, True)
    if jqlRslt["status"]!=True:
        print("Unable to run \"jql\" in", sys.argv[1])
        sys.exit()

    ## Delete the result file if it already exists
    if os.path.exists(data["fileOut"]):
        os.remove(data["fileOut"])

    ## Extract only keys from the result
    result = getFld("key", jqlRslt)
    jsonToFile(data["fileOut"], result)

    ## Write the result in the output file
    if os.path.exists(data["fileOut"]):
        print("result is in", data["fileOut"])
    else:
        print("unable to create:", data["fileOut"])