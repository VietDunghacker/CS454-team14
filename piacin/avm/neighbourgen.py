from ..solution import Solution

INCREASE = 1
DECREASE = 0

def explore_move(solution):
	"""
	Generate a list of explorative moves. A move is a tuple of (key, distance).
	"""
	moves = []
	for key in solution.keys():
		if key == "trace_eagerness":
			moves.append((key, 5))
			moves.append((key, -5))
		elif key == "threshold_ratio":
			moves.append((key, 0.05))
			moves.append((key, -0.05))
		elif key == "function_threshold":
			moves.append((key, 10))
			moves.append((key, -10))
		else:
			raise KeyError
	return moves

def apply_move(solution, move):
	new_sol = Solution(base = solution)
	(key, distance) = move
	new_sol[key] = solution[key] + distance
	new_sol.reify()
	return new_sol

def double_move(move):
	return (move[0], move[1] * 2)

def halve_move(move):
	return (move[0], move[1] / 2)