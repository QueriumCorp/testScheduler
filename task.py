###############################################################################
# task.py
# Handle tasks
###############################################################################
import dbConn

###############################################################################
# Support functions
###############################################################################

#######################################
# xxxxx
#######################################

###############################################################################
# Main logic
###############################################################################
def next():
    tbl = "testSchedule"
    colStts = "status"

    ### Get a pending task
    data = dbConn.getRow(
        tbl, [colStts], ["pending"],
        dbConn.getFields("testSchedule"))
    if data is None or len(data)<1:
        return []

    ### Convert the data into an object
    rsltObj = dbConn.mkObj(dbConn.getFields("testSchedule"), data)

    ### Change the task's status to running
    dbConn.modTbl(tbl, ["id"], [rsltObj["id"]], colStts, "running")

    return rsltObj