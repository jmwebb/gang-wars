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
	"""
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
	def __init__(self, n, state, values, turn, \
		remaining_spaces=None, scores={'X':0, 'O':0}):
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
		positions = []
		if (row + 1) < self.n:
			positions.append((row+1,col))
		if (row - 1) >= 0:
			positions.append((row-1, col))
		if (col + 1) < self.n:
			positions.append((row,col+1))
		if (col - 1) >= 0:
			positions.append((row, col-1))
		return positions


	def actions(self):
		legal_actions = []
		current_player_owned = []
		# Identify all valid "Stake" actions
		for row in range(self.n):
			for col in range(self.n):
				if self.state[row][col] == '.':
					legal_actions.append(Action((row, col), 'S', self.turn))
				elif self.state[row][col] == self.turn:
					current_player_owned.append((row,col))

		# Identify all valid "Raid" actions
		for owned in current_player_owned:
			row, col = owned
			for adjacent in self.adjacent_positions(row, col):
				adj_r, adj_c = adjacent
				if self.state[adj_r][adj_c] == '.':
					legal_actions.append(Action((adj_r, adj_c), 'R', self.turn))

		return legal_actions


	def transition(self, action):
		new_state = []
		new_scores = {'X': self.scores['X'], 'O': self.scores['O']}
		for row in self.state:
			new_row = []
			for position in row:
				new_row.append(position)
			new_state.append(new_row)

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
		return self.remaining_spaces == 0


class AlphaBetaPlayer:
	def __init__(self, my_player, opponent, max_depth):
		self.my_player = my_player
		self.opponent = opponent
		self.max_depth = max_depth

	def cutoff_test(self, state, curr_depth):
		if curr_depth >= self.max_depth:
			return True
		elif state.terminal():
			return True
		return False

	def evaluation(self, state):
		return state.scores[self.my_player] - state.scores[self.opponent]

	def max_value(self, state, alpha, beta, curr_depth):
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
		if self.cutoff_test(state, curr_depth):
			return self.evaluation(state)
		v = float('Inf')
		for action in state.actions():
			v = min(v, self.max_value(state.transition(action), alpha, beta, curr_depth+1))
			if v <= alpha:
				return v
			beta = min(beta, v)
		return v

	def alpha_beta_search(self, state):
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


if __name__ == '__main__':
	start_state = []
	start_scores = {'X':0, 'O':0}
	values = []
	my_player = ''
	opponent = ''
	max_depth = 0
	n = 0
	remaining_spaces = n**2
	with open('input.txt', 'r') as f:
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
			start_state.append(lines[j].strip())

	for row in range(n):
		for col in range(n):
			if start_state[row][col] != '.':
				remaining_spaces -= 1
				start_scores[start_state[row][col]] += values[row][col]

	start_board = Board(n, start_state, values, my_player, \
		remaining_spaces=remaining_spaces, scores=start_scores)
	ai = AlphaBetaPlayer(start_board.turn, start_board.opponent, max_depth)
	decision = ai.alpha_beta_search(start_board)
	result = start_board.transition(decision)

	with open('output.txt', 'w') as f:
		f.write('{}'.format(decision))
		for row in result.state:
			f.write('\n{}'.format(''.join(row)))



