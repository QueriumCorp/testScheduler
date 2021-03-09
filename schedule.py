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
# Remove path IDs that are already exists in the testPath table.
#######################################
def getNewPaths(testName, pathIds):
    pathIdsInData = set(pathIds)

    # Build a sql query for select
    tbl = "testPath"
    getFlds = ['path_id']
    sqlRtrn = ",".join(getFlds)
    sqlCond = "WHERE name={name}".format(name=testName)
    sql = "SELECT {sqlRtrn} FROM {tbl} {sqlCond}".format(
        sqlRtrn=sqlRtrn, tbl=tbl, sqlCond=sqlCond)
    # print (sql)
    pathIdsInDb = dbConn.fetchallQuery(
        sql, [], fldsRtrn=getFlds, mkObjQ=False)
    pathIdsInDb = set([item[0] for item in pathIdsInDb])

    newPathIds = pathIdsInData.difference(pathIdsInDb)
    return list(newPathIds)


#######################################
# mk test paths
#######################################
def mkTestPath(aTask, data):
    tbl = "testPath"
    skipFields = ["msg"]

    if len(data) < 1:
        return {
            "status": True,
            "result": 0
        }

    # Make dictionary of rows for the testPath table
    dbData = []
    for pathInfo in data:
        pathRow = defaultSettings(tbl, aTask, skipFields)
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
    pathInfo = mkPathInput(newTask)

    # If the number of paths is larger than the limit, sample the paths
    if "limitPaths" in newTask and newTask["limitPaths"] != -1:
        if len(pathInfo) > newTask["limitPaths"]:
            cntOld = len(pathInfo)
            pathInfo = random.sample(pathInfo, newTask["limitPaths"])
            logging.info("Sampled the paths from {cntOld} to {cntNew}".format(
                cntOld=cntOld, cntNew=len(pathInfo)))

    return mkTestPath(aTask, pathInfo)

    # pathFlds = ["id", "priority"]
    # paths = dbConn.getPathsInQstn(
    #     qstnId,
    #     aTask["skipStatuses"],
    #     pathFlds,
    #     flat=False
    # )
    # logging.info("Total number of paths: {}".format(len(paths)))
    # return mkTestPath(aTask, qstnId, paths)

#######################################
# Add questions in testPath
# Return:
# status: True/False
# result: a number of questions are added in testPath
#######################################
def qstnsToTestPath(aTask, qstns):
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
        rsltQstn = qstnToTestPath(aTask, qstnUnq)
        rsltQstn["unq"] = qstnUnq
        result.append(rsltQstn)

    return result

#######################################
# Add paths in testPath
#######################################
def pathsToTestPath(aTask, pathIds):

    # Get {question_id, path_id, priority} fields of each path in the task
    # request
    pathInfo = mkPathInput(aTask)

    # Remove any path_id(s) that are already in testPath under task["name"]
    allPaths = list(map(lambda x: x["path_id"], pathInfo))
    newPaths = getNewPaths(aTask["name"], allPaths)
    newInfo = list(filter(lambda x: x["path_id"] in newPaths, pathInfo))

    # Add the new paths in testPath
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
    if "questions" in aTask["jira"] and len(aTask["jira"]["questions"]) > 0:
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
    if "paths" in aTask["jira"] and len(aTask["jira"]["paths"]) > 0:
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
        taskModule.modStts(
            aTask["id"], "fail",
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

    # Add request data in testPath
    if rsltReq["reqType"] == "jira" or rsltReq["reqType"] == "question":
        rsltJira = qstnsToTestPath(aTask, rsltReq["result"])
        # summarizeQstn(tbl, aTask, rsltJira)
    elif rsltReq["reqType"] == "path":
        pathsToTestPath(aTask, rsltReq["result"])
