from discord import Interaction as Inter, User as D_User, Member as D_Member, Embed, ButtonStyle
from discord.ext.commands import Cog, Bot
from discord.app_commands import Group, command, describe
from discord.ui import View, Button, button

from utils import Default


class Game:
	def __init__(self, player: D_User | D_Member, opponent: D_User | D_Member, size: int = 3) -> None:
		self.player = player
		self.opponent = opponent
		self.turn = player
		self.size = size
		self.board = [['_' for i in  range(size)] for i in range(size)]

	def switch_turn(self) -> None:
		self.turn = self.player if self.turn.id == self.opponent.id else self.opponent

	def win_check(self) -> bool:
		user = self.turn

		if (
			( # H-TOP, TOP-LEFT > BOTTOM-RIGHT
				(self.board[0][0] == user) and 
				(
					(
						(self.board[0][1] == user) and 
						(self.board[0][2] == user)
					) or (
						(self.board[1][1] == user) and 
						(self.board[2][2] == user)
					)
				)
			) or ( # H-MIDDLE
				(self.board[1][0] == user) and
				(self.board[1][1] == user) and
				(self.board[1][2] == user)
			) or ( # H-BOTTOM, V-START, BOTTOM-LEFT > TOP-RIGHT
				(self.board[2][0] == user) and 
				(
					(
						(self.board[2][1] == user) and 
						(self.board[2][2] == user)
					) or (
						(self.board[1][0] == user) and 
						(self.board[0][0] == user)
					) or (
						(self.board[1][1] == user) and 
						(self.board[0][2] == user)
					)
				)
			) or ( # V-MIDDLE
				(self.board[2][1] == user) and 
				(self.board[1][1] == user) and 
				(self.board[0][1] == user)
			) or ( # V-END
				(self.board[2][2] == user) and 
				(self.board[1][2] == user) and 
				(self.board[0][2] == user)
			)
		): return True

		return False


class Game_button(Button):
	def __init__(self, coords: tuple[int], inter: Inter) -> None:
		self.coords = coords
		self.inter = inter

		super().__init__(
			label="_",
			style=ButtonStyle.blurple,
			row=coords[0]
		)

	async def callback(self, inter: Inter) -> None:
		game = self.view.game
		row, col = self.coords

		game.board[row][col] = game.turn

		label = "o"
		style = ButtonStyle.red

		if game.turn.id == game.player.id:
			label = "x"
			style = ButtonStyle.green

		self.label = label
		self.style = style
		self.disabled = True

		if game.win_check():
			return self.view.stop()

		game.switch_turn()

		await self.inter.edit_original_message(content=f"turn: {game.turn.mention}", view=self.view)


class Game_view(View):
	def __init__(self, game: Game) -> None:
		self.game = game

		super().__init__(timeout=300.0)

	async def interaction_check(self, inter: Inter) -> bool:
		if self.game.win_check():
			self.stop()
			return False

		return inter.user.id == self.game.turn.id

	async def on_timeout(self) -> None:
		if not self.game.win_check():
			self.game.switch_turn()
		
		self.stop()


class TicTacToe(Cog, Group, name="tic-tac-toe"):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot

		super().__init__()


	@command(
		description="Play a game of Tic Tac Toe against someone."
	)
	@describe(
		opponent="The user to play against.",
		bet="The amount of coins to bet on this game."
	)
	async def play(self, inter: Inter, opponent: D_Member, bet: int = 0, size: int = 3) -> None:
		game = Game(
			player=inter.user, 
			opponent=opponent,
			size=size
		)

		view = Game_view(game)
		for row in range(game.size):
			for col in range(game.size):
				view.add_item(Game_button((row, col), inter))

		await inter.response.send_message(content=f"turn: {game.turn.mention}", view=view)
		await view.wait()

		await inter.edit_original_message(content=f":tada: {game.turn.mention} won :tada:", view=None)


async def setup(bot: Bot) -> None:
	await bot.add_cog(TicTacToe(bot), guilds=[Default.test_server])