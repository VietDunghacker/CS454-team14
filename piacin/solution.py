class Solution(dict):
	def __init__(self, **kwargs):
		super(Solution, self).__init__()
		if "base" in kwargs.keys():
			base = kwargs.pop("base")
			for key, value in base.items():
				self[key] = value
		
		self.evaluated = False
		self.fitness = 0

		for key, value in kwargs.items():
			self[key] = value
		return

	def reify(self):
		if self["threshold_ratio"] < 0.01:
			self["threshold_ratio"] = 0.99
		elif self["threshold_ratio"] > 0.99:
			self["threshold_ratio"] = 0.01

		if self["function_threshold"] < 100:
			self["function_threshold"] = 4900
		elif self["function_threshold"] > 5000:
			self["function_threshold"] = 100

		if self["trace_eagerness"] < 1:
			self["trace_eagerness"] = 1000
		elif self["trace_eagerness"] > 1000:
			self["trace_eagerness"] = 1

		if self["decay"] < 1:
			self["decay"] = 1000
		elif self["decay"] > 1000:
			self["decay"] = 1

		if self["disable_unrolling"] < 1:
			self["disable_unrolling"] = 1000
		elif self["disable_unrolling"] > 1000:
			self["disable_unrolling"] = 1

		if self["max_retrace_guards"] < 1:
			self["max_retrace_guards"] = 100
		elif self["max_retrace_guards"] > 100:
			self["max_retrace_guards"] = 1

	def __str__(self):
		s = []
		for key, value in self.items():
			s.append("%s:%s" % (str(key), str(value)))
		s.append("evaluated:%d" % (self.evaluated))
		s.append("fitness:%f" % (self.fitness))
		return " ".join(s)