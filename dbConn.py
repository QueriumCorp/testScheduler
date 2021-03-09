###############################################################################
# dbConn.py
# MySQL module

# Requirements
# Python >= 3.4

# Need the following modules
# python3 -m pip install mysql-connector-python

###############################################################################
import sys
import logging
import json
import os
from mysql.connector import errorcode
import mysql.connector
from dotenv import load_dotenv
load_dotenv()

###############################################################################
# Support functions
###############################################################################

#######################################
# Make objects
#######################################
def mkObj(keys, data):
    return dict(zip(keys, data))


def mkObjs(keys, data):
    return list(map(lambda aRow: dict(zip(keys, aRow)), data))


#######################################
# Get fiedls in a table
#######################################
def getFields(tbl):
    switcher = {
        "testSchedule": [
            "id", "name", "jira", "author", "gradeStyle", "policies", "skipStatuses",
            "status", "limitPaths", "priority", "limitPathTime", "host", "pid", "gitBranch", "gitHash", "mmaVersion", "timeOutTime",
            "ruleMatchTimeOutTime", "msg", "jiraResp", "started", "finished", "created"
        ],
        "testPath": [
            "name", "question_id", "path_id", "trace_id", "diff_id", "author",
            "gradeStyle", "policies", "status", "ref_id", "priority",
            "limitPathTime", "pid", "stepCount", "stepsCompleted", "timeCompleted",
            "host", "gitBranch", "gitHash", "mmaVersion", "timeOutTime",
            "ruleMatchTimeOutTime", "msg", "started", "finished"
        ]
    }

    return switcher.get(tbl, [])

###############################################################################
# Main logic
###############################################################################

#######################################
# Execute an sql query and return fetchall
# parameters:
# query: sql query in string
# vals: a tuple of values
#######################################
def exec(query, cmd="fetchall", vals=tuple()):
    try:
        conn = mysql.connector.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASS'),
            database=os.environ.get('DB_NAME'),
        )
        with conn.cursor() as cursor:
            cursor.execute(query, vals)
            if (cmd == "fetchall"):
                return cursor.fetchall()
            elif (cmd == "fetchone"):
                return cursor.fetchone()
            elif (cmd == "commit"):
                conn.commit()
            else:
                logging.error("Invalid cmd")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    finally:
        conn.close()


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
def getRow(tbl, cols, vals, colsRtrn, fltr="LIMIT 1"):
    sqlRtrn = ",".join(colsRtrn)
    sqlCond = "=%s AND ".join(cols) + "=%s "
    sql = "SELECT {flds} FROM {tbl} WHERE {cond} {fltr};".format(
        flds=sqlRtrn, tbl=tbl, cond=sqlCond, fltr=fltr)
    logging.debug("getRow-sql: {}".format(sql))

    rslt = exec(sql, vals=tuple(vals))
    return rslt

#######################################
# Get paths in a question
# parameters:
# identifier: unq or id of a question
# statuses: a list of path status to skip
# colsRtrn: a list of fields to be returned
# [fltr]: additional query attributes
# [flat]: flatten the result
# Examples:
# getPathsInQstn("QUES-12889", [], ["id", "status"])
# getPathsInQstn(58418, [], ["id", "status"])
#######################################
def getPathsInQstn(identifier, statuses, colsRtrn, fltr="", flat=True):
    rtrn = ",".join(colsRtrn)
    stts = "\"" + "\",\"".join(statuses) + "\""

    sqlQstn = identifier
    if isinstance(identifier, str):
        sqlQstn = "SELECT id FROM question WHERE unq='{unq}'".format(
            unq=identifier)
    sqlPath = "SELECT path_id FROM question_path WHERE "
    sqlPath += "question_id IN ({sqlQstn})".format(sqlQstn=sqlQstn)
    sqlStts = "" if len(
        statuses) == 0 else "status NOT IN ({stts}) AND ".format(stts=stts)

    sql = "SELECT {rtrn} FROM path WHERE {sqlStts} id IN ({sqlPath}) {fltr};".format(
        rtrn=rtrn, sqlStts=sqlStts, sqlPath=sqlPath, fltr=fltr)
    logging.debug("getPathsInQstn - sql: {sql}".format(sql=sql))

    rslt = exec(sql)
    return [item[0] for item in rslt] if flat else rslt

#######################################
# Add rows in testPath
# parameters:
# data: list of dictionaries. The dictionary keys are fields in testPath.
# NOTE: some keys may not be valid fields, so extract only field keys from dict
# Example:
# addTestPaths([{"name": "test", "author": "eb"}])
#######################################
def addTestPaths(data):
    tbl = "testPath"
    # Get only valid field keys in data because data may contain keys that
    # are not valid fields in testPath.
    keys = set(getFields(tbl)).intersection(set(data[0].keys()))

    # Build a sql query for inserting multiple rows
    sqlKeys = ",".join(keys)
    sqlPh = ",".join(["("+",".join(["%s"]*len(keys))+")"]*len(data))
    sqlVals = [i for row in data for i in [row[k] for k in keys]]
    sql = "INSERT INTO {tbl} ({sqlKeys}) VALUES {sqlPh}".format(
        tbl=tbl, sqlKeys=sqlKeys, sqlPh=sqlPh)
    # logging.debug("addTestPaths - sql: {sql}".format(sql=sql))

    exec(sql, cmd="commit", vals=tuple(sqlVals))

