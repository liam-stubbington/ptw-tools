'''
@author:    Liam Stubbington 
            RT Physicist, Cambridge University Hospitals NHS Foundation Trust
            
version: 1.0
'''



import os
from glob import glob
from mpc.ptw_mpc import MPCPTWXml
from datetime import datetime
import time

PATH = "./mpc/data/"
EXT = "*.csv"



all_csv_files = [f
                 for path, subdir, files in os.walk(PATH)
                 for f in glob(os.path.normpath(
                     os.path.join(path, EXT)))
                     ]

# datetime(year, month, day, hour, minute, second, microsecond)
dt = datetime(
    year=2022,
    month=11,
    day=16,
)

# -- TO DO --
# Identify MPC files with a datestamp >=midnight today 
nw = datetime.now()
midnight_today = datetime(
    year=nw.year, 
    month=nw.month,
    day=nw.day
)

files_to_process = [
    MPCPTWXml(mpc_csv).export_to_PTW() 
    for mpc_csv in all_csv_files
    if MPCPTWXml(mpc_csv).check_acquisition_date_greater_than(dt)
]

# -- TO DO -- 
# e-mail or log summary of success failures 
fails = [f for f in files_to_process if f != 0]
message = "\n".join(
    [
        f"Nightly MPC --> TRACK-IT log for {dt}",
        f"New MPC Files found: {len(files_to_process)}",
        f"Number of failures: {len(fails)}",
        "\n"
    ]
)

print(message)
time.sleep(5)
    


