###############################################################################
# Testing module
# To run
# python3 test_recurrence.py
###############################################################################
import logging
import json
import dbConn
import handleKill
from urllib.parse import urlencode
import os
import sys
import util
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=logging.DEBUG)


def getTasksInKill():
    dbConn.modTbl("testSchedule", ["id"], [84], "status", "kill")
    rslt = handleKill.getTasksInKill()
    print(rslt)

def doIt():
    dbConn.modTbl("testSchedule", ["id"], [84], "status", "kill")
    handleKill.doIt()

if __name__ == '__main__':
    doIt()
    # getTasksInKill()
