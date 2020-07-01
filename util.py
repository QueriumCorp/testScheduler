def nextPageQ(resp):
    ## if a response contains isLast, return
    if "isLast" in resp:
        return {
            "isLast": resp["isLast"],
            "startAt": resp["startAt"]+resp["maxResults"]
        }

    ## if a response missing any of the these fields, no more data
    if "startAt" not in resp or "maxResults" not in resp:
        return {
            "isLast": True,
            "startAt": 0
        }

    ## if startAt+maxResults < total
    if (resp["startAt"]+resp["maxResults"]) < resp["total"]:
        return{
            "isLast": False,
            "startAt": resp["startAt"]+resp["maxResults"]
        }

    ## else
    return {
        "isLast": True,
        "startAt": 0
    }