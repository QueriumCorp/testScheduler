###############################################################################
# repo.py
#
###############################################################################
from dotenv import load_dotenv
load_dotenv()
import git
import gitdb
import os
import logging
import sys
import math
import time

###############################################################################
# Support functions
###############################################################################

#######################################
# Create a directory if it doesn't exist
#######################################
def mkDir(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)
        logging.info("Created a directory: {dir}".format(dir=dir))

    return dir

#######################################
# Get the repository directory
#######################################
def getRepoDir():
    result = os.path.join(
        mkDir(os.environ.get('dirScheduler')),
        os.environ.get('repoName')
    )
    return mkDir(result)


#######################################
# Clear local refers
#######################################
def clearRefs(remote="origin"):
    skip = ["HEAD"]
    dirRepo = getRepoDir()
    theRepo = git.Repo(dirRepo)
    dirRemoteRef = os.path.join(
        theRepo.working_dir, ".git", "refs", "remotes", remote)
    branches = os.listdir(dirRemoteRef)

    cntDel = 0
    for branch in branches:
        if branch in skip:
            continue

        path = os.path.join(dirRemoteRef, branch)
        if os.path.exists(path):
            os.remove(path)
            cntDel += 1
    logging.info("Deleted local refs: {}".format(cntDel))


#######################################
# Checkout a github reference
#######################################
def checkoutRef(repo, aRef):
    refBranch = str(math.ceil(time.time()))
    ## Create a branch for a new reference
    try:
        newBranch = repo.create_head(refBranch, aRef)
    except gitdb.exc.BadName as err:
        # logging.error("repo-checkoutRef: Invalid gitHash")
        raise
    else:
        repo.git.checkout(refBranch)
        logging.info("Created the {branch} branch that points to {ref}".format(branch=refBranch, ref=aRef))
        return refBranch

#######################################
# Clean up after validating gitHash
#######################################
def cleanup(repo, branchDel, branchNext="dev"):
    repo.git.checkout(branchNext)
    logging.debug("Checked out: {}".format(branchNext))
    repo.delete_head(branchDel)
    logging.debug("Deleted: {}".format(branchDel))

###############################################################################
# Main logic
###############################################################################
def getRepoDir():
    result = os.path.join(
        mkDir(os.environ.get('dirScheduler')),
        os.environ.get('repoName')
    )
    return mkDir(result)

#######################################
# Get the latest git hash on a given branch
#######################################
def validateBranchQ(aTask, remote="origin"):
    if "gitBranch" not in aTask:
        logging.error("validateBranchQ: Missing gitBranch")
        return False

    ## Get a directory for the CommonCore repo
    dirRepo = getRepoDir()
    theRepo = None
    if not os.path.isdir(os.path.join(dirRepo, ".git")):
        logging.info("Cloning the CommonCore repo .....")
        theRepo = git.Repo.clone_from(
            os.environ.get('repoUrl'),
            dirRepo
        )
    else:
        logging.info("Clearing local refs .....")
        clearRefs()

        logging.info("Fetching the latest .....")
        theRepo = git.Repo(dirRepo)
        for rmt in theRepo.remotes:
            rmt.fetch()

    # Verify if the task branch exists
    rslt = False
    taskBranch = remote + "/" + aTask["gitBranch"]
    for ref in theRepo.references:
        if ref.name == taskBranch:
            rslt = True
            break

    return rslt


#######################################
# Get the latest git hash on a given branch
#######################################
def getGitHash(aTask):
    if "gitHash" not in aTask or aTask["gitHash"]=="":
        raise NameError("Invalid gitHash")

    ## Verify if the gitBranch is valid
    if not validateBranchQ(aTask, remote="origin"):
        raise NameError("Invalid gitBranch")

    ## Get a directory for the CommonCore repo
    dirRepo = getRepoDir()

    ## Clone the remote repo locally if it doesn't already exist
    theRepo = None
    rslt = ""
    try:
        theRepo = git.Repo(dirRepo)
        theRepo.git.checkout(aTask["gitBranch"])
        theRepo.git.pull()
        logging.debug("Pulled the latest code on the {branch}".format(
            branch=aTask["gitBranch"]))

        ## Get the current gitHash
        rslt = theRepo.active_branch.commit.hexsha

        ## If gitHash points to a specific hash, create a tmp branch and point
        ## the HEAD to gitHash
        if aTask["gitHash"].lower() != "latest":
            tmpBranch = checkoutRef(theRepo, aTask["gitHash"])
            rslt = theRepo.active_branch.commit.hexsha
            ## Clean up the tmp branch
            cleanup(theRepo, tmpBranch)

    except git.exc.GitCommandError as err:
        # logging.error("repo-getGitHash-GitCommandError: Invalid gitBranch")
        raise
    except gitdb.exc.BadName as err:
        # logging.error("repo-getGitHash: Invalid gitHash")
        raise
    else:
        return rslt