from discord import Interaction as Inter, Member as D_Member, ButtonStyle, SelectOption
from discord.ext.commands import Cog, Bot
from discord.app_commands import Group, command, describe
from discord.ui import View, Button, button, Select, select

from utils import Default
from game import Game, Player, empty, sp, SP, p, P


class Move_button(Button):
	def __init__(self, p_row: int, p_col: int, row: int, col: int) -> None:
		self.p_row = p_row
		self.p_col = p_col
		self.row = row
		self.col = col

		super().__init__(
			label=f"({row} | {col}) -> {self.view.game.board[row][col]}",
			style=ButtonStyle.green if self.view.game.board[row][col] is empty else ButtonStyle.reds
		)

	async def callback(self, inter: Inter) -> None:
		game = self.view.game

		if game.board[self.row][self.col] in [sp, SP]:
			self.view.game.board[self.row][self.col] = p if game.board[self.row][self.col] is sp else P

		game.turn_switch()
		if game.board[self.row][self.col] in game.turn.pieces:
			self.view.game.turn.pieces.pop(game.board[row][col])
		game.turn_switch()

		self.view.game.board[self.row][self.col] = game.board[self.p_row][self.p_col]
		self.view.game.board[self.p_row][self.p_col] = empty

		await inter.response.edit_message(view=None)

		self.view.stop()


class Piece_button(Button):
	def __init__(self, row: int, col: int) -> None:
		self.row = row
		self.col = col

		super().__init__(label=f"{row} | {col}")

	async def callback(self, inter: Inter) -> None:
		game = self.view.game

		moves = game.get_moves(self.row, self.col)


class Choose_piece(Select):
	def __init__(self, options: list[SelectOption]) -> None:
		super().__init__(placeholder="Choose piece", options=options)

	async def callback(self, inter: Inter) -> None:
		game = self.view.game

		pieces = []

		for row in range(game.rows):
			for (col, piece) in enumerate(game.board[row]):
				if piece is self.value:
					pieces.append(Piece_button(row, col))

		self.view.clear_items()
		[self.view.add_item(p_button) for p_button in pieces]

		await self.view.response.edit_message(view=self.view)


class Chess_view(View):
	def __init__(self, inter: Inter, game: Game) -> None:
		self.inter = inter
		self.game = game

		super().__init__(timeout=250.0)

	async def callback(self, inter: Inter) -> bool:
		return inter.user.id == self.inter.user.id

	async def on_timeout(self) -> None:
		await self.inter.delete_original_message()


class Chess(Cog, Group, name="chess"):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot
		super().__init__()


	@command(help="Classic chess game.")
	async def play(self, inter: Inter, member: D_Member, bet: int = 0) -> None:
		game = Game(inter.user, member)

		embed = Embed(
			title="Chess",
			description="",
			color=Default.color
		)

		await inter.response.send_message("loading...")

		while True:
			embed.add_field(name="Turn:", value=self.turn.mention, inline=False)

			if game.out_of_moves():
				game.status = "draw"
				break

			embed.description = self.convert_board()

			view = Chess_view(inter, game)
			
			options = []
			for piece in game.turn.pieces:
				options.append(SelectOption(
					label=piece,
					value=piece
				))

			view.add_item(Choose_piece(options))

			await inter.response.edit_message(embed=embed, view=view)
			await view.wait()

			if game.win_check():
				game.status = "win"
				break

			game.turn_switch()
			embed.clear_fields()

		await inter.response.edit_message(content=f":tada: {self.turn.mention} won! :tada:", view=None)


async def setup(bot: Bot) -> None:
	await bot.add_cog(Chess(bot), guilds=[Default.test_server])