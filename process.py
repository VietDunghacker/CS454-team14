import pandas as pd
import sys
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, NullLocator, FormatStrFormatter

def process_default_runs(log_prefix):
	index = pd.Series(range(20), name="index")
	df = pd.DataFrame(columns=["index", "time"])
	input_file = "./result/default/{}_00.txt".format(log_prefix)
	times = pd.read_csv(input_file, names=["time"], comment="#")
	# print times
	_new = pd.DataFrame({"index":index, "time":times["time"]})
	df = df.append(_new)
	df.to_csv("%s_concat.csv" % (log_prefix), sep=",", index=False)

def process_piacin_runs(log_prefix, algo):
	index = pd.Series(range(100), name="index")
	df = pd.DataFrame(columns=["index", "time"])
	input_file = "./result/{}/{}_00.txt".format(algo, log_prefix)
	times = pd.read_csv(input_file, names=["time"], comment="#")
	# print times
	_new = pd.DataFrame({"index":index, "time":times["time"]})
	df = df.append(_new)
	df.to_csv("{}_{}_concat.csv".format(log_prefix, algo), sep=",", index=False)


if __name__ == '__main__':
	process_default_runs("log_bm_regex_v8.py_n_20_bm_50_pypy_piacin_0_run")
	process_piacin_runs("log_bm_regex_v8.py_n_100_bm_50_pypy_piacin_1_run", "hc")
	process_piacin_runs("log_bm_regex_v8.py_n_100_bm_50_pypy_piacin_1_run", "sa")
	process_piacin_runs("log_bm_regex_v8.py_n_100_bm_50_pypy_piacin_1_run", "ga")

	process_default_runs("log_bm_nltk_intensifier.py_n_20_bm_50_pypy_piacin_0_run")
	process_piacin_runs("log_bm_nltk_intensifier.py_n_100_bm_50_pypy_piacin_1_run", "hc")
	process_piacin_runs("log_bm_nltk_intensifier.py_n_100_bm_50_pypy_piacin_1_run", "sa")
	process_piacin_runs("log_bm_nltk_intensifier.py_n_100_bm_50_pypy_piacin_1_run", "ga")

	process_default_runs("log_bm_sort.py_n_20_bm_50_pypy_piacin_0_run")
	process_piacin_runs("log_bm_sort.py_n_100_bm_50_pypy_piacin_1_run", "hc")
	process_piacin_runs("log_bm_sort.py_n_100_bm_50_pypy_piacin_1_run", "sa")
	process_piacin_runs("log_bm_sort.py_n_100_bm_50_pypy_piacin_1_run", "ga")

	process_default_runs("log_bm_image_resize.py_n_20_bm_50_pypy_piacin_0_run")
	process_piacin_runs("log_bm_image_resize.py_n_100_bm_50_pypy_piacin_1_run", "hc")
	process_piacin_runs("log_bm_image_resize.py_n_100_bm_50_pypy_piacin_1_run", "sa")
	process_piacin_runs("log_bm_image_resize.py_n_100_bm_50_pypy_piacin_1_run", "ga")

	process_default_runs("log_bm_nonDecInt.py_n_20_bm_50_pypy_piacin_0_run")
	process_piacin_runs("log_bm_nonDecInt.py_n_100_bm_50_pypy_piacin_1_run", "hc")
	process_piacin_runs("log_bm_nonDecInt.py_n_100_bm_50_pypy_piacin_1_run", "sa")
	process_piacin_runs("log_bm_nonDecInt.py_n_100_bm_50_pypy_piacin_1_run", "ga")