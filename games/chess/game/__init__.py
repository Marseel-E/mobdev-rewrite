empty: str = "_"
k: str = "♔"
K: str = "♚"
q: str = "♕"
Q: str = "♛"
b: str = "♗"
B: str = "♝"
kn: str = "♘"
KN: str = "♞"
r: str = "♖"
R: str = "♜"
p: str = "♙"
P: str = "♟"
sp: str = "♙\u200b"
SP: str = "♟\u200b"

from discord import User, Member

class Player:
	def __init__(self, discord: User | Member, pieces: list[str]) -> None:
		self.discord = discord
		self.pieces = pieces

WHITE_PIECES = [
	*[sp for i in range(8)],
	r * 2, kn * 2, b * 2, q, k
]
BLACK_PIECES = [
	*[SP for i in range(8)],
	R * 2, KN * 2, B * 2, Q, K
]

from pprint import pprint

class Game:
	def __init__(self, player_1: User | Member, player_2: User | Member) -> None:
		self.player_1 = Player(player_1, WHITE_PIECES)
		self.player_2 = Player(player_2, BLACK_PIECES)

		self.turn = self.player_1
		self.moves_count = 0
		self.moves = []

		self.rows: int = 8
		self.cols: int = 8

		self.board = [[empty for i in range(self.cols)] for i in range(self.rows)]

		self.setup()


	def setup(self) -> None:		
		for row in range(self.rows):
			if row in [1, 6]:
				self.board[row] = [(SP if row == 1 else sp) for i in range(8)]
				continue

			if row in [0, 7]:
				for (col, piece) in enumerate(self.board[row]):
					if col in [0, 7]:
						piece = r if row == 0 else R
					if col in [1, 6]:
						piece = kn if row == 0 else KN
					if col in [2, 5]:
						piece = b if row == 0 else B
					if col == 3:
						piece = q if row == 0 else Q
					if col == 4:
						piece = k if row == 0 else K

					self.board[row][col] = piece


	def print_board(self) -> None:
		print(f"SIZE: {self.rows}", self.cols, sep=" x ")
		pprint(self.board)


	def turn_switch(self) -> None:
		self.turn = self.player_2 if self.turn.name == self.player_1.name else self.player_1


	def win_check(self) -> bool:
		self.turn_switch()

		if (k not in self.turn.pieces) and (K not in self.turn.pieces):
			self.turn_switch()
			return True

		self.turn_switch()

		return False


	def out_of_moves(self) -> bool:
		return self.moves_count > 100


	def evaluate_move(self, row: int, col: int, kill_only: bool = False) -> bool:
		try:
			self.board[row][col]
		except IndexError:
			return False
		else:
			if not kill_only:
				if self.board[row][col] == empty:
					self.moves.append((row, col))
			
			if self.board[row][col] not in [self.turn.pieces]:
				self.moves.append((row, col))


	def get_moves(self, row: int, col: int) -> None:
		self.moves = []

		piece = self.board[row][col]

		if piece in [k, K]:
			self.evaluate_move(row-1, col)   # TOP LEFT
			self.evaluate_move(row, col-1)   # UP
			self.evaluate_move(row-1, col+1) # TOP RIGHT
			self.evaluate_move(row, col-1)   # LEFT 
			self.evaluate_move(row, col+1)   # RIGHT
			self.evaluate_move(row+1, col-1) # BOTTOM LEFT
			self.evaluate_move(row+1, col)   # DOWN
			self.evaluate_move(row+1, col+1) # BOTTOM RIGHT

		if piece in [q, b, r, Q, B, R]:
			if piece not in [b, B]:
				[self.evaluate_move(row-i, col) for i in range(8)] # INF TOP
				[self.evaluate_move(row, col-i) for i in range(8)] # INF LEFT
				[self.evaluate_move(row, col+i) for i in range(8)] # INF RIGHT
				[self.evaluate_move(row+1, col) for i in range(8)] # INF BOTTOM

			if piece not in [r, R]:
				[self.evaluate_move(row-i, col-i) for i in range(8)] # INF TOP LEFT
				[self.evaluate_move(row-i, col+i) for i in range(8)] # INF TOP RIGHT
				[self.evaluate_move(row+i, col-i) for i in range(8)] # INF BOTTOM LEFT
				[self.evaluate_move(row+1, col+i) for i in range(8)] # INF BOTTOM RIGHT
		
		if piece in [kn, KN]:
			self.evaluate_move(row-2, col-1) # LONG TOP LONG LEFT
			self.evaluate_move(row-2, col+1) # LONG TOP LONG RIGHT
			self.evaluate_move(row-1, col-2) # TOP LONG LEFT
			self.evaluate_move(row-1, col+2) # TOP LONG RIGHT
			self.evaluate_move(row+1, col-2) # BOTTOM LONG LEFT
			self.evaluate_move(row+1, col+2) # BOTTOM LONG RIGHT
			self.evaluate_move(row+2, col-1) # LONG BOTTOM LONG LEFT
			self.evaluate_move(row+2, col+1) # LONG BOTTOM LONG RIGHT

		if piece in [sp, sp]:
			self.evaluate_move(row-1, col) # TOP
			
			if piece != p:
				self.evaluate_move(row-2, col) # LONG TOP (START PAWN)

			if piece != sp:
				self.evaluate_move(row-1, col-1, kill_only=True) # TOP LEFT (KILL)
				self.evaluate_move(row-1, col+1, kill_only=True) # TOP RIGHT (KILL)

		if piece in [P, SP]:
			self.evaluate_move(row+1, col) # TOP
			
			if piece != P:
				self.evaluate_move(row+2, col) # LONG TOP (START PAWN)

			if piece != SP:
				self.evaluate_move(row+1, col+1, kill_only=True) # TOP LEFT (KILL)
				self.evaluate_move(row+1, col-1, kill_only=True) # TOP RIGHT (KILL)


	def move(self) -> None:
		try:
			p_row, p_col, row, col = input("MOVE (FORMAT: <piece row> <piece col> <move row> <move col>): ").split(' ')
			p_row, p_col, row, col = int(p_row), int(p_col), int(row), int(col)
		except ValueError:
			print("MUST FOLLOW THE FORMAT")
			self.move()

		if (
			(
				(p_row < 0) or 
				(p_row > self.rows)
			) or (
				(p_col < 0) or 
				(p_col > self.cols)
			)
		):
			print("INVALID PIECE COORDINATES!")
			self.move()

		print("PIECE: ", self.board[p_row][p_col])

		if self.board[p_row][p_col] not in self.turn.pieces:
			print("INVALID PIECE!")
			self.move()

		self.get_moves(p_row, p_col)

		if (row, col) not in self.moves:
			print("INVALID MOVE!")
			self.move()

		if self.board[p_row][p_col] in [sp, SP]:
			self.board[p_row][p_col] = p if self.board[p_row][p_col] is sp else P

		self.turn_switch()
		if self.board[row][col] in self.turn.pieces:
			self.turn.pieces.pop(self.board[row][col])
		self.turn_switch()

		self.board[row][col] = self.board[p_row][p_col]
		self.board[p_row][p_col] = empty


	def start(self) -> None:
		while True:
			print("TURN:", self.turn.name)

			if self.out_of_moves():
				self.status = "draw"
				break

			self.print_board()

			self.move()

			if self.win_check():
				self.status = "win"
				break

			self.turn_switch()

		print("winner:", self.turn.name, self.status)


if __name__ == '__main__':
	game = Game(1, 2)
	game.start()