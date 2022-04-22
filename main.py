from os import environ, listdir

from discord import Status, Game, Intents
from discord.ext.commands import Bot
from dotenv import load_dotenv

load_dotenv('.env')

from utils import Default


class MobDev(Bot):
	def __init__(self, status: str = "minigames.exe") -> None:
		self.status = status
		super().__init__(
			help_command=None,
			command_prefix=".",
			case_sensitive=True,
			intents=Intents.default()
			application_id=environ.get("APP_ID"),
			description="A feature-rich & well designed minigames bot"
		)

	async def on_ready(self) -> None:
		print("STATUS: running...")

	async def setup_hook(self) -> None:
		for game in listdir('games'):
			try:
				await self.load_extension(f'games.{game}.core')
			except Exception as e:
				print(f"ERROR: failed to load '{game}'", e, sep="\n")
			else:
				print(f"STATUS: loaded '{game}'", end="\n")

		await self.tree.sync()
		await self.tree.sync(guild=Default.test_server)

		await self.change_presence(
			status=Status.online,
			activity=Game(self.status)
		)


if __name__ == '__main__':
	MobDev().run(environ.get("TOKEN"))