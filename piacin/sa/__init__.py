from ..piacin import Piacin
from ..solution import Solution
from ..fitness import fitness
from os.path import expanduser
from . import neighbourgen
import math
import os
import sys
import time
import logging
import errno
import pickle
import atexit
import random

if hasattr(sys, "pypy_translation_info"):
	import pypyjit

logging.basicConfig(level=logging.INFO)

root = logging.getLogger()
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('# %(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

class PiacinSA(Piacin):
	START = 0
	MOVE = 1
	GENERATE = 2

	def __init__(self):
		super(PiacinSA, self).__init__()

		self.bag_location = os.path.join(expanduser("~"), ".piacin")
		
		py_file = os.path.split(os.path.abspath(sys.modules['__main__'].__file__))[-1]
		py_name = os.path.splitext(py_file)[0]
		self.bag_file = os.path.join(self.bag_location, "piacin_hc_bag_%s.pkl" % (py_name))

		self.state = self.START
		self.temperature = 1
		self.alpha = 0.02

		self.previous_solution = None
		self.neighbour = []

	def start(self):
		logging.info("START")
		self.previous_solution = self.current_solution
		self.remaining_evaluations -= 1
		self.previous_neighbor = []
		self.state = self.GENERATE
		return

	def move(self):
		logging.info("MOVING")
		moved = False
		
		current_fitness = self.previous_solution.fitness
		best_fitness = self.best_solution.fitness
		neighbour_fitness = self.neighbour.fitness

		if neighbour_fitness < current_fitness:
			moved = True
			if neighbour_fitness < best_fitness: # minimise!
				self.best_solution = self.neighbour
		elif self.temperature >= self.alpha:
			rand_number = random.random()
			if rand_number <= math.exp((current_fitness - neighbour_fitness) / self.temperature):
				moved = True

		self.temperature -= self.alpha
				
		if not moved and self.remaining_evaluations > 0:
			if len(self.previous_neighbor) >= 6:
				self.current_solution = self.generate_random()
				self.previous_solution = self.current_solution
				logging.info("Random Restart: %s" % (str(self.current_solution)))
				self.previous_neighbor = []
				self.state = self.GENERATE
				self.remaining_evaluations -= 1
				return
			else:
				logging.info("Retrying another neighbour")
				self.previous_neighbor.append(self.neighbour)
				self.state = self.GENERATE
				self.generate()
		else:
			self.previous_solution = self.current_solution
			self.current_solution = self.neighbour
			logging.info("Moving to: %s (%f)" % (str(self.current_solution), self.current_solution.fitness))
			self.previous_neighbor = [self.current_solution]
			self.generate()

	def generate(self):
		logging.info("GENERATE")
		self.neighbour = neighbourgen.generate_neighbours(self.current_solution, self.previous_neighbor)
		self.evaluate()

	def evaluate(self):
		logging.info("EVALUATING")
		self.current_solution = self.neighbour
		self.remaining_evaluations -= 1

		self.state = self.MOVE
		return

	def get_next_input(self):
		try:
			self.unpack()
		except IOError:
			try:
				os.makedirs(self.bag_location)
			except OSError as exc:
				if exc.errno == errno.EEXIST and os.path.isdir(self.bag_location):
					pass
				else: 
					raise
			logging.warning("packing a new instance of PiacinHC")
			self.pack()
		
		if self.remaining_evaluations <= 0:
			logging.info("No Budget: bailing out with best known solution")
			return self.best_solution

		if self.state == self.START:
			self.start()
		elif self.state == self.MOVE:
			self.move()
		elif self.state == self.GENERATE:
			self.generate()
		else:
			return self.best_solution

		logging.info("GetNextInput returning: %s" % (str(self.current_solution)))
		return self.current_solution

	def pack(self):
		pickle.dump(self.__dict__, open(self.bag_file, "wb"))
		return

	def unpack(self):
		try:
			temp_dict = pickle.load(open(self.bag_file, "rb"))
		except IOError:
			try:
				os.makedirs(self.bag_location)
			except OSError as exc:
				if exc.errno == errno.EEXIST and os.path.isdir(self.bag_location):
					pass
				else:
					raise
			self.pack()
			return
		self.__dict__.update(temp_dict)
		return

def save_state(piacin):
	global timestamp	
	# fitness = math.sqrt(math.pow(piacin.current_solution["function_threshold"] - 1000, 2) + math.pow(piacin.current_solution["trace_eagerness"] - 50, 2))
	fitness = time.time() - timestamp # fitness is elapsed time
	piacin.current_solution.evaluated = True
	piacin.current_solution.fitness = fitness
	logging.info("Current Solution: %s" %(str(piacin.current_solution)))
	piacin.pack()

if hasattr(sys, "pypy_translation_info"):
	piacin = PiacinSA()
	params = piacin.get_next_input()

	pypyjit.set_param(threshold=int(params["threshold_ratio"] * params["function_threshold"]), function_threshold = params["function_threshold"], trace_eagerness = params["trace_eagerness"], decay = params["decay"], disable_unrolling = params["disable_unrolling"], max_retrace_guards = params["max_retrace_guards"])
	atexit.register(save_state, piacin)

	timestamp = time.time()