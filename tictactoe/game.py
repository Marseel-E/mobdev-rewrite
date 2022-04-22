__all__ = ['Game']

from enum import Enum


class Tile(Enum):
	empty: str = "_"
	player: str = "x"
	opponent: str = "o"


class Game:
	def __init__(self, size: int = 3) -> None:
		assert (3 >= size <= 5)
		self.size = size
		self.player = Tile.player
		self.opponent = Tile.opponent		
		self.tiles = [[Tile.empty for i in range(self.size)] for i in range(self.size)]


	def is_finished(self) -> bool:
		for user in [self.player, self.opponent]:
			if (
				( # H-TOP, TOP-LEFT > BOTTOM-RIGHT
					(self.tiles[0][0] == user) and 
					(
						(
							(self.tiles[0][1] == user) and 
							(self.tiles[0][2] == user)
						) or (
							(self.tiles[1][1] == user) and 
							(self.tiles[2][2] == user)
						)
					)
				) or ( # H-MIDDLE
					(self.tiles[1][0] == user) and
					(self.tiles[1][1] == user) and
					(self.tiles[1][2] == user)
				) or ( # H-BOTTOM, V-START, BOTTOM-LEFT > TOP-RIGHT
					(self.tiles[2][0] == user) and 
					(
						(
							(self.tiles[2][1] == user) and 
							(self.tiles[2][2] == user)
						) or (
							(self.tiles[1][0] == user) and 
							(self.tiles[0][0] == user)
						) or (
							(self.tiles[1][1] == user) and 
							(self.tiles[0][2] == user)
						)
					)
				) or ( # V-MIDDLE
					(self.tiles[2][1] == user) and 
					(self.tiles[1][1] == user) and 
					(self.tiles[0][1] == user)
				) or ( # V-END
					(self.tiles[2][2] == user) and 
					(self.tiles[1][2] == user) and 
					(self.tiles[0][2] == user)
				)
			): return True

		return False