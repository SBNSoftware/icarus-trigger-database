import numpy as np
import logging
import lzma

def open_trigger_log(file_path):
    """
    Opens the trigger logfile, handling both compressed (.xz) and uncompressed files.

    Parameters
    ----------
    file_path: path to the trigger log file.

    Returns
    -------
    A list containing all the lines in the file.
    """
    lines = []
    if file_path.endswith('.xz'):
        with lzma.open(file_path, mode='rt') as file:
            lines = [x.strip('\n') for x in file.readlines()]
    else:
        with open(file_path, 'r') as file:
            lines = [x.strip('\n') for x in file.readlines()]
    return lines

def parse_trigger_log(log_name, run):
    """
    Parses a single trigger log and returns a list containing the field information
    in each trigger string.

    Parameters
    ----------
    log_name: The name of the trigger log file.
    run: The run number corresponding to the log file.

    Returns
    -------
    A tuple containing the trigger string fields in the order that they appear.

    """
    fields = dict(version=1,
                  event_no=3, seconds=4, nanoseconds=5,
                  wr_event_no=7, wr_seconds=8, wr_nanoseconds=9,
                  enable_type=11, enable_event_no=13, enable_seconds=14, enable_nanoseconds=15,
                  gate_id=17, gate_type=27,
                  gate_id_BNB=19, gate_id_NuMI=21, gate_id_BNBOff=23, gate_id_NuMIOff=25,
                  beam_seconds=30, beam_nanoseconds=31,
                  trigger_type=33, trigger_source=35,
                  cryo1_e_conn_0=37, cryo1_e_conn_2=39, cryo2_w_conn_0=41, cryo2_w_conn_2=43,
                  cryo1_east_counts=45, cryo2_west_counts=47,
                  mj_adder_source_east=49, mj_adder_source_west=51,
                  flag_east=53, delay_east=55,
                  flag_west=57, delay_west=59)

    data = dict(zip(list(fields.values()), [list() for i in range(len(fields))]))
    lines = [x.strip('\n') for x in open_trigger_log(log_name)]
    strings = [x for x in lines if 'string received' in x and ((x != 'string received:: ') and ('[RATE LIMIT]' not in x))]
    count = 0
    isfirst = True
    results = list()
    for r in range(len(strings)):
     
        res = strings[r][len('string received:: '):].replace(' ', '').split(',')
     
        for ki, k in enumerate(data.keys()):
            if len(res) == 48 and ki < len(data.keys()) - 6:
                data[k].append(res[k])
            elif len(res) == 50 and ki < len(data.keys()) - 5:
                data[k].append(res[k])
            elif len(res) == 52 and ki < len(data.keys()) - 4:
                data[k].append(res[k])
            elif len(res) == 60:
                data[k].append(res[k])
            elif len(res) > 1 and (len(res) != 48 and len(res) != 50 and len(res) != 52 and len(res) != 60):
                count += 1
                if isfirst:
                    isfirst=False
        
        if len(res) == 48:
            results.append(tuple([run]+[data[k][-1] for k in list(data.keys())[:-6]]))
        elif len(res) == 50:
            results.append(tuple([run]+[data[k][-1] for k in list(data.keys())[:-5]]))
        elif len(res) == 52:
            results.append(tuple([run]+[data[k][-1] for k in list(data.keys())[:-4]]))
        elif len(res) == 60:
            results.append(tuple([run]+[data[k][-1] for k in data.keys()]))
    
    if count > 0:
        logging.warning(f'There were {count} triggers not matching the trigger string template.')
    logging.info(f'Trigger log for Run {run} processed ({len(results)} triggers).')
    
    return results
