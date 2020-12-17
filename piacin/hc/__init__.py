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

if hasattr(sys, "pypy_translation_info"):
	import pypyjit

logging.basicConfig(level=logging.INFO)

root = logging.getLogger()
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('# %(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

class PiacinHC(Piacin):
	def __init__(self):
		super(PiacinHC, self).__init__()

		self.bag_location = os.path.join(expanduser("~"), ".piacin")
		
		py_file = os.path.split(os.path.abspath(sys.modules['__main__'].__file__))[-1]
		py_name = os.path.splitext(py_file)[0]
		self.bag_file = os.path.join(self.bag_location, "piacin_hc_bag_%s.pkl" % (py_name))

		self.state = 0

		self.previous_solution = None
		self.anchor_solution = None
		self.neighbours = []
		self.neighbour_pos = 0

	def start(self):
		logging.info("START")
		self.previous_solution = self.current_solution
		self.remaining_evaluations -= 1
		self.state  = 2
		return

	def move(self):
		logging.info("MOVING")
		best_improvement = 0.0
		moved = False
		
		current_fitness = self.previous_solution.fitness
		best_fitness = self.best_solution.fitness
		
		for solution in self.neighbours:
			improvement = current_fitness - solution.fitness # minimise!
			if improvement > best_improvement:
				self.current_solution = solution
				best_improvement = improvement
				moved = True

				if solution.fitness < best_fitness: # minimise!
					self.best_solution = solution
		
		if not moved and self.remaining_evaluations > 0:
			self.current_solution = self.generate_random()
			logging.info("Random Restart: %s" % (str(self.current_solution)))
			self.previous_solution = self.current_solution
			self.remaining_evaluations -= 1
			self.state = 2
			return
		else:
			logging.info("Moving to: %s (%f)" % (str(self.current_solution), self.current_solution.fitness))
			self.previous_solution = self.current_solution
			self.generate()

	def generate(self):
		logging.info("GENERATE")
		self.neighbours = neighbourgen.generate_neighbours(self.current_solution, self.previous_solution)
		self.neighbour_pos = 0
		self.evaluate()

	def evaluate(self):
		logging.info("EVALUATING %d/%d" % (self.neighbour_pos + 1, len(self.neighbours)))
		self.current_solution = self.neighbours[self.neighbour_pos]
		self.neighbour_pos += 1
		self.remaining_evaluations -= 1

		if self.neighbour_pos == len(self.neighbours):
			self.state = 1
		else:
			self.state = 3
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

		if self.state == 0:
			self.start()
		elif self.state == 1:
			self.move()
		elif self.state == 2:
			self.generate()
		elif self.state == 3:
			self.evaluate()
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
	piacin = PiacinHC()
	params = piacin.get_next_input()

	pypyjit.set_param(threshold=int(params["threshold_ratio"] * params["function_threshold"]), function_threshold = params["function_threshold"], trace_eagerness = params["trace_eagerness"], decay = params["decay"], disable_unrolling = params["disable_unrolling"], max_retrace_guards = params["max_retrace_guards"])
	atexit.register(save_state, piacin)

	timestamp = time.time()