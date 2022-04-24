import aiohttp

from typing import TypedDict

from pprint import pprint

from discord.enums import ButtonStyle


class QuestionData(TypedDict):
	category: str
	type: str
	difficulty: str
	question: str
	correct_answer: str
	incorrect_answers: list[str]

async def get_question() -> QuestionData:
	async with aiohttp.ClientSession() as session:
		async with session.get('https://opentdb.com/api.php?amount=1') as response:
			return (await response.json())['results'][0]


from discord import Interaction as Inter, Embed, ButtonStyle
from discord.ui import View, Button, button


class Trivia_button(Button):
	def __init__(self, label: str, correct_answer: bool | None = None) -> None:
		self.correct_answer = correct_answer

		super().__init__(
			label=label,
			style=ButtonStyle.blurple,
		)

	async def callback(self, inter: Inter) -> None:
		for answer in self.view.children:
			answer.style = ButtonStyle.green if (answer.correct_answer) else ButtonStyle.red
			answer.disabled = True

		await self.view.inter.edit_original_message(view=self.view)

		await inter.response.send_message(content=":tada: correct! :tada:" if self.correct_answer else ":x: incorrect :x:", ephemeral=True)

		self.view.stop()

class Trivia_view(View):
	def __init__(self, inter: Inter) -> None:
		self.inter = inter

		super().__init__(timeout=60.0)

	async def interaction_check(self, inter: Inter) -> bool:
		return inter.user.id == self.inter.user.id

	async def on_timeout(self) -> None:
		await self.inter.delete_original_message()

import random
import html

from discord.ext.commands import Cog, Bot
from discord.app_commands import Group, command, describe

from utils import Default


class Trivia(Cog, Group, name="trivia"):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot

		super().__init__()


	@command(description="Random trivia questions.")
	@describe(bet="The amount of coins to bet on this question.")
	async def play(self, inter: Inter, bet: int = 0) -> None:
		question = await get_question()

		embed = Embed(
			title=html.unescape(question['question']),
			description="",
			color=Default.color
		)

		list_answers = question['incorrect_answers']
		list_answers.append(question['correct_answer'])
		random.shuffle(list_answers)
	
		view = Trivia_view(inter)

		for i, answer in enumerate(list_answers):
			kwargs = {'label': i+1}

			if answer == question['correct_answer']:
				kwargs['correct_answer'] = True

			view.add_item(Trivia_button(**kwargs))

			embed.description += f"{i+1}. {html.unescape(answer)}\n"

		await inter.response.send_message(embed=embed, view=view, ephemeral=True)
		await view.wait()


async def setup(bot: Bot) -> None:
	await bot.add_cog(Trivia(bot), guilds=[Default.test_server])