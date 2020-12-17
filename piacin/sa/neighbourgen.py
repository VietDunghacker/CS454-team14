from ..solution import Solution
import random

def generate_neighbours(solution, past_sol):
	neighbours = []
	for key in solution.keys():
		new_sol = Solution(base=solution)
		new_sol[key] = increase(solution, key)
		new_sol.reify()
		if not new_sol in past_sol:
			neighbours.append(new_sol)
		new_sol = Solution(base=solution)
		new_sol[key] = decrease(solution, key)
		new_sol.reify()
		if not new_sol in past_sol:
			neighbours.append(new_sol)
	return random.choice(neighbours)

def increase(solution, key):
	if key == "trace_eagerness":
		return solution["trace_eagerness"] + 10
	elif key == "threshold_ratio":
		return solution["threshold_ratio"] + 0.05
	elif key == "function_threshold":
		return solution["function_threshold"] + 20
	elif key == "decay":
		return solution["decay"] + 10
	elif key == "disable_unrolling":
		return solution["disable_unrolling"] + 10
	elif key == "max_retrace_guards":
		return solution["max_retrace_guards"] + 5
	else:
		print(key)
		raise KeyError

def decrease(solution, key):
	if key == "trace_eagerness":
		return solution["trace_eagerness"] - 10
	elif key == "threshold_ratio":
		return solution["threshold_ratio"] - 0.05
	elif key == "function_threshold":
		return solution["function_threshold"] - 20
	elif key == "decay":
		return solution["decay"] - 10
	elif key == "disable_unrolling":
		return solution["disable_unrolling"] - 10
	elif key == "max_retrace_guards":
		return solution["max_retrace_guards"] - 5
	else:
		print(key)
		raise KeyError
		