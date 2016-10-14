"""
File: homework.py
---------------
Homework 2
Course: CSCI 561
Name: James Webb
USC ID: jamesweb

An adversarial search suite that implements Minimax with and without
alpha-beta pruning for the Gang War game. See 'gang_war_rules.txt' to see
rules governing game play.

The execution of this script performs a single action on a given an initial 
game state as described by 'input.txt', formatted as follows:

<N>
<MODE>
<YOUPLAY>
<DEPTH>
<... CELL VALUES ...>
<... BOARD VALUES ...>

where:
<N> is the board width and height, e.g. N=5 becomes a 5x5 board.
<MODE> is 'MINIMAX', 'ALPHABETA', or 'COMPETITION' and describes if the
	bot will use the minimax algorithm with or without alpha-beta pruning
	or the experimental optimized algorithm for bot v. bot competitions.
<YOUPLAY> is 'X' or 'O' and describes the player the bot will play as
<DEPTH> is the maximum depth of the search tree. This input is ignored in
	competition mode.
<... CELL VALUES ...> contains N lines each containing N positive integers
	separated by spaces. Each integer represents the value of that board cell.
<... BOARD STATE ...> contains N lines each with N characters 'X', 'O', or '.'
	representing if the cell is owned by X, O, or neither.

After deciding what action to take, the script then writes the result to
'output.txt' in the following format:

<MOVE> <MOVETYPE>
<... NEXT BOARD STATE ...>

where:
<MOVE> is the position of the new occupied cell (e.g. F2) where the letter
	designates the column and the number designates the row.
<MOVETYPE> is either 'Stake' or 'Raid'
<... NEXT BOARD STATE ...> is the resulting board state after the action is
	performed. It is in the same format as the board state from 'input.txt'.

The game playing agents and game representation elements have been
modularized so that they can be applied in different applications such as
human v. human I/O games, human v. bot I/O games, and bot v. bot training
applications.
"""

class Action:
	"""A class for storing a possible in-game action.

	In a game-tree, this class would be equivalent to an edge connecting two
	different board states. However, this class does not store the two
	board state endpoints. This class also does not serve as a transition
	model to change from one board state to another (see the 'transition'
	function of the Board class).

	Attributes:
		piece_position: a tuple representing the cell to be occupied.
			piece_position[0] is the row of the game board, piece_position[1]
			is the column. e.g. C7 -> (6, 2).
		type: a character representing if the move is a Stake ('S') or a Raid
			('R').
		player: a character representing which player is making this move
			(either 'X' or 'O').
	"""
	def __init__(self, piece_position, action_type, player):
		self.piece_position = piece_position
		self.type = action_type
		self.player = player

	def string_position(self):
		letter = chr(self.piece_position[1]+65)
		return '{}{}'.format(letter, self.piece_position[0]+1)

	def __repr__(self):
		if self.type == 'S':
			string_type = 'Stake'
		else:
			string_type = 'Raid'
		return '{} {}'.format(self.string_position(), string_type)

	def simple_str(self):
		return '{} {}'.format(self.string_position(), self.type)

	def __eq__(self, other):
		return self.piece_position == other.piece_position and \
		self.type == other.type and \
		self.player == other.player


