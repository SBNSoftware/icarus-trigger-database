import logging
import os
from glob import glob
from tools.parsers import parse_trigger_log, open_trigger_log
from tools.database_tools import command

def update_triggerlog(conn, triggerlog_directory, sql_directory):
    """
    Scans the trigger log directory for logs with no entry in table 'triggerlog.'
    If no matching entry is found, do a quick parsing of the log to verify that it
    isn't a "stub" (a failed run - no actual triggers) and retrieve the run number.

    Parameters
    ----------
    conn: psycopg.Connection
        The PostgreSQL connection handle.
    triggerlog_directory: str
        The path to the directory containing the trigger logs.
    sql_directory: str
        The path to the directory containing the SQL queries

    Returns
    -------
    None.
    """
    logging.info('Updating table `triggerlog`.')
    curs = conn.cursor()
    log_files = glob(f'{triggerlog_directory}run*-icarustrigger.log*')
    logging.info(f'Found {len(log_files)} files in trigger log directory ({triggerlog_directory}).')
    for f in log_files:
        log_name = f.split('/')[-1]
        command(curs, sql_directory+'select_triggerlog_logname.sql', (log_name,))
        file_size = os.path.getsize(f)
        res = curs.fetchall()
        if len(res) == 0:
            try:
                lines = open_trigger_log(f)
                runs = [x for x in lines if 'Completed the Start transition (Started run) for run ' in x]
                run = runs[0][53:runs[0].find(',')]
                command(curs, sql_directory+'insert_triggerlog_standard.sql', (log_name, False, file_size, run))
                conn.commit()
                logging.info(f'New trigger log entry for Run {run} (file: {log_name}).')
            except IndexError:
                command(curs, sql_directory+'insert_triggerlog_standard.sql', (log_name, True, file_size, 0))
                conn.commit()
                logging.info(f'Trigger log file {log_name} is a stub.')
        elif res[0][2] != file_size:
            command(curs, sql_directory+'update_triggerlog_reprocess.sql', (log_name,))
            command(curs, sql_directory+'update_triggerlog_filesize.sql', (file_size, log_name))
            conn.commit()
            logging.info(f'Trigger log for Run {res[0][3]} ({log_name}) has new file size on disk and will be reprocessed.')


def update_triggerdata(conn, triggerlog_directory, sql_directory):
    """
    Checks for unprocessed log files in the trigger log table, then parses any
    log files found. Information from the trigger log files will be stored to
    the `triggerdata` table. The parsed list of triggers is checked against
    existing entries for the run to ensure duplication does not occurr in the
    case of log files that have been updated on disk.

    Parameters
    ----------
    conn: psycopg.Connection
        The PostgreSQL connection handle.
    triggerlog_directory: str
        The path to the directory containing the trigger logs.
    sql_directory: str
        The path to the directory containing the SQL queries

    Returns
    -------
    None.
    """
    logging.info('Updating table `triggerdata`.')
    curs = conn.cursor()
    command(curs, sql_directory+'select_triggerlog_process.sql')
    res = curs.fetchall()
    logging.info(f'Found {len(res)} log files with unprocessed status.')
    
    for r in res:

        triggers = parse_trigger_log(triggerlog_directory+r[0], r[3])
        run = r[3]

        command(curs, sql_directory+'select_triggerdata_runnumber.sql', (run,))
        existing_triggers = [(e[0], str(e[2])) for e in curs.fetchall()]
        triggers = [x for x in triggers if (x[0], x[2]) not in existing_triggers]
        
        if len(existing_triggers) != 0 and len(triggers) != 0:
            logging.info(f'Found {len(triggers)} new triggers for Run {run}.')
        
        version = triggers[0][1] if len(triggers) != 0 else 1
        command(curs, f'{sql_directory}insert_triggerdata_standard_v{version}.sql', triggers)
        command(curs, sql_directory+'update_triggerlog_processed.sql', (r[0],))
        conn.commit()
