###############################################################################
# task.py
# Handle tasks
###############################################################################
import dbConn
import json
from datetime import datetime

###############################################################################
# Support functions
###############################################################################

#######################################
# xxxxx
#######################################

#######################################
# xxxxx
#######################################
def modStts(id, stts, cols=[], vals=[]):
    tbl = "testSchedule"
    colsDb = ["status"] + cols
    valsDb = [stts] + vals

    # Get a pending task
    dbConn.modMultiVals(tbl, ["id"], [id], colsDb, valsDb)

###############################################################################
# Main logic
###############################################################################
def next():
    tbl = "testSchedule"
    colStts = "status"

    # Get a pending task
    data = dbConn.getRow(
        tbl, [colStts], ["pending"],
        dbConn.getFields("testSchedule"), mkObjQ=True)
    if data is None or len(data) < 1:
        return []

    return data[0]