class Board:
	"""A class representing the current game state of the board

	Using Board objects, the present state of the game can be stored,
	and additional functionality such as determining possible actions and
	transitioning to new boards using those actions are supported

	Attributes:
		n: an integer [1,26] representing the height and width of the board.
		state: a 2D array where state[i][j] represents the state of the jth
			cell in the ith row of the board (can either be 'X', 'O', or '.').
		values: a 2D of the same format as state, but each value represents
			the value of occupying that cell.
		turn: a character 'X' or 'O' designating which player's turn it is to
			make a move.
		remaining_spaces: an integer representing the number of available
			spaces left on the board. Passed into the board object to avoid
			recalculating each time the terminal test is called.
		scores: a dict mapping a player ('X' or 'O') to their current score.
			Passed into the board object to save recalculation time.
	"""
	def __init__(self, n, state, values, turn, \
		remaining_spaces=None, scores={'X':0, 'O':0}):
		"""Inits a Board with the given game state, board values, and
		current player's turn. If not specified, board assumes new game
		board with n^2 remaining spaces and scores of 0.
		"""
		self.n = n
		self.state = state
		self.values = values
		self.turn = turn
		if turn == 'X':
			self.opponent = 'O'
		else:
			self.opponent = 'X'
		if remaining_spaces or remaining_spaces == 0:
			self.remaining_spaces = remaining_spaces
		else:
			self.remaining_spaces = n**2
		self.scores = scores



	def adjacent_positions(self, row, col):
		"""Returns the neighbors of a cell within the board's boundaries.

		Args:
			row: int representing the row of the current cell.
			col: int representing the column of the current cell.

		Returns:
			A list containing the tuples of the (row, col) of valid
			adjacent cells of the input cell.
		"""
		positions = []
		# south neighbor
		if (row + 1) < self.n:
			positions.append((row+1,col))
		# north neighbor
		if (row - 1) >= 0:
			positions.append((row-1, col))
		# east neighbor
		if (col + 1) < self.n:
			positions.append((row,col+1))
		# west neighbor
		if (col - 1) >= 0:
			positions.append((row, col-1))
		return positions


	def actions(self):
		"""Generates the list of possible actions given the current board.

		Using the turn variable within the board object, identifies all
		possible stake and raid moves that can be made given the current
		board. Does not assess the value of these actions or act as a
		transition model.

		Returns:
			A list of Action objects containing the position of the possible
			action, the type of action (Stake or Raid), and the player taking
			the action, which is equal to the value of the board's turn var.
		"""
		legal_stake_actions = []
		legal_raid_actions = []
		for row in range(self.n):
			for col in range(self.n):
				if self.state[row][col] == '.':
					# if cell is free, Stake is possible
					legal_stake_actions.append(Action((row, col), 'S', \
						self.turn))
					for adjacent in self.adjacent_positions(row, col):
						adj_r, adj_c = adjacent
						# if adjacent cell is owned by current player
						# then Raid is possible
						if self.state[adj_r][adj_c] == self.turn:
							legal_raid_actions.append(Action((row, col), \
								'R', self.turn))

		# Combine Stake and Raid actions into one list
		# Putting all Stakes before Raids is a requirement
		# of the assignment, does not improve performance.

		return legal_stake_actions + legal_raid_actions


	def transition(self, action):
		"""Transitions the board to a resulting board by applying an Action.

		Given an initial board and an action, applies the action to create
		a new board. The new board will reflect the new ownership, scores,
		spaces remaining, as well as toggling the which player has the next
		turn. Assumes the action is legal.

		Args:
			action: An Action object to be applied to the board.

		Returns:
			A Board object reflecting the changes produced by the action.
		"""
		new_state = deepcopy(self.state)
		new_scores = {'X': self.scores['X'], 'O': self.scores['O']}

		i, j = action.piece_position
		new_state[i][j] = self.turn
		new_scores[self.turn] += self.values[i][j]
		if action.type == 'R':
			# Because this is a raid, we must check adjacent squares
			# for opponent pieces to capture
			for position in self.adjacent_positions(i, j):
				row, col = position
				if new_state[row][col] != '.':
					# This square belongs to opponent, so it is captured
					if new_state[row][col] != action.player:
						new_state[row][col] = action.player
						new_scores[self.turn] += self.values[row][col]
						new_scores[self.opponent] -= self.values[row][col]

		return Board(self.n, \
			new_state, \
			self.values, \
			self.opponent, \
			remaining_spaces=self.remaining_spaces - 1, \
			scores=new_scores)
		return new_state


	def terminal(self):
		"""Returns True if game is in an end state
		(i.e. there are no remaining spaces on the board).
		"""
		return self.remaining_spaces == 0

