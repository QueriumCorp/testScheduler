###############################################################################
# schedule.py
# Handle scheduling a task
###############################################################################
import sys
import os
import json
import logging
import dbConn
import jql
import filter
from datetime import datetime
import random

###############################################################################
# Support functions
###############################################################################

#######################################
# Search Jira based on a JQL or a filter
#######################################
def jiraSearch(req):
    ### Search jira based on the req
    if "useFilter" in req:
        logging.info("Jira search is based on a filter")
        searchFilter = jql.searchByFilter(req, flatten=True)
        if len(searchFilter) > 0:
            result = {
                "filter": searchFilter["filter"],
                "keys": searchFilter["issueSearch"]["result"]
            }
        else:
            logging.warning(f"Invalid filter {req['useFilter']}")
    else:
        logging.info("Jira search is based on a jql")
        search = jql.issueSearch(req, flatten=True)
        result = {
            "keys": search["result"]
        }

    ### Create a new filter based on the given jql
    if "makeFilter" in req and "useFilter" not in req:
        filterStts = filter.mkFilter(req["makeFilter"], search["jql"])
        if filterStts["status"] == False:
            logging.warning(filterStts["result"])
        filterStts["name"] = req["makeFilter"]
        result["filter"] = filterStts

    return result

#######################################
# Make a name based on process ID and time
#######################################
def mkName():
    now = datetime.now()
    return str(os.getpid())+now.strftime("%Y%m%d%H%M%S")

#######################################
# Make default settings
#######################################
def defaultSettings(purpose, settings):
    if purpose=="testPath":
        result = {
            "name": mkName(),
            "question_id": -1,
            "path_id": -1,
            "trace_id": -1,
            "diff_id": -1,
            "author": "",
            "gradeStyle": "gradeBasicAlgebra",
            "policies": "$A1$",
            "status": "pending",
            "limitStepTime": 1800,
            "limitSteps": -1,
            "limitPathTime": 3600,
            "pid": -1,
            "stepCount": -1,
            "stepsCompleted": -1,
            "timeCompleted": -1,
            "host": "0.0.0.0",
            "gitBranch": "dev",
            "gitHash": "latest",
            "mmaVersion": "11.1",
            "timeOutTime": 60,
            "ruleMatchTimeOutTime": 120,
            "msg": "",
            "started": "1970-01-01 01:00:00",
            "finished": "1970-01-01 01:00:00"
        }

    for k in settings:
        result[k] = settings[k]

    return result


#######################################
# Add paths in a question to testPath
#######################################
def qstnToTestPath(info, settings):

    ### Get question_id of a question unq
    qstnId = dbConn.getRow("question", ["unq"], [info["key"]], ["id"])
    if len(qstnId)<1:
        logging.warning(f"{info['key']} is not found in UDB")
        return False
    if len(qstnId)>1:
        logging.warning(f"Multiple rows have the same {info['key']}: {qstnId}")
        return False

    ### Get paths in a question
    paths = dbConn.getPathsInQstn(
        qstnId[0],
        json.loads(settings["validStatus"]),
        ["id"]
    )
    logging.info(f"Number of paths in {info['key']}: {len(paths)}")

    ### If [paths] > limitPaths, sample the paths
    if "limitPaths" in settings and settings["limitPaths"]!=-1:
        if len(paths)>settings["limitPaths"]:
            logging.info(f"Sampled the paths to {settings['limitPaths']}")
            paths = random.sample(paths, settings["limitPaths"])

    ### Make dictionary of rows for the testPath table
    pathSttngs = []
    settings["question_id"] = qstnId[0]
    for pathId in paths:
        settings["path_id"] = pathId
        pathSttngs.append(defaultSettings("testPath", settings))

    ### Add the test paths in the testPath table
    dbConn.addTestPaths(pathSttngs)

    sys.exit()
    return True

#######################################
# Add questions to testPath
#######################################
def qstnsToTestPath(qstns, settings):
    print ("qstnsToTestPath", len(qstns["keys"]))
    if len(qstns["keys"])<1:
        logging.info("No question to test")
        return {"status": True, "result": 0}

    for qstnInfo in qstns["keys"]:
        qstnToTestPath(qstnInfo, settings)

###############################################################################
# Main logic
###############################################################################
def task(scheduleData):
    ### Search request
    req = json.loads(scheduleData["jira"])
    print (req)

    ### Jira respond of the request
    jiraData = jiraSearch(req)
    print(jiraData)

    ### Add questions in testPath
    qstnsToTestPath(jiraData, scheduleData)