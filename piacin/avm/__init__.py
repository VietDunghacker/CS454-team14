from ..piacin import Piacin
from ..solution import Solution
from ..fitness import fitness
from os.path import expanduser
import neighbourgen as ngen
import math
import sys
import time
import pypyjit
import os
import logging
import errno
import pickle
import atexit

logging.basicConfig(level=logging.INFO)

class PiacinAVM(Piacin):
	
	START = 0
	EXPLORE = 1
	EVALUATE_MOVES = 2
	ACCELERATE = 3
	TURN = 4
	OVERSHOOT = 5

	def __init__(self):
		super(PiacinAVM, self).__init__()

		self.bag_location = os.path.join(expanduser("~"), ".piacin")
		self.bag_file = os.path.join(self.bag_location, "avmbag")
		
		self.state = self.START

		self.moves = None
		self.solutions = None
		self.move_pos = 0
		
		self.previous_solution = None
		self.current_key = None
		self.direction = None
		self.step = 1

		self.previous_solution = None

	def start(self):
		logging.info("START")
		self.state  = self.EXPLORE
		return

	def explore_move(self):
		logging.info("EXPLORE")
		print "base", self.current_solution.fitness
		
		self.moves = neighbourgen.explore_move(self.current_solution)
		self.solutions = [ngen.apply_move(self.current_solution, m) for m in self.moves]
		self.state = self.EVALUATE_MOVES
		
		self.move_pos = 0
		self.previous_solution = self.current_solution
		self.evaluate_moves()

	def evaluate_moves(self):
		logging.info("EVALUATING %d/%dth MOVE" % (self.move_pos + 1, len(self.moves)))
		print self.moves[self.move_pos]
		self.current_solution = self.solutions[self.move_pos]
		self.move_pos += 1
		if self.move_pos == len(self.moves):
			self.state = self.TURN
		else:
			self.state = self.EVALUATE_MOVES

	def turn(self):
		logging.info("TURN")
		print "base", self.previous_solution.fitness
		best_improvement = 0.0
		decided = False
		current_fitness = self.previous_solution.fitness
		best_fitness = self.best_solution.fitness

		print [s.fitness for s in self.solutions]

		for (move, solution) in zip(self.moves, self.solutions):	
			improvement = current_fitness - solution.fitness
			if improvement > best_improvement:
				best_improvement = improvement
				self.direction = move
				print "improvement", self.direction
				decided = True

				if solution.fitness > best_fitness:
					self.best_solution = solution

		if not decided and self.remaining_evaluations > 0:
			logging.info("Random Restart")
			self.current_solution = self.generate_random()
			return
		else:
			print "chosen direction", self.direction
			self.accelerate()

	def accelerate(self):
		logging.info("ACCELERATING")
		self.direction = ngen.double_move(self.direction)
		print self.direction
		self.previous_solution = self.current_solution
		self.current_solution = ngen.apply_move(self.current_solution, self.direction)
		self.state = self.OVERSHOOT
		return

	def check_overshoot(self):
		logging.info("CHECKING OVERSHOOT")
		print "current", self.current_solution.fitness
		print "prev", self.previous_solution.fitness
		if self.current_solution.fitness < self.previous_solution.fitness:
			logging.info("NO - KEEP ACCELERATING")
			self.accelerate()
		else:
			logging.info("YES - EXPLORE AGAIN")
			self.current_solution = self.previous_solution
			self.explore_move()

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
			logging.warning("packing a new instance of PiacinAVM")
			self.pack()
		
		if self.remaining_evaluations == 0:
			logging.info("No Budget: bailing out with best known solution")
			return self.best_solution

		if self.state == self.START:
			self.start()
		elif self.state == self.EXPLORE:
			self.explore_move()
		elif self.state == self.EVALUATE_MOVES:
			self.evaluate_moves()
		elif self.state == self.ACCELERATE:
			self.accelerate()
		elif self.state == self.TURN:
			self.turn()
		elif self.state == self.OVERSHOOT:
			self.check_overshoot()
		else:
			return self.best_solution

		return self.current_solution

	def pack(self):
		pickle.dump(self.__dict__, open(self.bag_file, "wb"))
		return

	def unpack(self):
		temp_dict = pickle.load(open(self.bag_file, "rb"))
		self.__dict__.update(temp_dict)
		return

def save_state(piacin):
	global timestamp
	# fitness = math.sqrt(math.pow(piacin.current_solution["function_threshold"] - 1000, 2) + math.pow(piacin.current_solution["trace_eagerness"] - 50, 2))
	fitness = time.time() - timestamp # fitness is elapsed time
	piacin.current_solution.evaluated = True
	piacin.current_solution.fitness = fitness
	print piacin.current_solution
	piacin.pack()

if hasattr(sys, "pypy_translation_info"):
	piacin = PiacinAVM()
	params = piacin.get_next_input()

	pypyjit.set_param(threshold=int(params["threshold_ratio"] * params["function_threshold"]), function_threshold = params["function_threshold"], trace_eagerness=params["trace_eagerness"])
	atexit.register(save_state, piacin)

	timestamp = time.time()




