from discord import User, ButtonStyle, Interaction as Inter, Embed
from discord.ui import View, Button

import random


class Tile_button(Button):
	def __init__(self, coordinates: tuple[int], value: int) -> None:
		self.coordinates = coordinates
		self.value = value

		super().__init__(
			label=" ",
			style=ButtonStyle.blurple
		)

	async def callback(self, inter: Inter) -> None:
		if int(self.value) < 0:
			for tile in self.view.children:
				tile.disabled = True

				if tile.style == ButtonStyle.blurple:
					tile.style = ButtonStyle.gray

				if tile.value < 0:
					tile.label = '💣'
				elif tile.value == 0:
					tile.label = " "
				else:
					tile.label = tile.value
				
				self.style = ButtonStyle.red

			await inter.response.edit_message(content=f"{inter.user.mention} You lost!", view=self.view)

			return

		self.disabled = True
		self.label = self.value if int(self.value) != 0 else " "
		self.style = ButtonStyle.green

		row, col = self.coordinates[0], self.coordinates[1]
		game = self.view.game

		game.detect_empty(self.view, row-1, col) # TOP
		game.detect_empty(self.view, row, col-1) # LEFT
		game.detect_empty(self.view, row, col+1) # RIGHT
		game.detect_empty(self.view, row+1, col) # BOTTOM

		game.win_check(self.view)

		await self.view.inter.edit_original_message(view=self.view)


from pprint import pprint


class Game:
	def __init__(self, player: User = None, rows: int = 5, cols: int = 5) -> None:
		self.player = player

		self.rows = rows
		self.cols = cols

		self.board = [[0 for i in range(cols)] for i in range(rows)]

		self.skip_top: bool = False
		self.skip_right: bool = False
		self.skip_bottom: bool = False
		self.skip_left: bool = False
		self.won: bool = False
		self.last_coords: tuple[int] = (0, 0)

		self.plant_bombs()
		pprint(self.board)

		self.setup_board()
		pprint(self.board)

	def win_check(self, view: View) -> bool | None:
		for item in view.children:
			if (not item.disabled) and (item.value != "💣"):
				return False

		for item in view.children:
			item.disabled = True

		self.won = True
		view.stop()

	def plant_bombs(self) -> None:
		bombs = (self.rows * self.cols) / 8
		locations = random.sample(list(zip(range(self.rows), range(self.cols))), k=round(bombs))

		for (x, y) in locations:
			self.board[x][y] -= 1

	def is_bomb(self, row: int, col: int) -> bool:
		try:
			tile = self.board[row][col]
		except IndexError:
			return False

		return tile < 0

	def is_connected(self, row, col) -> bool:
		last_row, last_col = self.last_coords

		return (
			((row > 0) and (row-1 == last_row)) and         # TOP
			((col < self.cols) and (col+1 == last_col)) and # RIGHT
			((row < self.rows) and (row+1 == last_row)) and # BOTTOM
			((col > 0) and (col-1 == last_col))         # LEFT
		)

	def detect_empty(self, view: View, row: int, col: int) -> bool:
		try:
			tile = self.board[row][col]
		except IndexError:
			return False

		if tile == 0:
			for item in view.children:
				if item.coordinates == (row, col):
					item.disabled = True
					item.style = ButtonStyle.green

		if ((not self.skip_top) and (row-1 < 0)) or (not self.is_connected(row-1, col)):
			self.skip_top = True
		if ((not self.skip_right) and (col+1 > self.cols)) or (not self.is_connected(row, col+1)):
			self.skip_right = True
		if ((not self.skip_bottom) and (row+1 > self.rows)) or (not self.is_connected(row+1, col)):
			self.skip_bottom = True
		if ((not self.skip_left) and (col-1 < 0)) or (not self.is_connected(row, col-1)):
			self.skip_left = True

		if not self.skip_top:
			self.last_coords = (row-1, col)
			self.detect_empty(view, row-1, col)
		if not self.skip_right: 
			self.last_coords = (row, col+1)
			self.detect_empty(view, row, col+1)
		if not self.skip_bottom:
			self.last_coords = (row+1, col)
			self.detect_empty(view, row+1, col)
		if not self.skip_left:
			self.last_coords = (row, col-1)
			self.detect_empty(view, row, col-1)

	def setup_board(self) -> None:
		for row in range(self.rows):
			for (col, tile) in enumerate(self.board[row]):
				if tile >= 0:
					if self.is_bomb(row-1, col-1): tile += 1 # TOP LEFT
					if self.is_bomb(row-1, col): tile += 1   # TOP
					if self.is_bomb(row-1, col+1): tile += 1 # TOP RIGHT
					if self.is_bomb(row, col-1): tile += 1   # LEFT
					if self.is_bomb(row, col+1): tile += 1   # RIGHT
					if self.is_bomb(row+1, col-1): tile += 1 # BOTTOM LEFT
					if self.is_bomb(row+1, col): tile += 1   # BOTTOM
					if self.is_bomb(row+1, col+1): tile += 1 # BOTTOM RIGHT

				self.board[row][col] = tile


	async def generate_discord_board(self, view: View) -> None:
		for row in range(self.rows):
			for (col, tile) in enumerate(self.board[row]):
				view.add_item(Tile_button((row, col), tile))


from discord.ext.commands import Cog, Bot
from discord.app_commands import Group, command, describe

from utils import Default


class Minesweeper_view(View):
	def __init__(self, inter: Inter, game: Game) -> None:
		self.inter = inter
		self.game = game

		super().__init__(timeout=250.0)

	async def interaction_check(self, inter: Inter) -> bool:
		return inter.user.id == self.inter.user.id

	async def on_timeout(self) -> None:
		await self.inter.delete_original_message()


class Minesweeper(Cog, Group, name="minesweeper"):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot

		super().__init__()


	@command(description="Classic minesweeper game.")
	async def play(self, inter: Inter, bet: int = 0) -> None:
		game = Game(inter.user)

		view = Minesweeper_view(inter, game)
		await game.generate_discord_board(view)
		await inter.response.send_message(content=inter.user.mention, view=view)
		await view.wait()

		if game.won:
			await inter.edit_original_message(content=f":tada:{inter.user.mention}, You won! :tada:")


async def setup(bot: Bot) -> None:
	await bot.add_cog(Minesweeper(bot), guilds=[Default.test_server])