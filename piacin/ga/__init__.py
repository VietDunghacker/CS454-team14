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

class PiacinGA(Piacin):
	START = 0
	OFFSPRING = 1
	INITIAL_EVALUATION = 2
	EVALUATION = 3
	EVOLUTION = 4

	def __init__(self):
		super(PiacinGA, self).__init__()

		self.bag_location = os.path.join(expanduser("~"), ".piacin")
		
		py_file = os.path.split(os.path.abspath(sys.modules['__main__'].__file__))[-1]
		py_name = os.path.splitext(py_file)[0]
		self.bag_file = os.path.join(self.bag_location, "piacin_hc_bag_%s.pkl" % (py_name))

		self.best_solution.fitness = float('inf')
		self.state = self.START
		#self.remaining_evaluations = 80
		self.population = []
		self.offspring = []
		self.num_population = 10

	def start(self):
		logging.info("START")
		self.population.append(self.current_solution)
		for i in range(self.num_population - 1):
			self.population.append(self.generate_random())
		self.state = self.INITIAL_EVALUATION
		self.population_pos = 0
		self.evaluate_initial_population()

	def generate_offspring(self):
		logging.info("GENERATING OFFSPRING")
		self.offspring = []
		while len(self.offspring) < self.num_population:
			parent1, parent2 = self.selection(self.population)
			child1, child2 = self.crossover(parent1, parent2)
			child1 = self.mutation(child1)
			child2 = self.mutation(child2)

			self.offspring.append(child1)
			self.offspring.append(child2)

		self.offspring_pos = 0
		self.evaluate_offspring()

	def selection(self, population):
		subset = random.sample(population, 3)
		subset = sorted(subset, key = lambda x: x.fitness)
		return subset[0], subset[1]

	def crossover(self, parent1, parent2):
		child1 = Solution(base = parent1)
		child2 = Solution(base = parent2)
		cut = random.randint(1, len(parent1.keys()) - 1)
		for i, key in enumerate(parent1.keys()):
			if i >= cut:
				child1[key] = parent2[key]
				child2[key] = parent1[key]
		return child1, child2

	def mutation(self, solution):
		for key in ['threshold_ratio', 'function_threshold', 'trace_eagerness', 'decay', 'disable_unrolling', 'max_retrace_guards']:
			if random.random() < 1.0 / 6:
				solution[key] = self.mutate_key(key)
		return solution

	def mutate_key(self, key):
		if key == 'threshold_ratio':
			return random.random()
		elif key == 'function_threshold':
			return random.randint(100, 5000)
		elif key == 'trace_eagerness':
			return random.randint(1, 1000)
		elif key == 'decay':
			return random.randint(1, 1000)
		elif key == 'disable_unrolling':
			return random.randint(1, 1000)	
		elif key == 'max_retrace_guards':
			return random.randint(1, 100)
		else:
			raise Exception("No such key")

	def evolution(self):
		logging.info("EVOLUTION")
		self.population.extend(self.offspring)
		sorted_population = sorted(self.population, key = lambda x: x.fitness)
		self.population = sorted_population[ : self.num_population]
		self.state = self.OFFSPRING
		if self.population[0].fitness < self.best_solution.fitness:
			self.best_solution = Solution(base = self.population[0])
			self.best_solution.evaluated = 1
			self.best_solution.fitness = self.population[0].fitness
		self.generate_offspring()

	def evaluate_initial_population(self):
		logging.info("EVALUATING INITIAL POPULATION {}/{}".format(self.population_pos + 1, self.num_population))
		self.current_solution = self.population[self.population_pos]
		self.population_pos += 1
		self.remaining_evaluations -= 1

		if self.population_pos == self.num_population:
			self.state = self.OFFSPRING
		else:
			self.state = self.INITIAL_EVALUATION
		return

	def evaluate_offspring(self):
		logging.info("EVALUATING OFFSPRING {}/{}".format(self.offspring_pos + 1, self.num_population))
		self.current_solution = self.offspring[self.offspring_pos]
		self.offspring_pos += 1
		self.remaining_evaluations -= 1

		if self.offspring_pos == self.num_population:
			self.state = self.EVOLUTION
		else:
			self.state = self.EVALUATION
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
		elif self.state == self.OFFSPRING:
			self.generate_offspring()
		elif self.state == self.INITIAL_EVALUATION:
			self.evaluate_initial_population()
		elif self.state == self.EVALUATION:
			self.evaluate_offspring()
		elif self.state == self.EVOLUTION:
			self.evolution()
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
	piacin = PiacinGA()
	params = piacin.get_next_input()

	pypyjit.set_param(threshold=int(params["threshold_ratio"] * params["function_threshold"]), function_threshold = params["function_threshold"], trace_eagerness = params["trace_eagerness"], decay = params["decay"], disable_unrolling = params["disable_unrolling"], max_retrace_guards = params["max_retrace_guards"])
	atexit.register(save_state, piacin)

	timestamp = time.time()