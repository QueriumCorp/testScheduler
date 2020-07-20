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
import logging

###############################################################################
# Support functions
###############################################################################

#######################################
# XXXXX
#######################################
def mkSql(type, cols, colsRtrn, fltr="", tbl="testSchedule"):
    sql = ""
    if type == "getTask":
        sqlRtrn = ",".join(colsRtrn)
        sqlCond = "=%s AND ".join(cols)+"=%s "
        sql = "SELECT "+sqlRtrn+" FROM "+tbl+" WHERE "+sqlCond+fltr

    if sql == "":
        # logging.error("Invalid type: %s" % (type))
        raise Exception (f"Invalid type in mkSql: {type}")
    return sql

###############################################################################
# Main logic
###############################################################################

#######################################
# Get a row from the testSchedule table based on the condition pair of
# cols and vals
# parameters:
# cols: a list of fields for query condition
# vals: a list of values for the fields
# colsRtrn: a list of fields to be returned
# [fltr]: additional query attributes
#######################################
def getTask(cols, vals, colsRtrn, fltr=""):
    print ("getTask")
    conn = pymysql.connect(
        os.environ.get('DB_HOST'), os.environ.get('DB_USER'),
        os.environ.get('DB_PASS'), os.environ.get('DB_NAME'),
        use_unicode=True, charset="utf8")

    try:
        sql = mkSql("getTask", cols, colsRtrn, fltr)
        with conn.cursor() as cursor:
            cursor.execute(sql, tuple(vals))
            rslt = cursor.fetchone()
    except pymysql.Error as err:
        print (f"Error in pymysql")
        print (err)
    except Exception as err:
        print ("Error:", err)
    finally:
        conn.close()

    return rslt
