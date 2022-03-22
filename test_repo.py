###############################################################################
# Testing module
# python3 test_repo.py
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
import jira
import util
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=logging.DEBUG)


def getGitHash():
    task.modStts(4, "pending", ["msg"], [""])
    aTask = task.next()
    rslt = repo.getGitHash(aTask)
    print("rslt:")
    print(rslt)


def getGitHash2():
    tbl = "testSchedule"
    id = 48
    aTask = dbConn.getRow(
        tbl, ["id"], [id],
        dbConn.getFields("testSchedule"), mkObjQ=True
    )[0]
    print(aTask)
    print(aTask.keys())
    print(aTask["gitHash"])

    rslt = repo.getGitHash(aTask)
    print(rslt)


def getGitHash3():
    tbl = "testSchedule"
    id = 584
    aTask = dbConn.getRow(
        tbl, ["id"], [id],
        dbConn.getFields("testSchedule"), mkObjQ=True
    )[0]
    print(aTask)
    print(aTask.keys())
    print(aTask["gitHash"])

    rslt = repo.getGitHash(aTask)
    print(rslt)


def getGitHash4():
    tbl = "testSchedule"
    id = 584
    aTask = dbConn.getRow(
        tbl, ["id"], [id],
        dbConn.getFields("testSchedule"), mkObjQ=True
    )[0]
    print(aTask)
    print(aTask.keys())
    print(aTask["gitHash"])

    validBranch = repo.validateBranchQ(aTask, remote="origin")
    print("validBranch: ", validBranch)
    
    rslt = repo.getGitHash(aTask)
    print (rslt)


if __name__ == '__main__':
    getGitHash4()
    # getGitHash3()
    # getGitHash2()
    # getGitHash()
