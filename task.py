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

    # Convert the data into an object
    rsltObj = data[0]

    # Convert json-string values into json
    if "jira" in rsltObj and rsltObj["jira"].strip() != "":
        rsltObj["jira"] = json.loads(rsltObj["jira"])
    if "skipStatuses" in rsltObj and rsltObj["skipStatuses"].strip() != "":
        rsltObj["skipStatuses"] = json.loads(rsltObj["skipStatuses"])

    return rsltObj
