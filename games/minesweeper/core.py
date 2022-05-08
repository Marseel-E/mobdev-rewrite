import random
import itertools

from discord import Interaction as Inter, User, ButtonStyle
from discord.ext.commands import Cog, Bot
from discord.app_commands import Group, command, Range
from discord.ui import View, Button, button

from utils import Default


class Game:
	def __init__(self, player: User, bombs: int) -> None:
		self.player = player

		self.board = [[0 for i in range(5)] for i in range(5)]
		self.setup_board(bombs)

		self.zeros = self.get_zeros()

		self.won: bool = False


	def incr_empty(self, row: int, col: int) -> None:
		""" increases the tile value """
		# Makes sure the tile isn't out of index
		if (
			(5 > row >= 0) and
			(5 > col >= 0) 
		):
			# Makes sure the tile isn't a bomb
			if self.board[row][col] >= 0:
				# Increments the tile by 1
				self.board[row][col] += 1


	def setup_board(self, bombs: int) -> list[list[int]]:
		""" Sets the board bombs & numbers around them """
		# Generates the locations for the bombs
		placements = random.sample(list(itertools.product(range(5), range(5))), k=bombs)

		# Places the bombs on the board
		for (row, col) in placements:
			self.board[row][col] -= 1

		for (row, col) in placements:
			# Generates the numbers around the bombs
			# TOP LEFT
			self.incr_empty(row-1, col-1)
			# TOP
			self.incr_empty(row-1, col)
			# TOP RIGHT
			self.incr_empty(row-1, col+1)
			# RIGHT
			self.incr_empty(row, col+1)
			# BOTTOM RIGHT
			self.incr_empty(row+1, col+1)
			# BOTTOM
			self.incr_empty(row+1, col)
			# BOTTOM LEFt
			self.incr_empty(row+1, col-1)
			# LEFT
			self.incr_empty(row, col-1)


	def get_zeros(self) -> list[tuple[int, int]]:
		""" Returns a list coordinates of all zero/empty tiles on the board """
		zeros = []
		for row in range(5):
			for (col, tile) in enumerate(self.board[row]):
				if tile == 0:
					zeros.append((row, col))

		return zeros

	def win_check(self, view: View) -> bool:
		for item in view.children:
			if not item.disabled:
				row, col = item.coords
				if self.board[row][col] >= 0:
					return False

		for item in view.children:
			item.disabled = True
			if item.value < 0:
				item.label = "💣"
				item.style = ButtonStyle.gray

		self.won = True
		return True


	def reveal_if_empty(self, view: View, row: int, col: int) -> None:
		""" reveals the tile if its empty and next to the last empty tile """
		# assures that the tile is empty
		if (row, col) not in self.zeros:
			return

		self.zeros.remove((row, col))

		for item in view.children:
			b_row, b_col = item.coords
			# if the button is the current empty tile
			if (
				(row == b_row) and 
				(col == b_col)
			):
				item.disabled = True
				item.style = ButtonStyle.green

				# reruns the function to disable other empty tiles that are connected
				if row > 0: # UP
					self.reveal_if_empty(view, row-1, col)
				if col < 5: # RIGHT
					self.reveal_if_empty(view, row, col+1)
				if row < 5: # DOWN
					self.reveal_if_empty(view, row+1, col)
				if col > 0: # LEFT
					self.reveal_if_empty(view, row, col-1)


class Play_view(View):
	def __init__(self, inter: Inter, game: Game) -> None:
		self.inter = inter
		self.game = game
		super().__init__(timeout=250.0)

	async def interaction_check(self, inter: Inter) -> bool:
		return inter.user.id == self.inter.user.id

	async def on_timeout(self) -> None:
		await self.inter.delete_original_message()


class Tile_button(Button):
	def __init__(self, coords: tuple[int, int], value: int) -> None:
		self.coords = coords
		self.value = value

		super().__init__(
			label=" ",
			style=ButtonStyle.blurple
		)

	async def callback(self, inter: Inter) -> None:
		view = self.view
		game = view.game

		if self.value < 0:
			for item in view.children:
				item.disabled = True

				if item.value == 0:
					item.label = " "
				elif item.value < 0:
					item.label = "💣"
				else:
					item.label = item.value

				if item.style == ButtonStyle.blurple:
					item.style = ButtonStyle.gray

				self.style = ButtonStyle.red

			await inter.response.edit_message(
				content=f"{inter.user.mention}, you lost!",
				view=view
			)

			return view.stop()

		self.disabled = True
		self.style = ButtonStyle.green
		self.label = " " if self.value == 0 else self.value

		row, col = self.coords

		if row > 0: game.reveal_if_empty(view, row-1, col) # TOP
		if col < 5: game.reveal_if_empty(view, row, col+1) # RIGHT
		if row < 5: game.reveal_if_empty(view, row+1, col) # BOTTOM
		if col > 0: game.reveal_if_empty(view, row, col-1) # LEFT

		if game.win_check(view):
			view.stop()

		await inter.response.edit_message(view=view)


class Minesweeper(Cog, Group, name="minesweeper"):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot

		super().__init__()


	@command()
	async def play(self, inter: Inter, bombs: Range[int, 1, 25] = 3, bet: int = 0):
		game = Game(inter.user, bombs)

		view = Play_view(inter, game)
		view.clear_items()
		for row in range(5):
			for (col, tile) in enumerate(game.board[row]):
				view.add_item(Tile_button(
					value=tile,
					coords=(row, col)
				))

		await inter.response.send_message(
			content=inter.user.mention,
			view=view
		)
		await view.wait()

		if game.won:
			await inter.edit_original_message(content=f":tada: {inter.user.mention}, you win! :tada:")


async def setup(bot: Bot) -> None:
	await bot.add_cog(Minesweeper(bot), guilds=[Default.test_server])