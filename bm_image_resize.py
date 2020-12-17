import argparse
import time
import os
from PIL import Image


def block():
	for file in os.listdir('./image/'):
		path = os.path.join('./image/', file)
		image = Image.open(path)
		image = image.resize((360, 270), resample = Image.LANCZOS)

def test_tokenize(count):
	times = []
	for i in range(count):
		t0 = time.time()
		block()
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

	print(test_tokenize(args.bmnumber))