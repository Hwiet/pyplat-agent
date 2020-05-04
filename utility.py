def reward(row, col):
	if self.move_grid[row][col] == 8:
			return 100
	elif self.move_grid[row][col] == 9:
			return 500
	elif self.move_grid[row][col] == 10:
			return 1000
	return 0


def enemy_path_cost(enemy, row, col):
	"""Return how many cells the enemy will travel before reaching a cell."""
	if enemy.gridR == row and enemy.gridC == col:
		return 0
	if is_enemy_coming(row, col):
		return abs(enemy.gridC - col)
	else:
		if enemy.isGoingLeft
			return enemy.gridC + col
		else:
			return (COL_COUNT - enemy.gridC) + (COL_COUNT - col)


def utility(node):
	