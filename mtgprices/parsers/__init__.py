from mtgprices.models import Site
from mtgprices.parsers.base import Parser
from mtgprices.parsers.goldfish import GoldFishParser
from mtgprices.parsers.scryfall import ScryfallParser
from mtgprices.parsers.starcitygames import StarCityGamesParser

PARSERS: dict[Site, Parser] = {
    Site.STARCITYGAMES: StarCityGamesParser(),
    Site.GOLDFISH: GoldFishParser(),
    Site.SCRYFALL: ScryfallParser(),
}


def get_parser(site: Site) -> Parser:
    return PARSERS[site]
