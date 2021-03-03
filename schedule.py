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
import task as taskModule

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
            "Changed the status from completed to pending: {}".format(
                len(completed)))

    # Get the ones already in pending
    pending = list(filter(lambda x: x["status"] == "pending", onesInDb))
    logging.info(
        "Already pending: {}".format(
            len(pending)))

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
# mk test paths
#######################################
def mkTestPath(settings, qstnId, paths):
    pathFlds = ["id", "priority"]

    if len(paths) < 1:
        return {
            "status": True,
            "result": 0
        }

    testPaths = paths
    # If [paths] > limitPaths, sample the paths
    if "limitPaths" in settings and settings["limitPaths"] != -1:
        if len(paths) > settings["limitPaths"]:
            logging.info("Sampled the paths to {}".format(
                settings['limitPaths']))
            testPaths = random.sample(paths, settings["limitPaths"])

    # Make dictionary of rows for the testPath table
    skipFields = ["msg"]
    pathSttngs = []
    settings["question_id"] = qstnId
    for path in testPaths:
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
        logging.info("Added paths: {}".format(len(newPaths)))
        dbConn.addTestPaths(newPaths)
    else:
        logging.info("No paths to schedule")

    return {
        "status": True,
        "result": len(newPaths)
    }

#######################################
# Add question paths to testPath
# Return:
# status: True/False
# result: a number of test paths in a question added in testPath
#######################################
def qstnToTestPath(settings, unq):
    logging.info("Scheduling paths in {}".format(unq))
    # Get question_id of a question unq
    qstnData = dbConn.getRow("question", ["unq"], [unq], ["id"], fltr="")

    if qstnData is None or len(qstnData) < 1:
        return {
            "status": False,
            "result": "Invalid unq"
        }
    elif len(qstnData) > 1:
        return {
            "status": False,
            "result": "Multiple questions have the same unq"
        }

    # Get paths in a question
    qstnId = qstnData[0][0]
    pathFlds = ["id", "priority"]
    paths = dbConn.getPathsInQstn(
        qstnId,
        settings["skipStatuses"],
        pathFlds,
        flat=False
    )
    logging.info("Total number of paths: {}".format(len(paths)))

    return mkTestPath(settings, qstnId, paths)

#######################################
# Add questions to testPath
# Return:
# status: True/False
# result: a number of questions are added in testPath
#######################################
def qstnsToTestPath(settings, qstns):
    if len(qstns) < 1:
        logging.info("No question to test")
        return {"status": True, "result": 0}

    logging.info("Question count: {}".format(len(qstns)))
    result = []
    testCnt = 1
    for qstnUnq in qstns:
        if testCnt > 4:
            break
        testCnt += 1
        rsltQstn = qstnToTestPath(settings, qstnUnq)
        rsltQstn["unq"] = qstnUnq
        result.append(rsltQstn)

    return result


#######################################
# Identify the schedule reqType
# Returns: a string of a schedule reqType
#######################################
def getScheduleType(req):
    if "useFilter" in req or "jql" in req:
        return "jira"
    elif "questions" in req:
        return "question"
    elif "paths" in req:
        return "path"
    else:
        return "invalid"

#######################################
# Handle when schedule reqType is jira
#######################################
def handleJira(aTask):
    data = jira.process(aTask)
    rslt = []
    if data["status"] == True:
        rslt = list(map(lambda x: x["key"], data["keys"]))
        return {
            "status": True,
            "result": rslt
        }

    return rslt

#######################################
# Handle when schedule reqType is question
#######################################
def handleQuestion(aTask):
    rslt = []
    if "questions" in aTask["jira"] and len(aTask["jira"]["questions"])>0:
        rsltTmp = aTask["jira"]["questions"]
        rslt = list(filter(lambda x: "QUES-" in x, rsltTmp))
        if len(rslt) != len(rsltTmp):
            logging.warning("Invalid questions: {}".format(
                set(rsltTmp) - set(rslt)
            ))

    return {
        "status": True,
        "result": rslt
    }


#######################################
# Handle when schedule reqType is path
#######################################
def handlePath(aTask):
    rslt = []
    if "paths" in aTask["jira"] and len(aTask["jira"]["paths"])>0:
        rslt = aTask["jira"]["paths"]

    return {
        "status": True,
        "result": rslt
    }

#######################################
# Handle when schedule reqType is invalid
#######################################
def handleInvalid(aTask):
    msg = "Invalid jira field in Task {}".format(aTask["id"])
    logging.error(msg)
    return {
        "status": False,
        "result": msg
    }

#######################################
# Get questions in a schedule request
# Return: a list of ques IDs: ["QUES-1234", "QUES-1235", etc]
#######################################
def processReq(aTask):
    reqType = getScheduleType(aTask["jira"])

    handlers = {
        "jira": handleJira,
        "question": handleQuestion,
        "path": handlePath,
        "invalid": handleInvalid
    }
    rslt = handlers[reqType](aTask)

    # If status is fasle, update the status in testSchedule
    if rslt["status"] == False:
        taskModule.modStts(aTask["id"], "fail",
            ["finished", "msg"],
            [datetime.utcnow(), rslt["result"]]
        )
        return {
            "reqType": reqType,
            "result": []
        }

    return {
        "reqType": reqType,
        "result": rslt["result"]
    }

#######################################
# Summarize the result
#######################################
def summarizeQstn(tbl, aTask, data):
    successQstns = list(filter(lambda x: x["status"] == True, data))
    successUnqs = list(map(lambda x: x["unq"], successQstns))
    logging.info("Questions scheduled: {}".format(len(successUnqs)))

    failedQstns = list(filter(lambda x: x["status"] == False, data))
    if len(failedQstns) > 0:
        logging.warning("Questions failed: {}".format(len(failedQstns)))
        failedUnqs = []
        for i in failedQstns:
            failedUnqs.append(i["unq"])
            logging.warning("{unq} failed: {msg}".format(
                unq=i["unq"], msg=i["result"]))

        dbConn.modMultiVals(
            tbl,
            ["id"], [aTask["id"]],
            ["status", "finished", "msg"],
            [
                "success" if len(failedQstns) == 0 else "failSome",
                datetime.utcnow(),
                json.dumps(
                    {
                        "success": successQstns,
                        "fail": failedQstns
                    },
                    separators=(',', ':'))
            ])


###############################################################################
# Main logic
###############################################################################
def task(aTask):
    tbl = "testSchedule"

    # Add questions in testPath
    rsltReq = processReq(aTask)

    # Add questions in testPath
    if rsltReq["reqType"] == "jira" or rsltReq["reqType"] == "question":
        rsltJira = qstnsToTestPath(aTask, rsltReq["result"])
        summarizeQstn(tbl, aTask, rsltJira)
