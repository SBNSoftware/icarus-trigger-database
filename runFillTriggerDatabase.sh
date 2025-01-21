#!/bin/bash

export HOSTNAME=$(hostname)
host=$(hostname | awk -F'.' '{print $1}')
timestamp=`date +%Y_%m_%d`
now=`date "+%Y-%m-%d %T"`

LOGFILE="/daq/log/triggerdb/triggerdb_cronjob_${host}_${timestamp}.log"
PYTHON_ENV="/home/nfs/icarus/triggerDB/pyenv"

echo "$now : Starting runFillTriggerDatabase.sh on $host now!" >> $LOGFILE

if [[ ! -d $PYTHON_ENV ]]; then
    echo "$now : Creating python environment with $(python3 --version)" >> $LOGFILE
    python3 -m venv $PYTHON_ENV 
    source $PYTHON_ENV/bin/activate
    python3 -m pip install --upgrade pip -q 2>&1
    python3 -m pip install psycopg 2>&1
    python3 -m pip install numpy 2>&1
else
    echo "$now : Activating python environment" >> $LOGFILE
    source $PYTHON_ENV/bin/activate
fi

# Run fill_database.py
echo "$now : Executing fill_database.py..." >> $LOGFILE 
python3 -u /home/nfs/icarus/triggerDB/fill_database.py >> $LOGFILE 2>&1

now=`date "+%Y-%m-%d %T"`
echo "$now : Done!" >> $LOGFILE
exit 0
