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
            logging.warning("Invalid filter {}".format(req['useFilter']))
            result = {
                "status": False,
                "result": "Invalid filter {}".format(req['useFilter'])
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
            "ref_id": -1,
            "priority": 1,
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
    sqlUpdate = "UPDATE {tbl} SET status='{stts}' WHERE id IN ({sqlPh})".format(tbl=tbl,stts=stts,sqlPh=sqlPh)
    logging.debug("mkQueryUpdate - query: {}".format(sqlUpdate))
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
    sql = "SELECT {sqlRtrn} FROM {tbl} WHERE {sqlCond}".format(sqlRtrn=sqlRtrn, tbl=tbl, sqlCond=sqlCond)

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
            "Changed the status from completed to pending: {}".format(len(completed)))

    ### Get the ones already in pending
    pending = list(filter(lambda x: x["status"]=="pending", onesInDb))
    logging.info(
            "Test paths that are already pending: {}".format(len(pending)))

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
# Add question paths to testPath
# Return:
# status: True/False
# result: a number of test paths in a question added in testPath
#######################################
def qstnToTestPath(info, settings):
    logging.info("Scheduling paths in {}".format(info['key']))
    ### Get question_id of a question unq
    qstnId = dbConn.getRow("question", ["unq"], [info["key"]], ["id"], fltr="")

    if qstnId is None or len(qstnId)<1:
        return {
            "status": False,
            "result": "{} was not found in UDB".format(info['key'])
        }
    if len(qstnId)>1:
        return {
            "status": False,
            "result": "Multiple rows have the same {info}: {qstnId}".format(info=info['key'], qstnId=qstnId)
        }

    ### Get paths in a question
    # print (settings["skipStatuses"])
    qstnId = qstnId[0]
    paths = dbConn.getPathsInQstn(
        qstnId[0],
        json.loads(settings["skipStatuses"]),
        ["id"]
    )
    logging.info("Number of paths in UDB: {}".format(len(paths)))
    if len(paths)<1:
        return {
            "status": True,
            "result": 0
        }

    ### If [paths] > limitPaths, sample the paths
    if "limitPaths" in settings and settings["limitPaths"]!=-1:
        if len(paths)>settings["limitPaths"]:
            logging.info("Sampled the paths to {}".format(settings['limitPaths']))
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
        logging.info("New test paths: {}".format(len(newPaths)))
        dbConn.addTestPaths(newPaths)
    else:
        logging.info("No new test paths to schedule")

    return {
        "status": True,
        "result": len(newPaths)
    }

#######################################
# Add questions to testPath
# Return:
# status: True/False
# result: a number of questions are added in testPath
#######################################
def qstnsToTestPath(qstns, settings):
    if len(qstns["keys"])<1:
        logging.info("No question to test")
        return {"status": True, "result": 0}

    logging.info ("Jira Questions: {}".format(len(qstns['keys'])))
    result = []
    for qstnInfo in qstns["keys"]:
        rsltQstn = qstnToTestPath(qstnInfo, settings)
        rsltQstn["unq"] = qstnInfo['key']
        result.append(rsltQstn)

    return result


###############################################################################
# Main logic
###############################################################################
def task(scheduleData):
    tbl = "testSchedule"

    ### Change the task's status to running and started time
    dbConn.modMultiVals(tbl, ["id"], [scheduleData["id"]],
        ["status", "started"], ["running", datetime.now()]
    )

    ### Search request
    req = json.loads(scheduleData["jira"])
    logging.debug("Jira request: {}".format(req))

    ### Jira respond of the request
    jiraData = jiraSearch(req)

    ### If jira request fails, update testSchdule
    if jiraData["status"]==False:
        dbConn.modMultiVals(
            tbl,
            ["id"], scheduleData["id"],
            ["status", "finished", "msg"],
            ["Failed", datetime.now(), jiraData["result"]])
        logging.info("Failed on jiraSearch: {}".format(jiraData['result']))
        return jiraData

    ### Update testSchedue with the jira result
    dbConn.modMultiVals(
        tbl,
        ["id"], [scheduleData["id"]],
        ["jiraResp"], [json.dumps(jiraData["keys"], separators=(',', ':'))])

    ### Create a new jiraFilter based on the given jql
    if "makeFilter" in req and "useFilter" not in req:
        fltrRslt = jiraFilter.mkFilter(req["makeFilter"], jiraData["jql"])
        if fltrRslt["status"]==False:
            dbConn.modMultiVals(
                tbl,
                ["id"], scheduleData["id"],
                ["status", "finished", "msg"],
                ["Failed", datetime.now(), fltrRslt["result"]])
            logging.info("Unable to create a Jira filter: {}".format(
                req['makeFilter']))
            return fltrRslt

    ### Add questions in testPath
    rsltQstns = qstnsToTestPath(jiraData, scheduleData)

    ### Report failed questions
    failedQstns = list(filter(lambda x: x["status"]==False, rsltQstns))
    if len(failedQstns)>0:
        logging.warning("Failed on adding questions: {}".format(failedQstns))
    dbConn.modMultiVals(
        tbl,
        ["id"], [scheduleData["id"]],
        ["status", "finished", "msg"],
        [
            "success" if len(failedQstns)==0 else "failedSome",
            datetime.now(),
            json.dumps(rsltQstns, separators=(',', ':'))
        ])