class MinimaxPlayer:
	"""A game-playing AI implementing the vanilla Minimax algorithm.

	This bot serves as a modularized class which performs minimax search
	on a Board object and outputs the highest-valued action possible.

	Attributes:
		my_player: A char ('X' or 'O') this bot is assigned to play as.
		opponent: A char that is whichever char my_player is not.
		max_depth: An integer representing the maximum depth in the
			minimax search tree this bot can observe before cutting-off.
	"""
	def __init__(self, my_player, opponent, max_depth):
		self.my_player = my_player
		self.opponent = opponent
		self.max_depth = max_depth

	def cutoff_test(self, state, curr_depth):
		"""Determines if the bot should stop searching the game tree.

		Args:
			state: A Board object representing the current state in the
				game tree the search is exloring.
			curr_depth: An integer of the current depth the search is
				exploring in the game tree.

		Returns:
			True if the search has reached the maximum depth or if the
			board is in a terminal state. False if neither is true.
		"""
		if curr_depth >= self.max_depth:
			return True
		elif state.terminal():
			return True
		return False

	def evaluation(self, state):
		"""Evaluates the current state of the board by computing the game
			score.

		Args:
			state: a Board object that is the node in the game tree currently
				being explored.

		Returns:
			The bot's player score - its opponent's player score.
		"""
		return state.scores[self.my_player] - state.scores[self.opponent]

	def max_value(self, state, curr_depth):
		"""Performs search on MAX nodes in the game tree.
		
		Given the current state in the game tree, explore all result states
		from all possible actions. Return the maximum value from those result
		states.

		Args:
			state: A Board action representing the MAX node in the game tree.
			curr_depth: An integer of the current depth the search is
				exploring in the game tree.

		Returns:
			The maximum min_value from exploring all possible actions from
			the current state.
		"""
		if self.cutoff_test(state, curr_depth):
			return self.evaluation(state)
		v = float('-Inf')
		for action in state.actions():
			v = max(v, self.min_value(state.transition(action), curr_depth+1))
		return v

	def min_value(self, state, curr_depth):
		"""Performs search on MIN nodes in the game tree.
		
		Given the current state in the game tree, explore all result states
		from all possible actions. Return the miniimum value from those result
		states.

		Args:
			state: A Board object representing the MIN node in the game tree.
			curr_depth: An integer of the current depth the search is
				exploring in the game tree.

		Returns:
			The minimum max_value from exploring all possible actions from
			the current state.
		"""
		if self.cutoff_test(state, curr_depth):
			return self.evaluation(state)
		v = float('Inf')
		for action in state.actions():
			v = min(v, self.max_value(state.transition(action), curr_depth+1))
		return v

	def search(self, state):
		"""Determines the best possible move given the current game board.

		Using Minimax, explores all possible actions from the given board
		and returns the best possible action.

		Args:
			state: A Board object representing the root of the game tree.

		Returns:
			The Action object with the highest value across all actions.
		"""
		best_action = None
		best_value = float('-Inf')
		for action in state.actions():
			v = self.min_value(state.transition(action), 1)
			# Because we consider all Stake moves first it makes sense to
			# use v > best_value, because then even if a Raid action has
			# the same value as a Stake value, we will use the Stake value
			# (as instructed, ties are broken using Stake)
			if v > best_value:
				best_value = v
				best_action = action
		return best_action


