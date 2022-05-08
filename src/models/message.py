from models.matches import Matches
import random
import numpy as np
import re
import logging
from models.match import Match
from models.playerinfo import Playerinfo
import pytz

class Message:
    matches = Matches
    punlines = {}
    verb_numbers = {}
    meme_const_cats = []
    meme_const_cats_parsed = {}
    playerinfos = []
    used_verbs = {}

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
    logger = logging.getLogger(__name__)

    def __init__(self, matches, punlines, playerinfos):
        self.matches = matches
        self.punlines = punlines
        self.verb_numbers = {key: len(value) for key, value in punlines['performance_verbs'].items()}
        self.meme_const_cats = [key for key in punlines['performance_verbs'].keys()]
        self.meme_const_cats_parsed = self._parse_meme_const_categories()
        self.playerinfos = playerinfos
        self.used_verbs = self._reset_used_verbs()
        
    def get_messages_for_matches(self):
        messages = []
        for match in self.matches.get_matches():
            messages.append(self._create_message_for_match(match))
        return messages

    def get_message_for_playerinfos(self):
        messages = []
        for playerinfo in self.playerinfos:
            messages.append(self._create_message_for_playerinfos(playerinfo))
        return '\n\n'.join(messages)

    def _create_message_for_playerinfos(self, playerinfo: Playerinfo):
        messages = []
        messages.append(f"<b>{playerinfo.name}</b>")
        messages.append(f"Steamname: {playerinfo.steamname}")
        messages.append(f"Anzahl Spiele: {playerinfo.count_games}")
        messages.append(f"Siege: {playerinfo.wins}")
        messages.append(f"Niederlagen: {playerinfo.loses}")
        messages.append(f"Win rate: {playerinfo.win_rate}")
        messages.append(f"Letztes Spiel: {playerinfo.last_game.strftime('%d.%m.%Y %H:%M:%S')} ({playerinfo.days_since_last_game} Tag(e) vergangen)")
        return '\n'.join(messages)

    def _create_message_for_match(self, match: Match):
        messages = []

        if match.win:
            messages.append(f"<b>W: {random.choice(self.punlines['match_outcome']['win'])}</b>")
        else:
            messages.append(f"<b>L: {random.choice(self.punlines['match_outcome']['lose'])}</b>")

        for matchresult in match.matchresults:
            messages.append(f"{matchresult.name} hat mit {matchresult.hero} {self._generate_verb(matchresult)} mit {matchresult.kills} Kills, {matchresult.deaths} Toden und {matchresult.assists} Assists")

        self._reset_used_verbs()

        return '\n\n'.join(messages)

    def _parse_meme_const_categories(self):
        meme_const_cats_parsed = {}

        for const_cat in self.meme_constant_cats:
            prefix_match = re.search("^[<>]", const_cat)
            cat_cat_match = re.search("(?<=^[<>])[0-9]+", const_cat)

            if not all([prefix_match, cat_cat_match]):
                raise(f"Could not parse meme constant category {const_cat}. "
                        "Ensure it matches the convention of '[<>]x', with "
                        "'x' being a positive integer.")

            meme_const_cats_parsed[cat_cat_match.group(0)] = prefix_match.group(0)

        self.meme_const_cats_parsed = meme_const_cats_parsed

        return None

    def _reset_used_verbs(self, cat = None):
        if cat is None:
            self.used_verbs = {key: [] for key in self.verb_numbers.keys()}
        else:
            if type(cat) is str:
                if not cat in self.meme_const_cats:
                    raise(f"'{cat}' is no a valid category.")
                self.used_verbs[cat] = []
            elif type(cat) is list:
                # FIXME: make the error say which categories are invalid
                if not all([x in self.meme_const_cats for x in cat]):
                    raise(f"'{cat}' contains invalid categories.")
                for cat_i in cat:
                    self.used_verbs[cat_i] = []

        return None

    def _generate_verb(self, matchresult):
        verb = ""

        mc_cat_array = np.array(self.meme_const_cats_parsed.key())

        # TODO: this currently depends on categories being sorted, this may not be given
        mc_cat_idx_arr = np.which(mc_cat_array > matchresult.meme_constant)[0]

        if mc_cat_idx_arr.size == 0:
            cat = self.meme_constant_cats[mc_cat_array.size - 1]
        else:
            cat = self.meme_constant_cats[mc_cat_array[0]]

        cat_verb_n = self.verb_numbers[cat]

        if len(self.used_verbs[cat]) >= cat_verb_n:
            self.logger.info(f"Out of unique verbs for category {cat}, "
                                "resetting list of used verbs...")
            self._reset_used_verbs()

        verb_idx_list = [* range(0, cat_verb_n)]

        verb_idx_set_unused = set(verb_idx_list) - set(self.used_verbs[cat])

        verb_idx = random.choice([* verb_idx_set_unused])

        verb = self.punlines["performance_verbs"][cat][verb_idx]

        return verb