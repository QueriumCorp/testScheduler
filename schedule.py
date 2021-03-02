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
import jira
from datetime import datetime
import random

###############################################################################
# Support functions
###############################################################################

#######################################
# Make a name based on process ID and time
#######################################
def mkName():
    now = datetime.now()
    return str(os.getpid())+now.strftime("%Y%m%d%H%M%S")

#######################################
# Make default settings
#######################################
def defaultSettings(purpose, settings, skip=[]):
    if purpose == "testPath":
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
            "limitPathTime": 600,
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
        if k not in skip:
            result[k] = settings[k]

    return result

#######################################
# Build a sql query for updating completed status to pending
#######################################
def mkQueryUpdate(tbl, idLen, stts="pending"):
    sqlPh = ",".join(["%s"]*idLen)
    sqlUpdate = "UPDATE {tbl} SET status='{stts}' WHERE id IN ({sqlPh})".format(
        tbl=tbl, stts=stts, sqlPh=sqlPh)
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

    # Build a sql query for select
    sqlRtrn = ",".join(getFlds)
    sqlCond = (") OR (".join(["=%s AND ".join(keysCond)+"=%s"]*len(data)))
    sqlCond = "("+sqlCond+")"
    sql = "SELECT {sqlRtrn} FROM {tbl} WHERE {sqlCond}".format(
        sqlRtrn=sqlRtrn, tbl=tbl, sqlCond=sqlCond)

    # Make values to test
    sqlVals = [i for row in data for i in [row[k] for k in keysCond]]

    # Get test paths that are already in testPath
    onesInDb = dbConn.fetchallQuery(
        sql, sqlVals, fldsRtrn=getFlds, mkObjQ=True)
    # print(onesInDb)
    # sys.exit()

    # Filter the ones in completed
    completed = list(filter(lambda x: x["status"] == "completed", onesInDb))
    # Update the status from completed to pending
    if len(completed) > 0:
        idsComp = list(map(lambda x: x["id"], completed))
        dbConn.execQuery(mkQueryUpdate(tbl, len(idsComp)), idsComp)
        logging.info(
            "Changed the status from completed to pending: {}".format(len(completed)))

    # Get the ones already in pending
    pending = list(filter(lambda x: x["status"] == "pending", onesInDb))
    logging.info(
        "Test paths that are already pending: {}".format(len(pending)))

    # Remove the paths that are already in testPath because their status
    # changed to pending
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
    # Get question_id of a question unq
    qstnId = dbConn.getRow("question", ["unq"], [info["key"]], ["id"], fltr="")

    if qstnId is None or len(qstnId) < 1:
        return {
            "status": False,
            "result": "{} was not found in UDB".format(info['key'])
        }
    if len(qstnId) > 1:
        return {
            "status": False,
            "result": "Multiple rows have the same {info}: {qstnId}".format(info=info['key'], qstnId=qstnId)
        }

    # Get paths in a question
    # print (settings["skipStatuses"])
    qstnId = qstnId[0]
    pathFlds = ["id", "priority"]
    paths = dbConn.getPathsInQstn(
        qstnId[0],
        json.loads(settings["skipStatuses"]),
        pathFlds,
        flat=False
    )
    logging.info("Number of paths in UDB: {}".format(len(paths)))
    if len(paths) < 1:
        return {
            "status": True,
            "result": 0
        }

    # If [paths] > limitPaths, sample the paths
    if "limitPaths" in settings and settings["limitPaths"] != -1:
        if len(paths) > settings["limitPaths"]:
            logging.info("Sampled the paths to {}".format(
                settings['limitPaths']))
            paths = random.sample(paths, settings["limitPaths"])

    # Make dictionary of rows for the testPath table
    skipFields = ["msg"]
    pathSttngs = []
    settings["question_id"] = qstnId[0]
    for path in paths:
        settings["path_id"] = path[0]
        # Inherit the priority field from path to testPath
        if "priority" in pathFlds:
            idx = pathFlds.index('priority')
            settings["priority"] = path[idx]

        pathSttngs.append(defaultSettings("testPath", settings, skipFields))

    # Remove the test paths that are already in testPath
    condFlds = ['name', 'path_id']
    newPaths = rmExistingPaths(condFlds, pathSttngs)

    # Add the test paths in the testPath table
    if len(newPaths) > 0:
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
    if len(qstns["keys"]) < 1:
        logging.info("No question to test")
        return {"status": True, "result": 0}

    logging.info("Question count: {}".format(len(qstns['keys'])))
    result = []
    testCnt = 1
    for qstnInfo in qstns["keys"]:
        if testCnt > 3:
            break
        testCnt += 1
        rsltQstn = qstnToTestPath(qstnInfo, settings)
        rsltQstn["unq"] = qstnInfo['key']
        result.append(rsltQstn)

    return result


###############################################################################
# Main logic
###############################################################################
def task(aTask):
    tbl = "testSchedule"

    # Add questions in testPath
    jiraRslt = jira.process(aTask)
    if jiraRslt["status"] == False:
        return jiraRslt

    # Add questions in testPath
    rsltQstns = qstnsToTestPath(jiraRslt, aTask)

    # Report failed questions
    failedQstns = list(filter(lambda x: x["status"] == False, rsltQstns))
    if len(failedQstns) > 0:
        logging.warning("Failed on adding questions: {}".format(failedQstns))

        dbConn.modMultiVals(
            tbl,
            ["id"], [aTask["id"]],
            ["status", "finished", "msg"],
            [
                "success" if len(failedQstns) == 0 else "failedSome",
                datetime.now(),
                json.dumps(rsltQstns, separators=(',', ':'))
            ])
        return {
            "status": False,
            "result": "Failed to add paths in questions: {msg}".format(
                msg=failedQstns
            )}

    return {
        "status": True,
        "result": "Completed successfully"}