class AlphaBetaPlayer:
	"""A game-playing AI implementing the minimax algorithm with a-B pruning.

	This bot serves as a modularized class which performs minimax search
	with alpha-beta prining on a Board object and outputs the highest-valued 
	action possible.

	Attributes:
		my_player: A char ('X' or 'O') this bot is assigned to play as.
		opponent: A char that is whichever char my_player is not.
		max_depth: An integer representing the maximum depth in the
			minimax search tree this bot can observe before cutting-off.
	"""
	def __init__(self, my_player, opponent, max_depth):
		self.my_player = my_player
		self.opponent = opponent
		self.max_depth = max_depth

	def cutoff_test(self, state, curr_depth):
		"""Determines if the bot should stop searching the game tree.

		Args:
			state: A Board object representing the current state in the
				game tree the search is exloring.
			curr_depth: An integer of the current depth the search is
				exploring in the game tree.

		Returns:
			True if the search has reached the maximum depth or if the
			board is in a terminal state. False if neither is true.
		"""
		if curr_depth >= self.max_depth:
			return True
		elif state.terminal():
			return True
		return False

	def evaluation(self, state):
		"""Evaluates the current state of the board by computing the game
			score.

		Args:
			state: a Board object that is the node in the game tree currently
				being explored.

		Returns:
			The bot's player score - its opponent's player score.
		"""
		return state.scores[self.my_player] - state.scores[self.opponent]

	def max_value(self, state, alpha, beta, curr_depth):
		"""Performs search on MAX nodes in the game tree.
		
		Given the current state in the game tree, explore all result states
		from all possible actions. Return the maximum value from those result
		states.

		Args:
			state: A Board action representing the MAX node in the game tree.
			alpha: A number representing the current upperbound on the
				possible backed-up value of this branch.
			beta: A number representing the current lower bound on the
				possible backed-up value of this branch
			curr_depth: An integer of the current depth the search is
				exploring in the game tree.

		Returns:
			The maximum min_value from exploring all possible actions from
			the current state.
		"""
		if self.cutoff_test(state, curr_depth):
			return self.evaluation(state)
		v = float('-Inf')
		for action in state.actions():
			v = max(v, self.min_value(state.transition(action), alpha, beta, curr_depth+1))
			if v >= beta:
				return v
			alpha = max(alpha, v)
		return v

	def min_value(self, state, alpha, beta, curr_depth):
		"""Performs search on MIN nodes in the game tree.
		
		Given the current state in the game tree, explore all result states
		from all possible actions. Return the minimum value from those result
		states.

		Args:
			state: A Board action representing the MAX node in the game tree.
			alpha: A number representing the current upperbound on the
				possible backed-up value of this branch.
			beta: A number representing the current lower bound on the
				possible backed-up value of this branch
			curr_depth: An integer of the current depth the search is
				exploring in the game tree.

		Returns:
			The minimum max_value from exploring all possible actions from
			the current state.
		"""
		if self.cutoff_test(state, curr_depth):
			return self.evaluation(state)
		v = float('Inf')
		for action in state.actions():
			v = min(v, self.max_value(state.transition(action), alpha, beta, curr_depth+1))
			if v <= alpha:
				return v
			beta = min(beta, v)
		return v

	def search(self, state):
		"""Determines the best possible move given the current game board.

		Using Minimax with alpha-beta pruning, explores all possible actions 
		from the given board and returns the best possible action.

		Args:
			state: A Board object representing the root of the game tree.

		Returns:
			The Action object with the highest value across all actions.
		"""
		best_action = None
		best_value = float('-Inf')
		for action in state.actions():
			v = self.min_value(state.transition(action), float('-Inf'), float('Inf'), 1)
			# Because we consider all Stake moves first it makes sense to
			# use v > best_value, because then even if a Raid action has
			# the same value as a Stake value, we will use the Stake value
			# (as instructed, ties are broken using Stake)
			if v > best_value:
				best_value = v
				best_action = action
		return best_action

def generate_player_and_board(filename):
	"""Reads an inpt file to determine the current game state.

	For purposes of the competition, input files are provided to the AI
	describing current information about the board and the search to be
	performed. This info is scanned in and stored in Player and Board objects.

	Args:
		filename: A string of the input file path to be read.

	Returns:
		A tuple containing a Board object representing the inital board
		configuration and a Player determined by the mode of the input.
	"""
	start_state = []
	start_scores = {'X':0, 'O':0}
	values = []
	my_player = ''
	opponent = ''
	max_depth = 0
	n = 0
	with open(filename, 'r') as f:
		lines = f.readlines()
		n = int(lines[0].strip())
		mode = lines[1].strip()
		my_player = lines[2].strip()
		if my_player == 'X':
			opponent = 'O'
		else:
			opponent = 'X'
		if mode == 'COMPETITION':
			cpu_remaining = float(lines[3].strip())
		else:
			max_depth = int(lines[3].strip())
		for i in range(4, n+4):
			values.append([int(x) for x in lines[i].split()])
		for j in range(i+1, n+i+1):
			start_state.append(list(lines[j].strip()))

	remaining_spaces = n**2
	for row in range(n):
		for col in range(n):
			if start_state[row][col] != '.':
				remaining_spaces -= 1
				start_scores[start_state[row][col]] += values[row][col]

	start_board = Board(n, start_state, values, my_player, \
		remaining_spaces=remaining_spaces, scores=start_scores)
	if mode == 'MINIMAX':
		ai = MinimaxPlayer(start_board.turn, start_board.opponent, max_depth)
	elif mode == 'ALPHABETA':
		ai = AlphaBetaPlayer(start_board.turn, start_board.opponent, max_depth)

	return (start_board, ai)



if __name__ == '__main__':
	from copy import deepcopy
	# Read the input file to generate the start board and the player bot
	start_board, ai = generate_player_and_board('input.txt')
	# Use the bot's search to determine the best action to take
	decision = ai.search(start_board)
	# Apply the action to the start board
	result = start_board.transition(decision)
	# Write the action and resulting board to the output file
	with open('output.txt', 'w') as f:
		f.write('{}'.format(decision))
		for row in result.state:
			f.write('\n{}'.format(''.join(row)))



