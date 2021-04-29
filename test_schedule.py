###############################################################################
# To run
# python3 test_schedule.py
###############################################################################
import logging
from mysql.connector import errorcode
import mysql.connector
import task
import repo
import json
from datetime import datetime
import schedule
import dbConn
from urllib.parse import urlencode
import os
import jql
import input
import jira
import util
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=logging.DEBUG)


def template():
    rslt = "template"
    print("rslt:")
    print(rslt)


def processReq():
    task.modStts(4, "pending", ["msg"], [""])
    aTask = task.next()
    rslt = schedule.processReq(aTask)
    print("rslt:")
    print(rslt)


def mkPathInput():
    task.modStts(4, "pending", ["msg"], [""])
    aTask = task.next()
    rslt = schedule.mkPathInput(aTask)
    print("rslt:")
    print(rslt)


def getNewPaths():
    task.modStts(4, "pending", ["msg"], [""])
    aTask = task.next()
    pathInfo = schedule.mkPathInput(aTask)
    allPaths = list(map(lambda x: x["path_id"], pathInfo))
    rslt = schedule.getNewPaths(aTask["id"], allPaths)
    print("rslt:")
    print(rslt)


def defaultSettings():
    task.modStts(4, "pending", ["msg"], [""])
    aTask = task.next()
    print ("aTask:", aTask)
    tbl = "testPath"
    skipFields = ["msg", "started", "finished"]
    rslt = schedule.defaultSettings(tbl, aTask, skipFields)
    print(rslt)

def mkTestPath():
    task.modStts(48, "pending", ["msg"], [""])
    aTask = task.next()
    pathInfo = schedule.mkPathInput(aTask)
    allPaths = list(map(lambda x: x["path_id"], pathInfo))
    newPaths = schedule.getNewPaths(aTask["id"], allPaths)
    newInfo = list(filter(lambda x: x["path_id"] in newPaths, pathInfo))
    rslt = schedule.mkTestPath(aTask, newInfo)

    print("rslt:")
    print(rslt)

def multiUnq():
    aRow = dbConn.getRow(
        "testSchedule", ["id"], [11],
        dbConn.getFields("testSchedule"))
    aTaskS = dbConn.mkObj(dbConn.getFields("testSchedule"), aRow[0])
    aTaskS["jira"] = json.loads(aTaskS["jira"])
    aTaskS["skipStatuses"] = json.loads(aTaskS["skipStatuses"])
    # print(aTaskS)
    rsltProc = schedule.processReq(aTaskS)
    qstns = rsltProc["result"]
    # print(qstns)
    for unq in qstns:
        qstnData = dbConn.getRow("question", ["unq"], [unq], ["id"], fltr="")

    # print("rslt:")
    # print(rslt)

def handleSchedule():
    # task.modStts(55, "pending", ["msg"], [""])
    # aTask = task.next()
    # aTask = {"jira": {"useScheduleId": "4"}}

    aTask = {"jira": {"useScheduleId": 4}}
    rslt = schedule.handleSchedule(aTask)
    print(rslt)
    
def runTask():
    # task.modStts(4, "success", ["msg"], [""])
    task.modStts(85, "pending", ["msg"], [""])
    aTask = task.next()
    schedule.task(aTask)

def processReq2():
    task.modStts(85, "pending", ["msg"], [""])
    aTask = task.next()
    print(aTask)
    print(aTask["jira"])
    rslt = schedule.processReq(aTask)
    print(rslt)


def qstnsToTestPath():
    task.modStts(85, "pending", ["msg"], [""])
    aTask = task.next()
    rsltReq = schedule.processReq(aTask)
    print("rsltReq")
    print(rsltReq)
    rslt = schedule.qstnsToTestPath(aTask, rsltReq["result"])
    print("rslt")
    print(rslt)

if __name__ == '__main__':
    # qstnsToTestPath()
    runTask()
    # processReq2()
    # handleSchedule()
    # mkTestPath()
    # multiUnq()
    # defaultSettings()
    # getNewPaths()
    # mkPathInput()
    # processReq()
