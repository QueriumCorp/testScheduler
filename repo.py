###############################################################################
# repo.py
#
###############################################################################
from dotenv import load_dotenv
load_dotenv()
import git
import os
import logging
import sys

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

###############################################################################
# Main logic
###############################################################################
def getGitHash(aBranch):
    ## Get a directory for the CommonCore repo
    dirRepo = getRepoDir()

    ## Clone the remote repo locally if it doesn't already exist
    theRepo = None
    try:
        if not os.path.isdir(os.path.join(dirRepo, ".git")):
            logging.info("Cloning a repo .....")
            theRepo = git.Repo.clone_from(
                os.environ.get('repoUrl'),
                dirRepo,
                branch=aBranch
            )
            ## Validate the repo
            assert theRepo.active_branch.name == aBranch
        else:
            theRepo = git.Repo(dirRepo)
            for remote in theRepo.remotes:
                remote.fetch()
            theRepo.git.checkout(aBranch)
            theRepo.git.pull()
            logging.debug("Pulled the latest code on {aBranch}".format(aBranch=aBranch))
    except git.exc.GitCommandError as err:
        logging.error("repo-getGitHash: Invalid branch: {}".format(aBranch))
        raise
    else:
        return theRepo.active_branch.commit.hexsha

