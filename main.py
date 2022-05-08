from os import environ, listdir
from traceback import print_tb

from discord import Status, Game, Intents
from discord.ext.commands import Bot
from dotenv import load_dotenv

load_dotenv('.env')

from utils import Default


class MobDev(Bot):
	def __init__(self) -> None:
		super().__init__(
			help_command=None,
			command_prefix=".",
			case_sensitive=True,
			status=Status.online,
			intents=Intents.default(),
			activity=Game("minigames.exe"),
			application_id=environ.get("APP_ID"),
			description="A feature-rich & well designed minigames bot"
		)

	async def on_ready(self) -> None:
		print("STATUS: running...")

	async def setup_hook(self) -> None:
		for game in listdir('games'):
			if 'core.py' not in listdir(f'games/{game}'):
				continue
			
			try:
				await self.load_extension(f'games.{game}.core')
			except Exception as e:
				print(f"ERROR: failed to load '{game}'", end="\n")
				print_tb(e)
			else:
				print(f"STATUS: loaded '{game}'", end="\n")

		try:
			await self.tree.sync()
			await self.tree.sync(guild=Default.test_server)
		except Exception as e:
			print("ERROR: failed to sync commands", end="\n")
			print_tb(e)
		else:
			print("STATUS: synced commands")


if __name__ == '__main__':
	MobDev().run(environ.get("TOKEN"))