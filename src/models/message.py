from models.matches import Matches
import random
import logging

class Message:
    matches = Matches
    punlines = {}
    used_verbs = []

    # this value represents the expected maximum number of players in a match
    verb_decay = 5

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
    logger = logging.getLogger(__name__)

    def __init__(self, matches, punlines):
        self.matches = matches
        self.punlines = punlines
        
    def get_messages(self):
        messages = []
        for match in self.matches.get_matches():
            messages.append(self._create_message_for_match(match))
        return messages

    def _create_message_for_match(self, match):
        messages = []

        if match.win:
            messages.append(random.choice(self.punlines["win"]))
        else:
            messages.append(random.choice(self.punlines["lose"]))

        for matchresult in match.matchresults:
            verb = self._generate_verb(matchresult)

            while self._check_verb_used(verb):
                verb = self._generate_verb(matchresult)

            messages.append(f"{matchresult.name} hat mit {matchresult.hero} {self._generate_verb(matchresult)} mit {matchresult.kills} Kills, {matchresult.deaths} Toden und {matchresult.assists} Assists")

        return '\n\n'.join(messages)
        
    def _check_verb_used(self, verb):
        if verb in self.used_verbs:
            return True
        else:
            used_verbs = used_verbs[1:self.verb_decay - 1] + [verb]
            return False

    def _generate_verb(self, matchresult):
        verb = ""
        if matchresult.meme_constant < 0.5:
            verb = random.choice(self.punlines["<0.5"])
        elif matchresult.meme_constant < 1:
            verb = random.choice(self.punlines["<1"])
        elif matchresult.meme_constant < 2:
            verb = random.choice(self.punlines["<2"])
        elif matchresult.meme_constant < 5:
            verb = random.choice(self.punlines["<5"])
        elif matchresult.meme_constant < 10:
            verb = random.choice(self.punlines["<10"])
        else:
            verb = random.choice(self.punlines[">10"])

        return verb