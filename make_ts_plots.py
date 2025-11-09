# Create timeseries plots to detect suspect FMC data
# Given input data dictionary, formatted pickle, output a series of png files to a directory. Plots are broken into "periods" to allow for flagging bad stretches with buffer. Default is 72 hour periods


import pandas as pd
import os.path as osp
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import transforms
import sys
from utils import plot_one, time_range

def ts_plot(ml_data, st, ts, pi, t0, t1, batch, outfile):
    plot_one(ml_data, st, start_time = t0, end_time = t1, title2 = f"Periods {batch}", 
                         save_path = None, show=True)
    for p, t in zip(pi, ts):
        if np.isnan(p): continue
        plt.axvline(x=t, color='black', linestyle='dotted')
        plt.text(t, plt.ylim()[1], str(p), verticalalignment='top', horizontalalignment="right", color='black')  # Annotate

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print(f"Invalid arguments. {len(sys.argv)} was given but 4 expected")
        print(('Usage: %s <fmda_data> <output_dir>' % sys.argv[0]))
        print("Example: python src/make_ts_plots.py data/ml_data.pkl ts_plots/TEST/")
        sys.exit(-1)

    # Use args to set up data and paths
    ml_data = pd.read_pickle(osp.join(sys.argv[1]))
    out_dir = osp.join(sys.argv[2])
    os.makedirs(out_dir, exist_ok=True)

    n_periods = 5 # number of periods per png plot file
    n_hours = 72 # hours in a period
    for st in ml_data:

        d = ml_data[st]['data']
        max_period = d.st_period.max()
        for start in range(0, max_period + 1, n_periods):
            batch = list(range(start, min(start + n_periods, max_period + 1)))
            ts = [d[d['st_period'].isin([bi])].date_time.min() for bi in batch]
            if np.all(pd.isna(ts)): continue
            pi = [d[d['st_period'].isin([bi])].st_period.min() for bi in batch]
            t0 = d[d['st_period'].isin(batch)].date_time.min()
            t1 = d[d['st_period'].isin(batch)].date_time.max()
            print("~"*50)
            print(f"Running batch for station {st}")
            print(f"Start time: {t0}")
            print(f"End time: {t1}")
            # Check for axis breaks
            ## Some gaps between plotting periods are many months apart, 
            ## resulting plot is unreadable. Split if possible
            times = np.array(ts)[~pd.isna(ts)]
            thresh = pd.Timedelta(days=90)
            if np.any(pd.to_datetime(times).diff()[1:] > thresh):
                for t, p0, bb in zip(ts, pi, batch):
                    if pd.isna(t): continue
                    out_file = osp.join(out_dir, f"{st}_{bb}_{bb}.png")
                    ts_plot(ml_data, st, [t], [p0], t, t+pd.Timedelta(hours=72), [bb], out_file)
                    plt.savefig(out_file)
                    plt.close()
            else:
                out_file = osp.join(out_dir, f"{st}_{batch[0]}_{batch[-1]}.png")
                ts_plot(ml_data, st, ts, pi, t0, t1, batch, out_file)

 
            for p, t in zip(pi, ts):
                if np.isnan(p): continue
                plt.axvline(x=t, color='black', linestyle='dotted')
                plt.text(t, plt.ylim()[1], str(p), verticalalignment='top', horizontalalignment="right", color='black')  # Annotate
            plt.savefig(out_file)
            plt.close()






    
