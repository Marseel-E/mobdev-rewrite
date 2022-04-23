__all__ = ['Game', 'User']

from discord import User as D_User, Member as D_Member, ButtonStyle


class User:
	def __init__(self, discord: D_User | D_Member | None, icon: str, color: ButtonStyle = ButtonStyle.blurple) -> None:
		self.discord = discord
		self.id = discord.id if discord is not None else 0
		self.icon = icon
		self.color = color

	def __eq__(self, other) -> bool:
		if isinstance(self, other):
			return self.id == other.id

		return False

class Empty(User):
	def __init__(self) -> None:
		super().__init__(icon="_", discord=None)


class Game:
	def __init__(self, player: D_User | D_Member, opponent: D_User | D_Member, size: int = 3) -> None:
		assert (3 >= size <= 5)
		self.size = size
		self.player = User(player, "x", ButtonStyle.green)
		self.opponent = User(opponent, "o", ButtonStyle.red)
		self.turn = self.player
		self.tiles = [[Empty() for i in range(self.size)] for i in range(self.size)]


	