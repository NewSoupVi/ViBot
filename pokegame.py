from dataclasses import dataclass
from enum import Enum


class PokemonType(Enum):
    NoType = -1
    Grass = 1
    Poison = 2


@dataclass
class Pokemon:
    dexNo: int = -1
    form: str = ""
    name: str = "Missingno."
    type1: PokemonType = PokemonType.NoType
    type2: PokemonType = PokemonType.NoType
    level: int = 1


class PokeGame:
    def __int__(self):
        print("PokeGame initialized!")

    async def catch_pokemon(self, discord_id = -1):
        return Pokemon(dexNo=1, name="Bulbasaur", type1=PokemonType.Grass, type2=PokemonType.Poison)
