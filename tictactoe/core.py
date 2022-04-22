from typing import TYPE_CHECKING

from discord import Interaction as Inter, Member as D_Member, Embed, ButtonStyle
from discord.ext.commands import Cog, Bot
from discord.app_commands import Group, command, describe
from discord.ui import View, Button, button

from utils import Default

if TYPE_CHECKING:
	from .game import *


class Board_Button(View):
	def __init__(self, label: str) -> None:
		super().__init__(
			label=label,
			style=ButtonStyle.blurple
		)

	async def callback(self, inter: Inter) -> None:
		self.label = game.current_player
		self.style = ButtonStyle.green if game.current_player == Tile.player else ButtonStyle.red
		self.disabled = True

		await self.view.inter.edit_original_message(view=self.view)

		game.current_player = game.opponent if game.current_player == game.player else game.player


class Board(View):
	def __init__(self, inter: Inter, game: Game) -> None:
		self.inter = inter
		self.game = game

		super().__init__(timeout=300.0)

	async def interaction_check(self, interaction: Interaction) -> bool:
		return interaction.user.id == self.inter.user.id

	async def on_timeout(self) -> None:
		await self.inter.delete_original_message()


class TicTacToe(Cog, Group):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot

		super().__init__(name="tic-tac-toe")


	@command()
	@describe(
		opponent="The member you want to play against.", 
		bet="The amount of coins you want to bet on this game."
	)
	async def play(self, inter: Inter, opponent: D_Member, bet: int = 0) -> None:
		if inter.user.id == opponent.id:
			return await inter.response.send_message("can't play with yourself", ephemeral=True)

		game = Game(inter.user, opponent)

		view = Board(inter, game)
		for row in range(game.rows):
			for col in range(game.columns):
				view.add_item(Board_Button(game.tiles[row][col]))

		await inter.response.send_message(view=view)
		await view.wait()


async def setup(bot: Bot) -> None:
	await bot.add_cog(TicTacToe(bot), guilds=[Default.test_server])