def generateReferences():

	def cross(vector_a, vector_b):
		return [a + b for a in vector_a for b in vector_b]

	all_rows = 'ABCDEFGHI'
	all_columns = '123456789'

	coordinates = cross(all_rows, all_columns)

	row_units = [cross(row, all_columns) for row in all_rows]

	col_units = [cross(all_rows, col) for col in all_columns]

	box_units = [cross(row_square, col_square) for row_square in ['ABC', 'DEF', 'GHI'] for col_square in ['123', '456', '789']]

	allUnits = row_units + col_units + box_units  # Add units together
	groups = {}

	groups['units'] = {pos: [unit for unit in allUnits if pos in unit] for pos in coordinates}
	groups['peers'] = {pos: set(sum(groups['units'][pos], [])) - {pos} for pos in coordinates}

	return coordinates, groups, allUnits


def parseSudoku(puzzle, digits='123456789', nulls='0.'):
	"""
	Parses a string describing a Sudoku puzzle board into a dictionary with each cell mapped to its relevant
	coordinate, i.e. A1, A2, A3...
	"""

	flat_puzzle = ['.' if char in nulls else char for char in puzzle if char in digits + nulls]

	if len(flat_puzzle) != 81:
		raise ValueError('Invalid sudoku length %s' % len(flat_puzzle))

	coordinates, groups, allUnits = generateReferences()

	return dict(zip(coordinates, flat_puzzle))


def validate(puzzle):
	"""Checks if a completed Sudoku puzzle has a valid sol."""
	if puzzle is None:
		return False

	coordinates, groups, allUnits = generateReferences()
	fullSet = [str(x) for x in range(1, 10)]

	return all([sorted([puzzle[cell] for cell in unit]) == fullSet for unit in allUnits])


def solve(puzzle):
	digits = '123456789'

	coordinates, groups, allUnits = generateReferences()
	in_grid = parseSudoku(puzzle)
	in_grid = {k: v for k, v in in_grid.items() if v != '.'}
	out_grid = {cell: digits for cell in coordinates}
	def confirmValue(grid, pos, val):
                if grid is None:
                        return grid
		remaining_values = grid[pos].replace(val, '')
		for val in remaining_values:
			grid = eliminate(grid, pos, val)
		return grid

	def eliminate(grid, pos, val):
		"""Eliminates `val` as a possibility from all peers of `pos`."""

		if grid is None:
			return None

		if val not in grid[pos]:
			return grid

		grid[pos] = grid[pos].replace(val, '')

		if len(grid[pos]) == 0:
			return None
		elif len(grid[pos]) == 1:
			for peer in groups['peers'][pos]:
				grid = eliminate(grid, peer, grid[pos])
				if grid is None:
					return None


		for unit in groups['units'][pos]:
			possibilities = [p for p in unit if val in grid[p]]

			if len(possibilities) == 0:
				return None
			elif len(possibilities) == 1 and len(grid[possibilities[0]]) > 1:
				if confirmValue(grid, possibilities[0], val) is None:
					return None

		return grid

	for position, value in in_grid.items():
		out_grid = confirmValue(out_grid, position, value)

	if validate(out_grid):
		return out_grid

	def guessDigit(grid):
		"""Guesses a digit from the cell with the fewest unconfirmed possibilities and propagates the constraints."""

		if grid is None:
			return None

		if all([len(possibilities) == 1 for cell, possibilities in grid.items()]):
			return grid

		n, pos = min([(len(possibilities), cell) for cell, possibilities in grid.items() if len(possibilities) > 1])

		for val in grid[pos]:
			sol = guessDigit(confirmValue(grid.copy(), pos, val))
			if sol is not None:
				return sol

	out_grid = guessDigit(out_grid)
        if out_grid is not None:
	        return [out_grid[s] for s in coordinates]
        else:
            return False
