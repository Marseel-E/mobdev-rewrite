from typing import TYPE_CHECKING

from discord import Interaction as Inter, Member as D_Member
from discord.ext.commands import Cog, Bot
from discord.app_commands import Group, command, describe

from utils import Default

if TYPE_CHECKING:
	from .game import *


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
		pass


async def setup(bot: Bot) -> None:
	await bot.add_cog(TicTacToe(bot), guilds=[Default.test_server])