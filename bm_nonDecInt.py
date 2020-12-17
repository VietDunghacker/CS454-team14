import argparse
import time
import numpy as np 

def nonDecInt(n) : 
	a = np.zeros((n + 1, 10)) 

	for i in range(10) : 
		a[0][i] = 1

	for i in range(n): 
		a[i + 1][9] = 1

	for i in range(n): 
		for j in range(8, -1, -1): 
			a[i + 1][j] = a[i][j] + a[i + 1][j + 1] 

	return int(a[n][0]) 

def test_nonDecInt(count):
	times = []
	for i in range(count):
		t0 = time.time()
		nonDecInt(1000)
		t1 = time.time()
		times.append(t1 - t0)
	return sum(times)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--piacin', dest='piacin', action='store_const', const=True, default=False, help='Use piacin')
	parser.add_argument('--clear', dest='clear', action='store_const', const=True, default=False, help='Clear piacin bag')
	parser.add_argument("-k", "--bmnumber", type=int, default=100, help="Number of time to repeat benchmark within run (default: 100)")

	args = parser.parse_args()

	if args.piacin:
		import piacin.hc

	print(test_nonDecInt(args.bmnumber))