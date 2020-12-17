from random import randint, random
from .solution import Solution

class Piacin(object):
	def __init__(self):
		self.remaining_evaluations = 80
		# start with random parameter set
		# self.current_solution = self.generate_random()

		# start with default parameter set
		self.current_solution = Solution(function_threshold = 1619, trace_eagerness = 200, threshold_ratio = 0.6418,
			decay = 40, disable_unrolling = 200, max_retrace_guards = 15)

		self.best_solution = self.current_solution
		self.next_solution = self.current_solution

	def generate_random(self):
		return Solution(function_threshold=randint(100, 5000), trace_eagerness=randint(1,1000), threshold_ratio=random(), 
			decay = randint(1, 1000), disable_unrolling = randint(1, 1000), max_retrace_guards = randint(1, 100))