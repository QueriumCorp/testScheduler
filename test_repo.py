###############################################################################
# test.py
# Testing module
###############################################################################
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
import logging
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
    print (rslt)


if __name__ == '__main__':
    getGitHash2()
    # getGitHash()