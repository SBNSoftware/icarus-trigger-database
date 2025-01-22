## icarus-trigger-database
This repository organizes code that is used for extracting information from trigger log files and placing the results in an event-by-event PostgreSQL database.
The main script `runFillTriggerDatabase.sh` runs daily as a cronjob in the online cluster and scans the backup trigger logfile directory for new files to parse.
Future plans involve moving the filling operation inside the DAQ itself through an analyzer module for maximum reliablity. 

## Tables
### Trigger Data
The `triggerdata` table encapsulates all information that exists at the per-trigger level. It corresponds to the contents of the trigger TCP/IP packet.

| Column  | Type | Description | Default |
| --------| ---- | ----------- | ------- |
|`run_number`        | integer | DAQ run number ||
|`version`           | integer | Version numbering for the trigger string data ||
|`event_no`          | integer | Event number ||
|`seconds`           | integer | Local time stamp of the global trigger (seconds) ||
|`nanoseconds`       | integer | Local time stamp of the global trigger (nanoseconds) ||
|`wr_event_no`       | integer | Event number from the White Rabbit ||
|`wr_seconds`        | integer | Time stamp of the global trigger (seconds) ||
|`wr_nanoseconds`    | integer | Time stamp of the global trigger (nanoseconds) ||
|`enable_type`       | integer | Enable gate type ||
|`enable_seconds`    | integer | Time stamp of the enable gate (seconds) ||
|`enable_nanoseconds`| integer | Time stamp of the enable gate (nanoseconds) ||
|`gate_id`           | integer | Number of the current gate ||
|`gate_type`         | integer | Number encoding the type of gate (1: BNB, 2: NuMI, 3: BNBOffbeam, 4: NuMIOffbeam, 5: Calibration)||
|`gate_id_bnb`       | integer | Gate ID (BNB) ||
|`gate_id_numi`      | integer | Gate ID (NuMI) ||
|`gate_id_bnboff`    | integer | Gate ID (offbeam BNB) ||
|`gate_id_numioff`   | integer | Gate ID (offbeam NuMI) ||
|`beam_seconds`      | integer | Time stamp of the beam gate (seconds) ||
|`beam_nanoseconds`  | integer | Time stamp of the beam gate (nanoseconds) ||
|`trigger_type`      | integer | Type of trigger logic (0: Majority, 1: MinBias) ||
|`trigger_source`    | integer | Originating cryostat of the trigger (0: Undecided, 1: East, 2: West, 7: Both)||
|`cryo1_e_conn_0` | text |64-bit word with the status of the pairs of PMT discriminated signals (LVDS) for the EE wall||
|`cryo1_e_conn_2` | text |64-bit word with the status of the pairs of PMT discriminated signals (LVDS) for the EW wall||
|`cryo2_w_conn_0` | text |64-bit word with the status of the pairs of PMT discriminated signals (LVDS) for the WE wall||
|`cryo2_w_conn_2` | text |64-bit word with the status of the pairs of PMT discriminated signals (LVDS) for the WW wall||
|`cryo1_east_counts` | integer | Counters of other activity in coincidence with the gate (other potential global triggers in the event) for the East cryostat ||
|`cryo2_west_count`  | integer | Counters of other activity in coincidence with the gate (other potential global triggers in the event) for the Wast cryostat ||
|`mj_adder_source_east` | integer | Enumeration of trigger source in the East cryostat, specifically adder vs. majority (1: adders, 2: majority, 7: both) | `-1` |
|`mj_adder_source_west` | integer | - Enumeration of trigger source in the West cryostat, specifically adder vs. majority (1: adders, 2: majority, 7: both) | `-1` |
|`flag_east`  | integer || `-1` |
|`delay_east` | integer || `-1` |
|`flag_west`  | integer || `-1` |
|`delay_west` | integer || `-1` |

## Credits
This repository builds upon work from [https://github.com/justinjmueller/icarus_runinfo_database](https://github.com/justinjmueller/icarus_runinfo_database) created by [Justin Mueller](https://github.com/justinjmueller).
A few changes have been made to interface with the 'official' PostgreSQL database, but the original idea and logic behind the scripts belongs to Justin Mueller.
