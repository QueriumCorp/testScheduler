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
    switcher = {
        "testPath": {
            "schedule_id": None,
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
            "mmaVersion": "11.2",
            "timeOutTime": 60,
            "ruleMatchTimeOutTime": 120,
            "msg": "",
            "started": "1970-01-01 01:00:00",
            "finished": "1970-01-01 01:00:00"
        },
        "testSchedule": {
            "name": "",
            "jira": "",
            "author": "maria@querium.com",
            "gradeStyle": "gradeBasicAlgebra",
            "policies": "$A1$",
            "skipStatuses": ["invalid"],
            "status": "pending",
            "limitPaths": -1,
            "limitPathTime": 3600,
            "host": "0.0.0.0",
            "pid": -1,
            "gitBranch": "dev",
            "gitHash": "latest",
            "mmaVersion": "11.2",
            "timeOutTime": 60,
            "msg": "",
            "jiraResp": "",
            "rrule": "",
            "started": "1970-01-01 01:00:00",
            "finished": "1970-01-01 01:00:00"
        }
    }
    result = switcher.get(purpose, {})

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
# Remove path IDs that are already exists in the testPath table.
#######################################
def getNewPaths(scheduleId, pathIds):
    pathIdsInData = set(pathIds)

    # Get all path IDs of the schedule ID in the testPath table
    pathIdsInDb = dbConn.pathsInSchedule(scheduleId)

    newPathIds = pathIdsInData.difference(pathIdsInDb)
    return list(newPathIds)


#######################################
# mk test paths
#######################################
def mkTestPath(aTask, data):
    tbl = "testPath"
    skipFields = ["status","msg","started","finished","created","updated"]

    if len(data) < 1:
        return {
            "status": True,
            "result": 0
        }

    # Make dictionary of rows for the testPath table
    dbData = []
    for pathInfo in data:
        pathRow = defaultSettings(tbl, aTask, skipFields)
        pathRow["schedule_id"] = aTask["id"]
        for k in pathInfo:
            if k in pathRow:
                pathRow[k] = pathInfo[k]
        dbData.append(pathRow)

    # Add the test paths in the testPath table
    if len(dbData) > 0:
        dbConn.addTestPaths(dbData)
        logging.info("Added paths: {}".format(len(dbData)))
    else:
        logging.info("No paths were added")

    return {
        "status": True,
        "result": len(dbData)
    }

#######################################
#
#######################################
def allignQstnPath(keys, data):
    pathToQstn = {}
    pathsHaveExtra = set()
    for i in data:
        if i[1] in pathToQstn:
            tmp = pathToQstn[i[1]]
            tmp.append(i[0])
            pathToQstn[i[1]] = tmp
            pathsHaveExtra.add(i[1])
        else:
            pathToQstn[i[1]] = [i[0]]

    missingPaths = set(keys).difference(set(pathToQstn.keys()))
    extras = {}
    # for i in pathsHaveExtra:
    #     extras[i] = pathToQstn[i]

    cleanData = {}
    for i in pathToQstn:
        if i not in pathsHaveExtra:
            cleanData[i] = pathToQstn[i][0]
            # cleanData.append(tuple([pathToQstn[i][0], i]))
        else:
            extras[i] = pathToQstn[i]

    return {
        "missingPaths": list(missingPaths),
        "multiQstnPaths": extras,
        "pathToQstn": cleanData
    }

#######################################
#
#######################################
def getPathInfo(flds, skips, pathIds):
    restFlds = list(filter(lambda x: x != "id", flds))
    try:
        idxId = flds.index("id")
    except ValueError:
        logging.error ("getPathInfo: missing the id element")
        return []
    else:
        pathsDb = dbConn.getPaths(
                flds,
                pathIds,
                skipStatus=skips
            )

        pathIdsDb = list(map(lambda x: x[idxId], pathsDb))
        if (len(pathIdsDb) < len(pathIds)):
            pathIdsDb = list(map(lambda x: x[idxId], pathsDb))
            logging.warning("Path IDs weren't found in " + \
                "the path table: {}".format(
                    set(pathIds).difference(set(pathIdsDb))))

        qstnIdPathId = dbConn.getQstnIds(pathIdsDb)
        rsltClean = allignQstnPath(pathIdsDb, qstnIdPathId)

        # Log any paths that have multiple questions links in question_path
        if len(list(rsltClean["multiQstnPaths"].keys()))>0:
            logging.warning("Path linked to multiple questions in " + \
                "question_path: {}".format(
                    list(rsltClean["multiQstnPaths"].keys())))

        # Log any paths that aren't linked to any question in question_path
        if len(rsltClean["missingPaths"])>0:
            logging.warning("Path weren't found in question_path: {}".format(
                rsltClean["missingPaths"]
            ))

        # Build dictionary of path_id and its info
        cleanPaths = list(rsltClean["pathToQstn"].keys())
        rslt = []
        for i in pathsDb:
            if i[idxId] in cleanPaths:
                rslt.append(dbConn.mkObj(
                    ["question_id", "path_id"] + restFlds,
                    (rsltClean["pathToQstn"][i[idxId]],) + i
                ))
                # rslt.append((rsltClean["pathToQstn"][i[idxId]],) + i)

        return rslt

