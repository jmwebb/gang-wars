from random import random, randint

def random_board(blank=False):
	n = randint(5, 7)
	chance = random()
	board = [['.' for i in range(n)] for j in range(n)]
	values = [[0 for i in range(n)] for j in range(n)]
	for row in range(n):
		for col in range(n):
			val = randint(1,99)
			values[row][col] = val
			if not blank:
				if random() > chance:
					player = randint(0,1)
					if player == 1:
						board[row][col] = 'X'
					else:
						board[row][col] = 'O'
	return (board, values, n)


