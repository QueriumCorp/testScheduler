###############################################################################
# dbConn.py
# MySQL module

# Requirements
# Python >= 3.4

# Need the following modules
# python3 -m pip install PyMySQL

###############################################################################
from dotenv import load_dotenv
load_dotenv()
import pymysql
import os
import json

###############################################################################
# Support functions
###############################################################################

#######################################
# Get fiedls in a table
#######################################
def getFields(tbl):
    switcher = {
        "testSchedule": [
            "id","name","jira","author","gradeStyle","policies","validStatus",
            "status","limitPaths","limitStepTime","limitSteps","limitPathTime","host","pid","gitBranch","gitHash","mmaVersion","timeOutTime",
            "ruleMatchTimeOutTime","msg","jiraResp","started","finished","created"
            ],
        "testPath": [
            "name","question_id","path_id","trace_id","diff_id","author",
            "gradeStyle","policies","status","limitStepTime","limitSteps",
            "limitPathTime","pid","stepCount","stepsCompleted","timeCompleted",
            "host","gitBranch","gitHash","mmaVersion","timeOutTime",
            "ruleMatchTimeOutTime","msg","started","finished"
            ]
    }

    return switcher.get(tbl, [])

#######################################
# Handle test paths already in the testPath table.
# - Remove the test paths that are already in pending status
# - Change status to pending if they are in completed status and remove
#######################################
def rmExistingPaths(data):
    test = []
    keys = ['name', 'path_id']
    for row in data:
        test.append({k: row[k] for k in keys})



###############################################################################
# Main logic
###############################################################################

#######################################
# Get a row from the testSchedule table based on the condition pair of
# cols and vals
# parameters:
# tbl: a table name
# cols: a list of fields for query condition
# vals: a list of values for the fields
# colsRtrn: a list of fields to be returned
# [fltr]: additional query attributes
#######################################
def getRow(tbl, cols, vals, colsRtrn, fltr=""):
    sqlRtrn = ",".join(colsRtrn)
    sqlCond = "=%s AND ".join(cols)+"=%s "
    sql = "SELECT "+sqlRtrn+" FROM "+tbl+" WHERE "+sqlCond+fltr
    conn = pymysql.connect(
        os.environ.get('DB_HOST'), os.environ.get('DB_USER'),
        os.environ.get('DB_PASS'), os.environ.get('DB_NAME'),
        use_unicode=True, charset="utf8")
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, tuple(vals))
            rslt = cursor.fetchone()
    except pymysql.Error:
        raise Exception("Error in pymysql")
    finally:
        conn.close()

    return rslt

#######################################
# Get paths in a question
# parameters:
# identifier: unq or id of a question
# statuses: a list of path status to get
# colsRtrn: a list of fields to be returned
# [fltr]: additional query attributes
# [flat]: flatten the result
#######################################
def getPathsInQstn(identifier, statuses, colsRtrn, fltr="", flat=True):
    print ("getPathsInQstn")
    rtrn = ",".join(colsRtrn)
    stts = "\""+"\",\"".join(statuses)+"\""
    sql = f"SELECT {rtrn} FROM path WHERE status NOT IN ({stts}) AND "+\
        f"id IN (SELECT path_id FROM question_path "+\
        f"WHERE question_id IN (SELECT id FROM question "+\
        f"WHERE unq=\"{identifier}\")) {fltr};"
    if isinstance(identifier, int):
        sql = f"SELECT {rtrn} FROM path WHERE status NOT IN ({stts}) AND "+\
            f"id IN (SELECT path_id FROM question_path "+\
            f"WHERE question_id={identifier}) {fltr};"
    print (sql)

    conn = pymysql.connect(
        os.environ.get('DB_HOST'), os.environ.get('DB_USER'),
        os.environ.get('DB_PASS'), os.environ.get('DB_NAME'),
        use_unicode=True, charset="utf8")
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            rslt = cursor.fetchall()
    except pymysql.Error:
        raise Exception("Error in pymysql")
    finally:
        conn.close()

    return [item[0] for item in rslt] if flat else rslt

#######################################
# Add rows in testPath
# parameters:
# data: list of dictionaries. The dictionary keys are fields in testPath.
# NOTE: some keys may not be valid fields, so extract only field keys from dict
#######################################
def addTestPaths(data):
    tbl = "testPath"
    ### Get only valid field keys in data because data may contain keys that
    ### are not valid fields in testPath.
    keys = set(getFields(tbl)).intersection(set(data[0].keys()))

    ### Build a sql query for inserting multiple rows
    sqlKeys = ",".join(keys)
    sqlPh = ",".join(["("+",".join(["%s"]*len(keys))+")"]*len(data))
    sqlVals = [ i for row in data for i in [row[k] for k in keys] ]
    sql = f"INSERT INTO {tbl} ({sqlKeys}) VALUES {sqlPh}"
    # print (sql)

    conn = pymysql.connect(
        os.environ.get('DB_HOST'), os.environ.get('DB_USER'),
        os.environ.get('DB_PASS'), os.environ.get('DB_NAME'),
        use_unicode=True, charset="utf8")
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, sqlVals)
            conn.commit()
    except pymysql.Error:
        raise Exception("Error in pymysql")
    finally:
        conn.close()