#######################################
# Preprocess
#######################################
def mkPathInput(aTask):
    pathFlds = ["id", "priority"]
    restFlds = list(filter(lambda x: x != "id", pathFlds))
    idxId = 0
    reqType = getScheduleType(aTask["jira"])
    rslt = []

    if reqType == "jira" or reqType == "question":
        paths = dbConn.getPathsInQstn(
            aTask["question_id"],
            aTask["skipStatuses"],
            pathFlds,
            flat=False
        )
        for i in paths:
            rslt.append(
                dbConn.mkObj(
                    ["question_id", "path_id"] + restFlds,
                    (aTask["question_id"],) + i
                )
            )
    elif reqType == "path":
        rslt = getPathInfo(
            pathFlds, aTask["skipStatuses"],aTask["jira"]["paths"])

    return rslt


#######################################
# Add question paths to testPath
# Return:
# status: True/False
# result: a number of test paths in a question added in testPath
#######################################
def qstnToTestPath(aTask, unq):
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
    newTask = aTask
    newTask["question_id"] = qstnId

    rslt = pathsToTestPath(newTask)
    return rslt


#######################################
# Add questions in testPath
# Return:
# status: True/False
# result: a number of questions are added in testPath
#######################################
def qstnsToTestPath(aTask, qstns):
    result = []
    if len(qstns) < 1:
        logging.info("No question to test")
        return result
    logging.info("Question count: {}".format(len(qstns)))

    for qstnUnq in qstns:
        rsltQstn = qstnToTestPath(aTask, qstnUnq)
        if rsltQstn["status"] == False:
            logging.warning("Failed: {}".format(rsltQstn["result"]))
        rsltQstn["unq"] = qstnUnq
        result.append(rsltQstn)

    return result

#######################################
# Sample the paths
#######################################
def sampleQ(aTask, pathCount):
    if "limitPaths" not in aTask:
        return False

    if aTask["limitPaths"] == -1:
        return False

    reqType = getScheduleType(aTask["jira"])
    if reqType == "path":
        return False

    if pathCount > aTask["limitPaths"]:
        return True

    return False

#######################################
# Add paths in testPath
#######################################
def pathsToTestPath(aTask):

    # Create a list of {question_id, path_id, priority} for each path
    pathInfo = mkPathInput(aTask)
    logging.debug("pathsToTestPath-pathInfo: {}".format(pathInfo))

    # Remove any path_id(s) that are already in testPath under task["name"]
    allPaths = list(map(lambda x: x["path_id"], pathInfo))
    newPaths = getNewPaths(aTask["id"], allPaths)
    newInfo = list(filter(lambda x: x["path_id"] in newPaths, pathInfo))

    # Sample the paths for scheduling based on jira and questions
    oldCnt = len(newInfo)
    if sampleQ(aTask, oldCnt):
        newInfo = random.sample(newInfo, aTask["limitPaths"])
        logging.info("Sampled the paths from {oldCnt} to {newCnt}".format(
                oldCnt=oldCnt, newCnt=aTask["limitPaths"]))

    # Add the new paths in testPath
    rslt = mkTestPath(aTask, newInfo)
    return rslt

#######################################
# Create test paths based on scheduleId
#######################################
def scheduleToTestPath(aTask, pathInfo):

    # Remove any path_id(s) that are already in testPath under task["name"]
    allPaths = list(map(lambda x: x["path_id"], pathInfo))
    newPaths = getNewPaths(aTask["id"], allPaths)
    logging.debug("Paths had already added: {}".format(
        len(allPaths)-len(newPaths)))
    newInfo = list(filter(lambda x: x["path_id"] in newPaths, pathInfo))

    # Create the test paths in testPath
    rslt = mkTestPath(aTask, newInfo)

    return rslt


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
    elif "useScheduleId" in req:
        return "schedule"
    else:
        return "invalid"

#######################################
# Handle when schedule reqType is jira
#######################################
def handleJira(aTask):
    data = jira.process(aTask)

    # If jira.process fails, return
    if data["status"] == False:
        return data

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
    if "questions" not in aTask["jira"]:
        return {
            "status": False,
            "result": "Invalid request: {}".format(aTask["jira"])
        }

    rslt = aTask["jira"]["questions"]
    return {
        "status": True,
        "result": rslt
    }


