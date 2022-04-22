__all__ = ['Color', 'Default']

from dataclasses import dataclass

from discord import D_Object


@dataclass
class Color:
	default: int = int("5261f8", 16)


@dataclass
class Default:
	test_server: D_Object = D_Object(id=843994109366501376)
	color: int = Color.default