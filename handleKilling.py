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
# Get test schedules in "killing" status
#######################################
def getTasksInKilling():
    table = "testSchedule"
    rslt = dbConn.getRow(
        table, ["status"], ["killing"], ["id"], fltr="", mkObjQ=True
    )

    return rslt

#######################################
# handle a task in "killing" status
# If none of its paths are in "running" or "acquired" status,
# Change its status to "killed" in testSchedule
#######################################
def processKilling(aTask):
    # Get paths in "acquired" or "running" status
    pathsNotDone = dbConn.getRowInConds(
        "testPath",
        ["schedule_id", "status"],
        [
            [aTask["id"]],
            ["running", "acquired"]
        ],
        ["id"],
        fltr="",
    )
    logging.debug("pathsNotDone: {}".format(len(pathsNotDone)))

    # Change the task ID to "killed" if all paths are done
    if len(pathsNotDone) <= 0:
        dbConn.modTbl("testSchedule",
            ["id"],
            [aTask["id"]],
            "status", "killed"
        )
        logging.info("Finished killing")
    else:
        logging.info("Some paths aren't done yet")


###############################################################################
# Main logic
###############################################################################
def softly():
    tasks = getTasksInKilling()

    for aTask in tasks:
        logging.info("Handling a task in the killing status: {}".format(
            aTask["id"]))
        processKilling(aTask)