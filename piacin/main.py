import random

class Solution(dict):
	def __init__(self, **kwargs):
		super(Solution, self).__init__()
		if "base" in kwargs.keys():
			base = kwargs.pop("base")
			for key, value in base.iteritems():
				self[key] = value
		
		self.evaluated = False
		self.fitness = 0

		for key, value in kwargs.iteritems():
			self[key] = value
		return

	def reify(self):
		if self["function_threshold"] < 100:
			self["function_threshold"] = 4900
		elif self["function_threshold"] > 5000:
			self["function_threshold"] = 100

		if self["trace_eagerness"] < 1:
			self["trace_eagerness"] = 1000
		elif self["trace_eagerness"] > 1000:
			self["trace_eagerness"] = 1

		if self["threshold_ratio"] < 0.01:
			self["threshold_ratio"] = 0.99
		elif self["threshold_ratio"] > 0.99:
			self["threshold_ratio"] = 0.01

		if self["loop_longevity"] < 100:
			self["loop_longevity"] = 4900
		elif self["loop_longevity"] > 5000:
			self["loop_longevity"] = 100

		if self["disable_unrolling"] < 1:
			self["disable_unrolling"] = 1000
		elif self["disable_unrolling"] > 1000:
			self["disable_unrolling"] = 1

		if self["decay"] < 1:
			self["decay"] = 100
		elif self["decay"] > 100:
			self["decay"] = 1

	def __str__(self):
		s = []
		for key, value in self.iteritems():
			s.append("%s:%s" % (str(key), str(value)))
		s.append("Evaluated: %d" % (self.evaluated))
		s.append("Fitness: %f" % (self.fitness))
		return " ".join(s)

class Piacin(object):
	def __init__(self):
		self.remaining_evaluations = 80
		# self.current_solution = self.generate_random()
		self.current_solution = Solution(function_threshold = 1619, trace_eagerness = 200, threshold_ratio = 0.64, loop_longevity = 1000, disable_unrolling = 200, decay = 40)

		self.best_solution = self.current_solution
		self.next_solution = self.current_solution

	def generate_random(self):
		return Solution(threshold_ratio = random.random(),
			function_threshold = random.randint(100, 5000),
			trace_eagerness = random.randint(1, 1000),
			loop_longevity = random.randint(100, 5000),
			disable_unrolling = random.randint(1, 1000),
			decay = random.randint(1, 100))
