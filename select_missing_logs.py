import logging
import os
import json
import psycopg
import shutil
from glob import glob
from tools.parsers import parse_trigger_log, open_trigger_log
from tools.database_tools import command

source_directory = "/exp/icarus/data/users/mueller/logs/trigger_logs/"
output_directory = "/exp/icarus/app/users/mvicenzi/icarus-trigger-database/matching_files/"

def scan_trigger_log(conn, log_directory, no_match_directory):
    
    curs = conn.cursor()
    log_files = glob(f'{log_directory}*')
    for f in log_files:
        log_name = f.split('/')[-1] 
        lines = open_trigger_log(f)
        runs = [x for x in lines if 'Completed the Start transition (Started run) for run ' in x]
        if(len(runs)<1):
            print(f'{log_name} has no run number!')
            continue
        run = runs[0][53:runs[0].find(',')]
        curs.execute('SELECT log_name FROM triggerlog WHERE run_number=%s', (run,))
        res = curs.fetchall()
        if len(res) != 0:
            print(f'{log_name} matches run {run} ({res[0]})')
        else:
            print(f'{log_name} has no matches in db')
            new_log_name = "run" + run + "-icarustrigger.log"
            shutil.copy2(f'{log_directory}{log_name}',f'{no_match_directory}{new_log_name}')
            print(f'Copying to {no_match_directory}')

def main():

    # Load the JSON configuration file
    configuration_file = "./config.json"
    config = json.load(open(configuration_file,'r'))

    dbconfig = config["database"]
    try:
        conn = psycopg.connect(user=dbconfig["user"],
                               host=dbconfig["host"],
                               port=dbconfig["port"],
                               dbname=dbconfig["name"],
                               password=dbconfig["password"])
        scan_trigger_log(conn, source_directory, output_directory)
    
    except Exception as e:
        print(str(e)+'\nConnection to database failed. Exititing.')


if __name__ == '__main__':
    main()
