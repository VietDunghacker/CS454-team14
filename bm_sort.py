import argparse
import re
import time
import os, sys

class Student:
	def __init__(self, idnum):
		self.idnum = idnum
	def __repr__(self):
		return repr((self.idnum))


def sort_prime_array():
	a = []
	b = 2
	prime = 199933
	while len(a) < prime:
		student = Student(b)
		a.append(student)
		b = (b * 2) % prime
	sorted(a, key = lambda x : x.idnum)

def test_sort(count):
	times = []
	for i in range(count):
		t0 = time.time()
		sort_prime_array()
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
		import piacin.sa

	print(test_sort(args.bmnumber))