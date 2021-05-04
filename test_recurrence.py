###############################################################################
# Testing module
# To run
# python3 test_recurrence.py
###############################################################################
import logging
import recurrence
import repo
import json
import datetime
import dbConn
import schedule
from urllib.parse import urlencode
import os
import sys
import util
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=logging.DEBUG)


def template():
    rslt = "template"
    print(rslt)


def decodeRrule():
    # data = "FREQ=DAILY;"
    # data = "TZID=US-Eastern:19970902T090000;FREQ=WEEKLY;COUNT=10"
    data = "FREQ=WEEKLY;INTERVAL=2;NEWSAMPLEON=TRUE"
    rslt = recurrence.decodeRrule(data)
    print(rslt)

def timeToSec():
    # data = datetime.datetime(2007, 12, 6, 16, 29, 43)
    # data = datetime.datetime(2007, 12, 6, 0, 1, 0)
    data = datetime.datetime(2007, 12, 6, 1, 0, 0)
    rslt = recurrence.timeToSec(data)
    print (rslt)

def timeToRunQ():
    aSchedule = dbConn.getRow(
        "testSchedule",
        ["id"], [71],
        dbConn.getFields("testSchedule"),
        fltr="",
        mkObjQ=True
    )[0]
    print ("aSchedule: {}".format(aSchedule))
    rule = recurrence.decodeRrule(aSchedule["rrule"])
    print("rule: {}".format(rule))
    print("created: {}".format(aSchedule["created"]))
    # timeNow = datetime.datetime(2021, 5, 3, 14, 10, 20)
    # timeNow = datetime.datetime(2021, 5, 3, 23, 27, 20)
    timeNow = datetime.datetime(2021, 5, 12, 14, 9, 20)
    print("timeNow: {}".format(timeNow))
    rslt = recurrence.timeToRunQ(rule, aSchedule["created"], stampNow=timeNow)
    print(rslt) # True

def mkScheduleQ():
    # data = {
    #     "name": "5731520200708080941",
    #     "rrule": "FREQ=DAILY",
    #     "created": datetime.datetime(2021, 3, 30, 15, 00, 00),
    #     "gitBranch": "dev",
    #     "gitHash": "latest"
    # }
    # dataHash = "22d8516d1cce5829df504e734f2abead6be061c5"
    data = {
        "name": "5731520200708080941",
        "rrule": "FREQ=DAILY",
        "created": datetime.datetime(2021, 3, 30, 15, 00, 00),
        "gitBranch": "dev",
        "gitHash": "57bdb3bfd4a1dd54c036acb3d4239d3bf67ea2d3"
    }
    dataHash = "57bdb3bfd4a1dd54c036acb3d4239d3bf67ea2d3"
    rslt = recurrence.mkScheduleQ(data, dataHash)
    print(rslt)

def testSchedule():
    rslt = schedule.defaultSettings(
        "testSchedule",
        {"name": "someName"},
        skip=["name"]
    )
    print (rslt)

def scheduleByRecurrence():
    # recSchedule = schedule.defaultSettings(
    #     "testSchedule",
    #     {
    #         "name": "testRec",
    #         "status": "recurring",
    #         "rrule": "FREQ=DAILY",
    #         "created": datetime.datetime(2021, 3, 31, 9, 45, 00)
    #     }
    # )
    # dbConn.addTestSchedule(recSchedule)

    # dbConn.modField("testSchedule", "id", 18,
    #     "rrule", "FREQ=MONTHLY")
    # dbConn.modField("testSchedule", "id", 18,
    #     # "created", datetime.datetime(2021, 3, 25, 14, 46, 00))
    #     "created", datetime.datetime(2021, 3, 2, 14, 46, 00))
    recurrence.scheduleByRecurrence()


