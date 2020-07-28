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
import jiraFilter
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
                "status": True,
                "filter": searchFilter["filter"],
                "keys": searchFilter["issueSearch"]["result"]
            }
        else:
            logging.warning(f"Invalid filter {req['useFilter']}")
            result = {
                "status": False,
                "result": f"Invalid filter {req['useFilter']}"
            }
    else:
        logging.info("Jira search is based on a jql")
        search = jql.issueSearch(req, flatten=True)
        if search["status"]:
            result = {
                "status": True,
                "keys": search["result"],
                "jql": search["jql"]
            }
        else:
            result = {
                "status": False,
                "result": search["result"]
            }

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
# Build a sql query for updating completed status to pending
#######################################
def mkQueryUpdate(tbl, idLen, stts="pending"):
    sqlPh = ",".join(["%s"]*idLen)
    sqlUpdate = f"UPDATE {tbl} SET status='{stts}' WHERE id IN ({sqlPh})"
    logging.debug(f"mkQueryUpdate - query: {sqlUpdate}")
    return sqlUpdate

#######################################
# Build dictionary of name and id
#######################################
def mkDict(dataA, dataB):
    rslt = {}
    for item in dataA:
        name = item["name"]
        if name in rslt:
            rslt[name].add(item["path_id"])
        else:
            rslt[name] = {item["path_id"]}

    for item in dataB:
        name = item["name"]
        if name in rslt:
            rslt[name].add(item["path_id"])
        else:
            rslt[name] = {item["path_id"]}

    return rslt

#######################################
# Handle test paths already in the testPath table.
# - Remove the test paths that are already in pending status
# - Change status to pending if they are in completed status and remove
#######################################
def rmExistingPaths(keysCond, data):
    tbl = "testPath"
    getFlds = ['id', 'name', 'path_id', 'status']

    ### Build a sql query for select
    sqlRtrn = ",".join(getFlds)
    sqlCond = (") OR (".join(["=%s AND ".join(keysCond)+"=%s"]*len(data)))
    sqlCond = "("+sqlCond+")"
    sql = f"SELECT {sqlRtrn} FROM {tbl} WHERE {sqlCond}"

    ### Make values to test
    sqlVals = [ i for row in data for i in [row[k] for k in keysCond] ]

    ### Get test paths that are already in testPath
    onesInDb = dbConn.fetchallQuery(sql, sqlVals, fldsRtrn=getFlds, mkObjQ=True)
    # print(onesInDb)
    # sys.exit()

    ### Filter the ones in completed
    completed = list(filter(lambda x: x["status"]=="completed", onesInDb))
    ### Update the status from completed to pending
    if len(completed)>0:
        idsComp = list(map(lambda x: x["id"], completed))
        dbConn.execQuery(mkQueryUpdate(tbl, len(idsComp)), idsComp)
        logging.info(
            f"Changed the status from completed to pending: {len(completed)}")

    ### Get the ones already in pending
    pending = list(filter(lambda x: x["status"]=="pending", onesInDb))
    logging.info(
            f"Test paths that are already pending: {len(pending)}")

    ### Remove the paths that are already in testPath because their status
    ### changed to pending
    rmPaths = mkDict(pending, completed)
    result = []
    for item in data:
        if item["name"] in rmPaths.keys():
            if item["path_id"] not in rmPaths[item["name"]]:
                result.append(item)
        else:
            result.append(item)

    return result

#######################################
# Add paths in a question to testPath
#######################################
def qstnToTestPath(info, settings):
    logging.info(f"Scheduling paths in {info['key']}")
    ### Get question_id of a question unq
    qstnId = dbConn.getRow("question", ["unq"], [info["key"]], ["id"])
    if qstnId is None or len(qstnId)<1:
        logging.warning(f"{info['key']} was not found in UDB")
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
    logging.info(f"Number of paths in UDB: {len(paths)}")

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

    ### Remove the test paths that are already in testPath
    condFlds = ['name', 'path_id']
    newPaths = rmExistingPaths(condFlds, pathSttngs)

    ### Add the test paths in the testPath table
    if len(newPaths)>0:
        logging.info(f"New test paths: {len(newPaths)}")
        dbConn.addTestPaths(newPaths)
    else:
        logging.info(f"No new test paths to schedule")

    return True

#######################################
# Add questions to testPath
#######################################
def qstnsToTestPath(qstns, settings):
    if len(qstns["keys"])<1:
        logging.info("No question to test")
        return {"status": True, "result": 0}

    logging.info (f"Jira Questions: {len(qstns['keys'])}")
    for qstnInfo in qstns["keys"]:
        qstnToTestPath(qstnInfo, settings)

###############################################################################
# Main logic
###############################################################################
def task(scheduleData):
    print("scheduleData")
    print(scheduleData)
    ### Search request
    req = json.loads(scheduleData["jira"])
    logging.debug(f"Jira request: {req}")

    ### Jira respond of the request
    jiraData = jiraSearch(req)
    # print("jiraData")
    # print(jiraData)
    if jiraData["status"]==False:
        dbConn.modMultiVals(
            "testSchedule",
            ["id"], scheduleData["id"],
            ["status", "msg"], ["Failed", jiraData["result"]])
        logging.info(f"Failed on jiraSearch: {jiraData['result']}")
        return jiraData

    ### Create a new jiraFilter based on the given jql
    if "makeFilter" in req and "useFilter" not in req:
        fltrRslt = jiraFilter.mkFilter(req["makeFilter"], jiraData["jql"])
        if fltrRslt["status"]==False:
            dbConn.modMultiVals(
                "testSchedule",
                ["id"], scheduleData["id"],
                ["status", "msg"], ["Failed", fltrRslt["result"]])
            logging.info(f"Unable to create a Jira filter: {req['makeFilter']}")
            return fltrRslt

    ### Add questions in testPath
    START HERE
    qstnsToTestPath(jiraData, scheduleData)