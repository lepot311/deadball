import csv
import logging
import sys

from enums import Handedness, PitcherDice, Positions, Traits

logging.basicConfig(filename='debug.log', level=logging.DEBUG)


# CONFIGURATION
N_INNINGS = 9


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

    def retire(self, player: Player):
        self.lineup.remove(player)
        self._retired.add(player)

    def is_available(self, player):
        return player not in self.retired

    def get_player_by_number(self, n):
        return [
            p for p in self.players
            if p.number == n
        ][0]

    def print_lineup(self):
        result = []
        for player in self.lineup:
            result.append(f"#{player.number:>2} {player.pos.name:>2} {player.hand.name} {player.name}")
        print('\n'.join(result))


def clean_row(n, row):
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

def load_roster(filename):
    with open(roster_filename) as fh:
        reader = csv.DictReader(fh)
        return [ clean_row(n, row) for n, row in enumerate(reader) ]


if __name__ == '__main__':
    # load roster
    roster_filename = sys.argv[1]
    roster = load_roster(roster_filename)

    # init team
    team_name = roster_filename.split('roster__')[-1].split('.')[0].replace('_', ' ').title()

    print()
    print(team_name)
    print("=" * len(team_name))

    players = [ Player(**row) for row in roster ]
    team = Team(team_name, players=players)

    for player in team.players:
        print()
        print(player)

    team.set_lineup()
    team.print_lineup()
