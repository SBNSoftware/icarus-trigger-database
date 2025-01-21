import psycopg
import logging
import sys, os
import json
from datetime import datetime
from tools.database_tools import command
from tools.handlers import update_triggerlog, update_triggerdata

configuration_file = "/home/nfs/icarus/triggerDB/config.json"

def main():

    # Load the JSON configuration file
    config = json.load(open(configuration_file,'r'))

    # Configure logging.
    logconfig = config["logging"]
    levels = {"ERROR": logging.ERROR,"WARNING": logging.WARNING,"INFO": logging.INFO}

    date = datetime.now().strftime("%Y_%m_%d")
    host = os.getenv("HOSTNAME").split(".")[0]
    logfile = logconfig["logpath"] + "triggerdb_" + host + "_" + date + ".log"
    logging.basicConfig(filename=logfile,
                        level=levels.get(logconfig["level"].upper(),logging.INFO),
                        format=logconfig["format"],
                        datefmt=logconfig["datefmt"])
    logging.info('Call to fill_database.py initiated.')

    # Open connection to the database.
    dbconfig = config["database"]
    try:
        conn = psycopg.connect(user=dbconfig["user"],
                               host=dbconfig["host"],
                               port=dbconfig["port"],
                               dbname=dbconfig["name"],
                               password=dbconfig["password"])
        logging.info('Connection to database established.')
    except Exception as e:
        logging.error(str(e)+'\nConnection to database failed. Exititing.')
        sys.exit(1)

    curs = conn.cursor()

    # Create tables
    inputconfig = config["input"]
    command(curs, inputconfig["queries"]+'tabledef_triggerlog.sql')
    command(curs, inputconfig["queries"]+'tabledef_triggerdata.sql')
    conn.commit()

    # Update tables.
    update_triggerlog(conn, inputconfig["directory"], inputconfig["queries"])
    update_triggerdata(conn, inputconfig["directory"], inputconfig["queries"])

if __name__ == '__main__':
    main()
