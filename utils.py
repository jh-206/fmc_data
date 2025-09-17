import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

plot_styles = {
    'fm': {'color': '#468a29', 'linestyle': '-', 'label': 'Observed FMC'},
    'fm_preds': {'color': '#468a29', 'linestyle': '-', 'label': 'Observed FMC'},
    'Ed': {'color': '#EF847C', 'linestyle': '--', 'alpha':.8, 'label': 'drying EQ'},
    'Ew': {'color': '#7CCCEF', 'linestyle': '--', 'alpha':.8, 'label': 'wetting EQ'},
    'rain': {'color': 'b', 'linestyle': '-', 'alpha':.9, 'label': 'Rain'},
    'model': {'color': 'k', 'linestyle': '-', 'label': 'Predicted FMC'}
}

def plot_one(d, st, features=True, m=None, start_time="2024-01-01", end_time = "2024-01-07", title2 = "", save_path = None, show=True):
	"""
	Plot univariate timeseries for formatted dictionary, one station key from output of build_ml_data
	"""
	import pandas as pd

	if type(start_time) is str:
		start_time = pd.Timestamp(start_time, tz="UTC")
		end_time = pd.Timestamp(end_time, tz="UTC")

	title = f"Observed FMC at RAWS {st}"
	if title2:
		title = title + " - " + title2

	timestamps = d[st]["times"]
	inds = np.where((timestamps >= start_time) & (timestamps <= end_time))[0]
	fm = d[st]["data"]["fm"].to_numpy()[inds]
	x = d[st]["times"][inds]
	# insert NA for time gaps instead of connecting with line as default behavior
	thr = pd.Timedelta(hours=1)   
	dt = pd.Series(x).diff()
	fm[dt > pd.Timedelta(hours=1)] = np.nan

	plt.plot(x, fm, **plot_styles['fm'])
	if features:
		Ed = d[st]["data"]["Ed"].to_numpy()[inds]
		Ed[dt > pd.Timedelta(hours=1)] = np.nan
		Ew = d[st]["data"]["Ew"].to_numpy()[inds]
		Ew[dt > pd.Timedelta(hours=1)] = np.nan
		rain = d[st]["data"]["rain"].to_numpy()[inds]
		rain[dt > pd.Timedelta(hours=1)] = np.nan
		plt.plot(x, Ed, **plot_styles['Ed'])
		plt.plot(x, Ew, **plot_styles['Ew'])
		plt.plot(x, rain, **plot_styles['rain'])
	if m is not None:
		plt.plot(x, m, **plot_styles['model'])
	plt.legend(loc='upper left', bbox_to_anchor=(1, 0.5))
	plt.xlabel("Hour")
	plt.ylabel("FMC (%)")
	plt.title(title)
	plt.xticks(rotation=90)
	plt.grid()
	plt.tight_layout()

	# Save plot if path provided
	if save_path is not None:
		plt.savefig(save_path)

	# Show plot unless False
	if not show:
		plt.close()


def time_range(start, end, freq="1h"):
	"""
	Wrapper function for pandas date range. Checks to allow for input of datetimes or strings
	"""
	if (type(start) is str) and (type(end) is str):
		start = str2time(start)
		end = str2time(end)
	else:
		assert isinstance(start, datetime) and isinstance(end, datetime), "Args start and end must be both strings or both datetimes"

	times = pd.date_range(start, end, freq=freq)
	times = times.to_pydatetime()
	return times