#######################################
# Update a table in the database
# Parameters
# tbl: name of a table
# colsCond: a list of field names
# valsCond: a list of field values
# col: a field name to be changed
# val: a new value of the field name
# Example:
# modTbl("testSchedule", ["id"], [1], "status", "pending")
#######################################
def modTbl(tbl, colsCond, valsCond, col, val):
    sqlCond = "=%s AND ".join(colsCond)+"=%s "
    sql = "UPDATE {tbl} SET {col}='{val}' WHERE {sqlCond};".format(
        tbl=tbl, col=col, val=val, sqlCond=sqlCond)
    logging.debug("modTbl - sql: {sql}".format(sql=sql))

    exec(sql, cmd="commit", vals=tuple(valsCond))


def modMultiVals(tbl, colsCond, valsCond, cols, vals):
    sqlSet = "=%s,".join(cols)+"=%s"
    sqlCond = "=%s AND ".join(colsCond)+"=%s "
    sql = "UPDATE {tbl} SET {sqlSet} WHERE {sqlCond};".format(
        tbl=tbl, sqlSet=sqlSet, sqlCond=sqlCond)
    logging.debug("modTbl - sql: {sql}".format(sql=sql))

    exec(sql, cmd="commit", vals=tuple(vals + valsCond))


#######################################
# Fetch all in a sql query
# Parameters
# sql: sql query string
# vals: any values for the place holders in the query string
# fldsRtrn: a list of fields to be return
# mkObjQ: True/False - turn the query result into an object. If mkObjQ is True,
#         make sure SELECT fields are the same as fldsRtrn values
# Example
# fetchallQuery("SELECT * FROM testPath;", [], fldsRtrn=["id","name"], mkObjQ=True)
#######################################
def fetchallQuery(sql, vals, fldsRtrn=[], mkObjQ=False):
    valTuple = tuple(vals) if not isinstance(vals, tuple) else vals
    result = exec(sql, cmd="fetchall", vals=valTuple)

    if mkObjQ:
        return mkObjs(fldsRtrn, result)

    return result

#######################################
# Run a sql query
# parameters:
#######################################
def execQuery(sql, vals, fldsRtrn=[], mkObjQ=False):
    valTuple = tuple(vals) if not isinstance(vals, tuple) else vals
    exec(sql, vals=valTuple, cmd="commit")


#######################################
# Get unq IDs of question IDs
# parameters:
#######################################
def getUnq(qstnIds, flat=True):
    tbl = "question"

    # Build a sql query for inserting multiple rows
    sqlIds = ",".join(map(lambda x: str(x), qstnIds))
    sql = "SELECT unq FROM {tbl} WHERE id in({ids})".format(
        tbl=tbl, ids=sqlIds)
    # logging.debug("getUnq - sql: {sql}".format(sql=sql))
    rslt = exec(sql)

    return [item[0] for item in rslt] if flat else rslt


#######################################
# Get path ids and with their priority
# parameters:
#######################################
def getPaths(flds, ids, skipStatus=[]):
    tbl = "path"
    stts = "\"" + "\",\"".join(skipStatus) + "\""

    "select id,priority from path where status not in ('xx', 'yy') and id in (3,4)"

    # Build a sql query for inserting multiple rows
    rtrnFlds = ",".join(flds)
    sqlIds = ",".join(list(map(lambda x: str(x), ids)))
    sqlStts = "" if len(skipStatus) == 0 else \
        "status NOT IN ({stts}) AND ".format(stts=stts)
    sql = "SELECT {rtrn} FROM {tbl} WHERE {sqlStts} id IN ({ids})".format(
        rtrn=rtrnFlds, tbl=tbl, sqlStts=sqlStts, ids=sqlIds)
    logging.debug("getUnq - sql: {sql}".format(sql=sql))
    rslt = exec(sql)

    return rslt

#######################################
# Get question ids of path ids
#######################################
def getQstnIds(pathIds):
    tbl = "question_path"
    flds = ["question_id", "path_id"]
    # Build a sql query for inserting multiple rows
    rtrnFlds = ",".join(flds)
    sqlIds = ",".join(list(map(lambda x: str(x), pathIds)))
    sql = "SELECT {rtrn} FROM {tbl} WHERE path_id IN ({ids})".format(
        rtrn=rtrnFlds, tbl=tbl, ids=sqlIds)
    # print(sql)
    rslt = exec(sql)

    return rslt