#######################################
# Handle when schedule reqType is path
#######################################
def handlePath(aTask):
    rslt = []
    if "paths" in aTask["jira"] and len(aTask["jira"]["paths"]) > 0:
        rslt = aTask["jira"]["paths"]

    return {
        "status": True,
        "result": rslt
    }

#######################################
# Handle when schedule reqType is schedule ID
#######################################
def handleSchedule(aTask):

    if "useScheduleId" not in aTask["jira"]:
        return {
            "status": False,
            "result": "Invalid jira field"
        }

    if type(aTask["jira"]["useScheduleId"]) != int:
        return {
            "status": False,
            "result": "Invalid schedule ID"
        }

    # Get test paths of the task
    rslt = dbConn.getRow(
        "testPath",
        ["schedule_id"],
        [aTask["jira"]["useScheduleId"]],
        ["question_id", "path_id", "priority"],
        fltr="", mkObjQ=True
    )

    return {
        "status": True,
        "result": rslt
    }

#######################################
# Handle when schedule reqType is invalid
#######################################
def handleInvalid(aTask):
    msg = "Invalid jira field"
    return {
        "status": False,
        "result": msg
    }

#######################################
# Get questions in a schedule request
# Return:
#  - a list of ques IDs: ["QUES-1234", "QUES-1235", etc]
#  - a list of path IDs if reqType is path
#######################################
def processReq(aTask):
    reqType = getScheduleType(aTask["jira"])

    handlers = {
        "jira": handleJira,
        "question": handleQuestion,
        "path": handlePath,
        "schedule": handleSchedule,
        "invalid": handleInvalid
    }
    rslt = handlers[reqType](aTask)

    # If the handler's status is false, return
    if rslt["status"] == False:
        return rslt

    return {
        "status": True,
        "reqType": reqType,
        "result": rslt["result"]
    }

#######################################
# Summarize the result
#######################################
def summarizeQstn(tbl, aTask, data):
    successQstns = list(filter(lambda x: x["status"] == True, data))
    logging.info("Questions scheduled: {}".format(len(successQstns)))
    failedQstns = list(filter(lambda x: x["status"] == False, data))

    # Determine the status of the task
    theStatus = "scheduled"
    if len(successQstns) <= 0 and len(data) > 0:
        theStatus = "fail"

    # Report any failed questions
    if len(failedQstns) > 0:
        dbConn.updateJson(tbl, "id", aTask["id"],
            "msg", {"schedule-summarizeQstn": failedQstns}
        )
        logging.warning("Questions failed: {}".format(len(failedQstns)))

    # Update the task status
    dbConn.modMultiVals(
        tbl,
        ["id"], [aTask["id"]],
        ["status", "finished"],
        [theStatus, datetime.utcnow()]
    )


#######################################
# Summarize the result based on scheduling by path IDs
#######################################
def summarizePath(tbl, aTask, data):
    theStatus = "scheduled"

    # Updated the status on the fail case
    if not data["status"]:
        theStatus = "fail"
        dbConn.updateJson(tbl, "id", aTask["id"],
            "msg", {"schedule-summarizePath": data["result"]}
        )

    dbConn.modMultiVals(
        tbl,
        ["id"], [aTask["id"]],
        ["status", "finished"],
        [theStatus, datetime.utcnow()]
    )


###############################################################################
# Main logic
###############################################################################
def task(aTask):
    tbl = "testSchedule"

    logging.info("Task {id} ({name}) --- Start".format(
        id=aTask["id"], name=aTask["name"]))

    # Add questions in testPath
    rsltReq = processReq(aTask)
    logging.debug("task-rsltReq: {}".format(rsltReq))

     # If status is false, update the status in testSchedule
    if rsltReq["status"] == False:
        # Update the status and msg of the failed task
        dbConn.modField(tbl, "id", aTask["id"], "status", "fail")
        dbConn.updateJson(tbl, "id", aTask["id"],
            "msg", {"schedule-processReq": rsltReq})

        logging.error("Failed on processReq in schedule-task: {}".format(
            rsltReq["result"]))
    else:
        # Add request data in testPath
        if rsltReq["reqType"] == "jira" or rsltReq["reqType"] == "question":
            rslt = qstnsToTestPath(aTask, rsltReq["result"])
            summarizeQstn(tbl, aTask, rslt)
        elif rsltReq["reqType"] == "schedule":
            rslt = scheduleToTestPath(aTask, rsltReq["result"])
            summarizePath(tbl, aTask, rslt)
        elif rsltReq["reqType"] == "path":
            rslt = pathsToTestPath(aTask)
            summarizePath(tbl, aTask, rslt)

    logging.info("Task {id} ({name}) --- Finish".format(
        id=aTask["id"], name=aTask["name"]))
