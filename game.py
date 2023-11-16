import csv
import logging
import random
import sys

from enums import Handedness, PitcherDice, Positions, Traits


logging.basicConfig(filename='debug.log', level=logging.DEBUG)

# CONFIGURATION
N_INNINGS    = 9
N_BALLS_AB   = 4
N_STRIKES_AB = 3


def roll(kind: str) -> int:
    count, n_sides = kind.split('d')
    count   = int(count) if count else 1
    n_sides = int(n_sides)
    result = 0
    for n in range(count):
        result += random.randrange(1, n_sides+1)
    logging.debug("Rolled %s -> %s", kind, result)
    return result


class Player:
    def __init__(self, number, name, pos, hand, bt, obt, traits=None, pd=None):
        self.number = number
        self.name   = name
        self.pos    = pos
        self.hand   = hand
        self.bt     = bt
        self.obt    = obt
        self.traits = traits or []
        self.pd     = pd

    def __str__(self):
        return '\n'.join([
            line.strip() for line in
            f'''
            Name: {self.name}
            ------{'-'*len(self.name)}
            Position: {self.pos.name} Handed: {self.hand.name}
            BT: {self.bt} OBT: {self.obt} {'PD:' if self.pd else ''} {self.pd.name if self.pd else ''}
            {'Traits:' if self.traits else ''} {' '.join([t.name for t in self.traits]) if self.traits else ''}
            '''.split('\n')
        ]).strip()


class Team:
    def __init__(self, name, players=None):
        self.name     = name
        self.players  = set(players) if players else set()

        self._retired = set()
        self.lineup   = []

        logging.debug("Inited team %s with %s ball players.", self.name, len(self.players))

    @property
    def retired(self):
        return self._retired

    @property
    def bench(self):
        return self.players - set(self.lineup) - self.retired

    def set_lineup(self, numbers=None):
        numbers = numbers or list(range(1, 10))

        assert len(numbers) == 9, "Nine players are required to set a lineup."

        self.lineup = [
            self.get_player_by_number(n)
            for n in numbers
        ]

        logging.debug("Set lineup: %s", ', '.join([ str(n) for n in self.lineup ]))

    def retire(self, player: Player) -> int:
        i = self.lineup.index(player)
        self.lineup.remove(player)
        self._retired.add(player)
        return i

    def is_available(self, player):
        return player not in self.retired

    def get_player_by_number(self, n):
        return [
            p for p in self.players
            if p.number == n
        ][0]

    def sub_player(self, entering: Player, leaving: Player):
        assert entering in self.bench

        i = self.retire(leaving)
        self.lineup.insert(i, entering)

    def print_lineup(self):
        result = []
        for player in self.lineup:
            result.append(f"#{player.number:>2} {player.pos.name:>2} {player.hand.name} {player.name}")
        print('\n'.join(result))


class Game:
    def __init__(self, teams=None):
        self.teams = teams or []

    def clean_row(self, n, row):
        return {
            'bt'    : int(row['BT']),
            'hand'  : Handedness[row['Handedness']],
            'name'  : row['Name'],
            'number': n,
            'obt'   : int(row['OBT']),
            'pd'    : PitcherDice[row['PD']] if row['PD'] else None,
            'pos'   : Positions[row['Position']],
            'traits': [ Traits[t] for t in row['Traits'].split() ],
        }

    def get_team_from_roster(self, filename) -> Team:
        with open(filename) as fh:
            reader = csv.DictReader(fh)
            roster = [ self.clean_row(n, row) for n, row in enumerate(reader) ]

        players = [ Player(**row) for row in roster ]
        team_name = filename.split('roster__')[-1].split('.')[0].replace('_', ' ').title()
        logging.debug("Loaded team '%s' from roster file: %s", team_name, filename)
        return Team(team_name, players=players)


if __name__ == '__main__':
    roster_filename_a = sys.argv[1]
    roster_filename_b = sys.argv[2]

    game = Game()
    game.teams.append(game.get_team_from_roster(roster_filename_a))
    game.teams.append(game.get_team_from_roster(roster_filename_b))

    if roster_filename_a == roster_filename_b:
        game.teams[1].name = "The Dopplegangers"

    for team in game.teams:
        team.set_lineup()
        team.print_lineup()