def mkJiraField():
    table = "testSchedule"
    aSchedule = dbConn.getRow(
        table,
        ["id"],
        [88],
        # [28],
        dbConn.getFields(table),
        fltr="",
        mkObjQ=True
    )[0]
    # aRule = recurrence.decodeRrule("FREQ=DAILY;NEWSAMPLEON=TRUE")
    # aRule = recurrence.decodeRrule("FREQ=DAILY")
    # aRule = recurrence.decodeRrule("FREQ=DAILY;NEWSAMPLEON=FALSE")
    aRule = recurrence.decodeRrule(aSchedule["rrule"])
    rslt = recurrence.mkJiraField(aRule, aSchedule)
    print (rslt)

def sampleOn():
    aRule = recurrence.decodeRrule("FREQ=DAILY")
    table = "testSchedule"
    aSchedule = dbConn.getRow(
        table,
        ["id"],
        [88],
        # [28],
        dbConn.getFields(table),
        fltr="",
        mkObjQ=True
    )[0]
    recSchedule = schedule.defaultSettings(
        table,
        aSchedule,
        skip=[
            "status", "host", "pid", "gitBranch", "gitHash",
            "msg", "rrule", "jiraResp", "started", "finished", "created",
            "updated", "jira"
        ]
    )
    print("recSchedule: {}".format(recSchedule))

    rslt = recurrence.mkJiraField(aRule, recSchedule)
    print (rslt)

def mkSchedule():
    tbl = "testSchedule"
    gitHash = "7831f709257f7ecf7e4b8514546a1dc358cbd6c8"
    dbConn.modTbl(tbl, ["id"], [90], "gitHash", gitHash)
    dbConn.modTbl(tbl, ["id"], [88], "rrule", "FREQ=DAILY;NEWSAMPLEON=FALSE")
    # dbConn.modTbl(tbl, ["id"], [88], "rrule", "FREQ=DAILY;NEWSAMPLEON=TRUE")
    # jiraVal = json.dumps({"fields": ["key"], "qstnType": "StepWise", "useFilter": "filterTest4"})
    jiraVal = json.dumps({"questions": ["QUES-6018"]})
    dbConn.modTbl(tbl, ["id"], [88], "jira", jiraVal)
    aSchedule = dbConn.getRow(tbl, ["id"], [88], dbConn.getFields(tbl), mkObjQ=True)[0]
    print("aSchedule: {}".format(aSchedule))

    # aSchedule["rrule"] = "FREQ=DAILY;NEWSAMPLEON=FALSE"
    # aSchedule["created"] = datetime.datetime(2021, 3, 30, 15, 00, 00)
    # aSchedule["gitBranch"] = "lates"
    # aSchedule["gitHash"] = "lates"
    # aSchedule["status"] = "recurring"
    # aSchedule["msg"] = "someRandomMsg"

    # stampNow = datetime.datetime(2021, 3, 31, 11, 25, 00)
    # stampNow = datetime.datetime(2021, 3, 31, 11, 35, 00)
    # stampNow = datetime.datetime(2021, 3, 31, 11, 25, 00)
    # stampNow = datetime.datetime(2021, 3, 31, 11, 30, 00)
    stampNow = datetime.datetime(2021, 5, 4, 19, 34, 00) # True
    # stampNow = datetime.datetime(2021, 3, 31, 15, 10, 00) # False
    rslt = recurrence.mkSchedule(aSchedule, stampNow)
    print(rslt)

def jiraGotPathsQ():
    # data = {"jira": {"questions": ["a", "b"]}}
    # data = {"jira": {"paths": []}}
    # data = {"jira": {"paths": [1, 2]}}
    data = {"jiras": {"paths": [1,2]}}
    rslt = recurrence.jiraGotPathsQ(data)
    print (rslt)

if __name__ == '__main__':
    mkSchedule()
    # sampleOn()
    # jiraGotPathsQ()
    # mkJiraField()
    # scheduleByRecurrence()
    # testSchedule()
    # mkScheduleQ()
    # timeToRunQ()
    # timeToSec()
    # decodeRrule()
