class Tile:
	def __init__(self, x: int, y: int) -> None:
		self.x = x
		self.y = y

	def __str__(self) -> str:
		return f"{self.x} | {self.y}"

	def __eq__(self, other) -> bool:
		return (
			self.x == other.x or
			self.y == other.y
		)

	def __lt__(self, other) -> bool:
		return (sum([self.x, self.y]) < sum([other.x, other.y]))

	def __gt__(self, other) -> bool:
		return (sum([self.x, self.y]) > sum([other.x, other.y]))

	def __add__(self, other) -> int:
		return sum([self.x, self.y]) + sum([other.x, other.y])

class Player:
	def __init__(self, discord: D_User | D_Member, tiles: list[Tile]) -> None:
		self.discord = discord
		self.tiles = tiles

	def __len__(self) -> int:
		return sum([tile_sum for tile_sum in [sum([tile.x, tile.y]) for tile in self.tiles]])

	def __iter__(self) -> list[Tile]:
		return self.tiles

import random

from discord import Interaction as Inter, Embed, D_User, D_Member, ButtonStyle


class Game:
	def __init__(self, player: D_User | D_Member, opponent: D_User, D_Member) -> None:
		self.dominos = self.generate_set()
		self.player = Player(player, tiles=self.get_hand())
		self.opponent = Player(opponent, tiles=self.get_hand())
		
		self.left = None
		self.right = None
		self.up = None
		self.down = None

		self.give_hands()

	@property
	def board(self) -> str:
		return [f"[{str(tile)}]" for tile in self.tiles] or ""

	def generate_set(self) -> list[Tile]:
		dominos = [
			(0,0),
			(0,1), (1,1),
			(0,2), (1,2), (2,2),
			(0,3), (1,3), (2,3), (3,3),
			(0,4), (1,4), (2,4), (3,4), (4,4),
			(0,5), (1,5), (2,5), (3,5), (4,5), (5,5),
			(0,6), (1,6), (2,6), (3,6), (4,6), (5,6), (6,6)
		]

		return [Tile(x, y) for (x, y) in dominos]

	def get_hand(self) -> list[Tile]:
		hand = random.choice(self.dominos, k=7)
		[self.dominos.pop(tile) for tile in hand]

		return hand

	def win_check(self) -> bool | Player:
		assert len(self.player) != len(self.opponent)

		if not (len(self.player)): return self.player
		if not (len(self.opponent)): return self.opponent
		
		return False

	def turn_switch(self) -> None:
		self.turn = self.player if self.turn.discord.id == self.opponent.discord.id else self.opponent

	def get_playable_tiles(self) -> list[Tile]:
		return [tile for tile in self.turn.tiles if tile == (self.left or self.right or self.up or self.down)]


from discord.ui import View, Button, button


class Domino_pos_button(Button):
	def __init__(self, direction: str, tile: Tile) -> None:
		self.direction = direction
		self.tile = tile

		super().__init__(
			label=direction,
			style=ButtonStyle.green
		)

	async def callback(self, inter: Inter) -> None:
		if self.direction == "left": self.view.game.left = self.tile
		if self.direction == "right": self.view.game.right = self.tile
		if self.direction == "up": self.view.game.up = self.tile
		if self.direction == "down": self.view.game.down = self.tile

class Domino_tile_button(Button):
	def __init__(self, tile: Tile, disabled: bool) -> None:
		self.tile = tile

		super().__init__(
			label=str(tile),
			style=ButtonStyle.blurple,
			disabled=disabled
		)

	async def callback(self, inter: Inter) -> None:
		view.clear_items()

		for direction in ['left', 'right', 'up', 'down']:
			view.add_item(Domino_pos_button(direction, self.tile))

		await self.view.inter.edit_original_message(view=self.view)

class Domino_view(View):
	def __init__(self, inter: Inter, game: Game) -> None:
		self.inter = inter
		self.game = game

		super().__init__()

	async def interaction_check(self, inter: Inter) -> bool:
		winner = self.game.win_check()

		if (winner):
			self.game.turn = winner
			self.stop()
			return False

	    return inter.user.id == self.game.turn.discord.id

	async def on_timeout(self) -> None:
		if not (self.game.win_check() or self.game.draw_check()):
			self.game.switch_turn()

		self.stop()


from discord.ext.commands import Cog, bot
from discord.app_commands import Group, command, describe

from utils import Default


class Dominos(Cog, Group, name="dominos"):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot

		super().__init__()


	@command(describe="Play a game of dominos against someone.")
	@describe(
		opponent="Your opponent",
		bet="The amount of coins you want to be on this game."
	)
	async def play(self, inter: Inter, opponent: D_Member, bet: int = 0) -> None:
		if inter.user.id == opponent.user.id:
			return await inter.response.send_message("You can't play with yourself m8", ephemeral=True)

		game = Game(
			player=inter.user,
			opponent=opponent
		)

		game.turn = game.player if sum([max(game.player)]) > sum([max(game.opponent)]) else game.opponent

		embed = Embed(
			title="Dominos",
			description=game.board,
			color=Default.color
		)
		game.footer(text=f"Turn: {game.turn.discord}", icon_url=game.turn.discord.avatar.url)

		view = Domino_view(inter, game)

		for tile in game.turn.tiles:

			view.add_item(Domino_tile_button(
				tile=tile,
				disabled=False if tile in game.get_playable_tiles() else True
			))

		await inter.response.send_message(embed=embed, view=view)
		await view.wait()

		await inter.edit_original_message(content=f":tada: {game.turn.mention} won! :tad:", view=None)


async def setup(bot: Bot) -> None:
	await bot.add_cog(Dominos(bot), guilds=[Default.test_server])