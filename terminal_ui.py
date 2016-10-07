from termcolor import colored
from random_board import random_board
import sys
from homework import Board, Action, AlphaBetaPlayer

def print_board():
	sys.stdout.write(colored('\t{}'.format('\t'.join([chr(65+i) for i in range(n)])), 'red', 'on_white', attrs=['underline']))
	print ''
	for row in range(n):
		sys.stdout.write(colored('{}\t'.format(row+1), 'red', 'on_white'))
		for col in range(n):
			if board.state[row][col] == 'X':
				sys.stdout.write(colored('{}'.format(values[row][col]), 'white', 'on_green'))
			elif board.state[row][col] == 'O':
				sys.stdout.write(colored('{}'.format(values[row][col]), 'white', 'on_red'))		
			else:
				sys.stdout.write('{}'.format(values[row][col]))
			sys.stdout.write('\t')
		sys.stdout.write('\n')
	sys.stdout.write(colored('X: {}'.format(board.scores['X']), 'white', 'on_green'))
	sys.stdout.write('\n')
	sys.stdout.write(colored('O: {}'.format(board.scores['O']), 'white', 'on_red'))
	sys.stdout.write('\n')

def valid_input(input_action):
	if input_action == 'QUIT':
		return True
	for legal_action in board.actions():
		if input_action == legal_action.simple_str():
			return True
	return False

state, values, n = random_board(blank=True)
board = Board(n, state, values, 'X')
ai = AlphaBetaPlayer('O', 'X', 4)
print_board()
while not board.terminal():
	print "{}'s turn!".format(board.turn)
	if board.turn == 'X':
		input_action = raw_input("Input move (e.g. B2 S) or 'QUIT': ").upper()
		while not valid_input(input_action):
			input_action = raw_input("Invalid move, try again: ").upper()
		if input_action == 'QUIT':
			break
		else:
			position, action_type = input_action.split()
			piece_position = (int(position[1])-1, ord(position[0])-65)
			action = Action(piece_position, action_type, board.turn)
	else:
		action = ai.alpha_beta_search(board)
	print '{} {}s at {}'.format(action.player, str(action).split()[1], str(action).split()[0])
	board = board.transition(action)
	print_board()







