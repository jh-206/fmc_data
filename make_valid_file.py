# Given manually created spreadsheet of valid/invalid data,
# create formatted csv to be used to manually remove bad data

import pandas as pd
import sys
import os.path as osp
import re
import numpy as np

if __name__ == '__main__':

    if len(sys.argv) != 4:
        print(f"Invalid arguments. {len(sys.argv)} was given but 4 expected")
        print(('Usage: %s <fmda_data> <manual_file> <output_file>' % sys.argv[0]))
        print("Example: python src/make_valid_file.py ml_data.pkl fmc_valid_checks_rocky24.csv fmc_valid_rocky24.csv")
        sys.exit(-1)

    
    # Use args to set up data and paths
    ml_data = pd.read_pickle(osp.join(sys.argv[1]))
    df = pd.read_csv(osp.join(sys.argv[2]))
    output_file = osp.join(sys.argv[3])
    
    # Set up restructured dataframe
    df_valid = pd.DataFrame(columns=['stid', 'start', 'end', 'valid']).astype({
        'stid': 'string',
        'start': 'string',
        'end': 'string',
        'valid': 'int'
    })
    
    pattern = r"^(\d+)(?:\s*,\s*(\d+))?$" # Use to extract period integers start_period, end_period e.g. (0, 243)
    for i in range(0, df.shape[0]):
        st = df.stid[i]
        d = ml_data[st]["data"]
        stringi = df[df.index == i].periods.values[0]
        valid_i = df[df.index == i].valid.values[0]
        pstart, pend = re.match(pattern, stringi).groups()
        # Handle whether single period or range
        if pend is None:
            periods = [int(pstart)]
        else:
            periods = np.arange(int(pstart), int(pend)+1, step=1)
        
        t0 = d[d.st_period.isin(periods)].date_time.min() # start time of period range
        t1 = d[d.st_period.isin(periods)].date_time.max() # end time for period range
    
        di = pd.DataFrame({
            'stid': [st],
            'start': [t0.strftime("%Y-%m-%dT%H:%M:%SZ")],
            'end': [t1.strftime("%Y-%m-%dT%H:%M:%SZ")],
            'valid': [valid_i]
        })
        
        df_valid = pd.concat([df_valid, di], ignore_index = True)
    
    assert df_valid.stid.unique().shape[0] == len(ml_data), f"Mismatch number of unique stations, {df_valid.stid.unique().shape} in processed dataframe but {len(ml_data)} in input ml_data"
    # Write output
    print(f"Writing to file: {output_file}")
    df_valid.to_csv(output_file, index=False)

