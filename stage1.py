import argparse
import os 
from pathlib import Path
import logging
import pandas
'''

'''
STAGE1="stage1"
ENV_VAR_USERS="USERS"
STAGE1_DIRNAME=STAGE1
logging.basicConfig(level="DEBUG")
LOGGER = logging.getLogger(STAGE1_DIRNAME)
LOGGER.setLevel("DEBUG")
USERS=[]

def finduser_from_csvfilename(csvfilename, l = LOGGER):
    s = csvfilename.split("_")
    user="unknown"
    if s[0].lower() in USERS:
        user = s[0].lower()
    l.debug("User = " + user)
    return user
        

def process_one_csv(csvfile, outputdir, l = LOGGER) :
    csv = pandas.read_csv(csvfile)
#    l.debug(csv.to_string())
    csvfilename = os.path.basename(csvfile)
    user = finduser_from_csvfilename(csvfilename)
    csv["Excelname"] = csvfilename
    csv["Cash_or_Card"] = "Card"
    csv["User"] = user
#    l.debug(csv.to_string())
    stage1_csv_file = os.path.join(outputdir, STAGE1 + "_" + os.path.basename(csvfile))
    l.debug("stage1_csv_file = " + stage1_csv_file)
    csv.to_csv(stage1_csv_file)

def stage1(statementdir, outputdir, l=LOGGER) :
    u = os.getenv(ENV_VAR_USERS)
    global USERS
    USERS = u.split(",") if u else []
    l.debug("USERS = " + str(USERS))
    l.debug("statementdir = " + statementdir + "outputdir = " + outputdir)
    if not os.path.isdir(statementdir) :
        raise Exception("Invalid statement directory")
    if not os.path.isdir(outputdir):
        raise Exception("Invalid output directory")
    stage1_dir = os.path.join(outputdir, STAGE1_DIRNAME)
    if os.path.isdir(stage1_dir):
        raise Exception("Stage1 directory :" + stage1_dir + " already exists")
    csvfiles = Path(statementdir).glob("*.csv")
    csvfiles = list(csvfiles)
    if len(csvfiles) == 0:
        raise Exception("No csvfiles in ", + statementdir)
    os.mkdir(stage1_dir) 
    for csvfile in csvfiles:
        l.debug("Found : " + str(csvfile))
        process_one_csv(csvfile, stage1_dir, l)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--statementdir", required=True)
    ap.add_argument("--outputdir", required=True)

    a = ap.parse_args()
    stage1(a.statementdir, a.outputdir)

if __name__ == '__main__':
    main()