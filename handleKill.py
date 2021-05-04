###############################################################################
# The module is to figure out when to schedule a test based on the reccurence
# field in the testSchedule table
###############################################################################
from dotenv import load_dotenv
load_dotenv()
import os
import dbConn
import logging

###############################################################################
# Constants
###############################################################################


###############################################################################
# Support functions
###############################################################################

#######################################
# Get test schedules in "kill" status
#######################################
def getTasksInKill():
    table = "testSchedule"
    rslt = dbConn.getRow(table, ["status"], ["kill"], ["id"], fltr="", mkObjQ=True)

    return rslt

#######################################
# Kill a task
# Change the task's status to "killing" in testSchedule
# Change the status of any "pending" paths to "killed" in testPath
# "acquired" and "running" paths will be handled by handleKilling
#######################################
def processKill(aTask):
    # Change the task's status to "killing"
    dbConn.modTbl("testSchedule", ["id"], [aTask["id"]], "status", "killing")

    # Change paths in the "pending" status to "killed"
    dbConn.modTbl("testPath",
        ["status", "schedule_id"],
        ["pending", aTask["id"]],
        "status", "killed"
    )

###############################################################################
# Main logic
###############################################################################
def doIt():
    tasks = getTasksInKill()

    for aTask in tasks:
        logging.info("killing task: {}".format(aTask["id"]))
        processKill(aTask)