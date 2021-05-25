###############################################################################
# filter.py
# Jira API module
###############################################################################
from dotenv import load_dotenv
load_dotenv()
import requests
from requests.auth import HTTPBasicAuth
import os
import json
import jql
import util
from urllib.parse import urlencode
from datetime import datetime
import logging
import dbConn

###############################################################################
# Support functions
###############################################################################

#######################################
# Does filter already exists
# parameters:
# name: name of a new filter
# jql: Jira Query Language
#######################################
def filterExistsQ(name):
    route, _ = jql.buildJql("filterNameSearch", name)
    urlRoot = os.environ.get('companyUrl')+route
    auth = HTTPBasicAuth(
        os.environ.get('jiraUser'),
        os.environ.get('api-token')
    )
    headers = {
    "Accept": "application/json"
    }

    urlNext = urlRoot
    terminateQ = False
    while not terminateQ:
        response = requests.request(
            "GET",
            urlNext,
            headers=headers,
            auth=auth
        )
        # If request fails, return the error code. Need a better way to handle?
        if response.status_code != 200:
            # return {"status": False, "result": response.status_code}
            return True

        rsltPart = json.loads(response.text)
        for val in rsltPart["values"]:
            logging.debug("name: {val}".format(val=val['name']))
            if val["name"] == name:
                return True

        nextPage = util.nextPage(rsltPart)
        terminateQ = nextPage["isLast"]
        urlNext = urlRoot+"&"+urlencode({"startAt": nextPage["startAt"]})

    return False

#######################################
# Create a filter in Jira
# NOTE: The api-token that is used to create filter belongs to Evan's account.
# It's not possible Evan to create a filter for a group that he is not a
# member of because he doesn't have enough privilege. To fix it: generate
# api-token under an account that has the privilege
# privilege.
# parameters:
# name: name of a new filter
# jqlStr: Jira Query Language
# settings: pass any settings for creating jira filter. If the share
# permission is not shareGroup, please look at the refs for
# addSharePermission
# return:
# {"status": boolean, "result": "<filterID>" or {errors}}
# Refs:
# https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filters/#api-rest-api-3-filter-post
# https://docs.atlassian.com/software/jira/docs/api/REST/1000.679.0/#api/2/filter-addSharePermission
#######################################
def mkJiraFilter(name, jqlStr, settings):
    route, _ = jql.buildJql("createFilter", name)
    url = os.environ.get('companyUrl')+route

    auth = HTTPBasicAuth(
        os.environ.get('jiraUser'),
        os.environ.get('api-token')
    )
    headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
    }

    ## Preprocess the payload
    data = {
        "name": name,
        "jql": jqlStr,
        "description": "Created at " + datetime.now().strftime("%c"),
        "sharePermissions": [{
            "type": "group", "group": {"name": "AI Engineer"}}]
    }
    if "description" in settings:
        data["description"] = settings["description"]
    if "shareGroup" in settings:
        data["sharePermissions"][0]["group"]["name"] = settings["shareGroup"]
    payload = json.dumps( data )

    response = requests.request(
        "POST",
        url,
        data=payload,
        headers=headers,
        auth=auth
    )

    rslt = json.loads(response.text)
    if "errorMessages" in rslt and len(rslt["errorMessages"])>0:
        return {"status": False, "result": "".join(rslt["errorMessages"])}
    if "errors" in rslt and len(rslt["errors"])>0:
        return {"status": False, "result": rslt["errors"]}
    if "errorMessages" in rslt or "errors" in rslt:
        return {"status": False, "result": "invalid request"}

    return {"status": True, "result": rslt["id"]}


#######################################
# Search Jira based on a JQL or a filter
# parameters:
# req: Jira Query Language
#######################################
def search(req):
    # Search jira based on the req
    if "useFilter" in req:
        logging.info("Jira search is based on a filter")
        searchFilter = jql.searchByFilter(req, flatten=True)
        if len(searchFilter) > 0:
            result = {
                "status": True,
                "filter": searchFilter["filter"],
                "keys": searchFilter["issueSearch"]["result"]
            }
        else:
            logging.error("Invalid filter: {}".format(req['useFilter']))
            result = {
                "status": False,
                "result": "Invalid filter {}".format(req['useFilter'])
            }
    else:
        logging.info("Jira search is based on a jql")
        jqlRspns = jql.issueSearch(req, flatten=True)
        if jqlRspns["status"]:
            result = {
                "status": True,
                "keys": jqlRspns["result"],
                "jql": jqlRspns["jql"]
            }
        else:
            result = {
                "status": False,
                "result": jqlRspns["result"]
            }

    return result

#######################################
# mkFilter
# parameters:
# name: name of a new filter
# jql: Jira Query Language
#######################################
def mkFilter(name, jql, settings={}):
    ## Check the filter name already exists in Jira
    if filterExistsQ(name):
        return {
            "status": False,
            "result": "already exists"
        }

    ## Create a Jira filter
    logging.info("Created a new filter in Jira {name}".format(name=name))
    return(mkJiraFilter(name, jql, settings))

###############################################################################
# Main logic
###############################################################################

#######################################
# Process request
#######################################
def process(aTask):
    tbl = "testSchedule"

    # Convert jql in a string form to json
    req = aTask["jira"]
    logging.debug("Jira request: {}".format(req))

    # Response of the jql request
    jqlRslt = search(req)

    # If jira request fails, update testSchdule and return
    if jqlRslt["status"] == False:
        jqlRslt["result"] =  "jira response error: {}".format(jqlRslt["result"])
        logging.error("Failed on process-search: {}".format(jqlRslt['result']))
        return jqlRslt

    # Update testSchedue with the jira result
    dbConn.modMultiVals(
        tbl,
        ["id"], [aTask["id"]],
        ["jiraResp"], [json.dumps(jqlRslt["keys"], separators=(',', ':'))])
    logging.info("Updated Task {id} with jira response".format(
        id=aTask['id']))

    # Create a new jira based on the given jql
    if "makeFilter" in req and "useFilter" not in req:
        fltrRslt = jira.mkFilter(req["makeFilter"], jqlRslt["jql"])
        if fltrRslt["status"] == False:
            dbConn.modMultiVals(
                tbl,
                ["id"], aTask["id"],
                ["status", "finished", "msg"],
                ["Fail", datetime.now(), fltrRslt["result"]])
            logging.error("Unable to create a Jira filter: {}".format(
                req['makeFilter']))
        else:
            logging.error("Successfully created a Jira filter: {}".format(
                req['makeFilter']))

    return jqlRslt