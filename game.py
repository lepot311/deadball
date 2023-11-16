import csv
from enum import Enum
import logging
import random
import sys

from tabulate import tabulate

from enums import Handedness, PitcherDice, Positions, Traits, pos_pitchers


logging.basicConfig(filename='debug.log', level=logging.DEBUG)

# CONFIGURATION
N_INNINGS = 9


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
        self._players = set(players) if players else set()

        self._retired = set()
        self.lineup   = []
        self.bullpen  = { p for p in self.players if p.pos in pos_pitchers }
        self.pitcher  = None

        logging.debug("Inited team %s with %s ball players.", self.name, len(self.players))

    @property
    def players(self):
        return self._players

    @property
    def retired(self):
        return self._retired

    @property
    def bench(self):
        return self.players - set(self.lineup) - self.retired

    @property
    def starting_pitchers(self):
        return [ p for p in self.bullpen if p.pos.name == 'SP' ]

    def add_player(self, player: Player):
        self.players.add(player)
        if player.pd:
            self.bullpen.add(player)

    def set_lineup(self, numbers=None):
        numbers = numbers or list(range(1, 10))

        assert len(numbers) == 9, "Nine players are required to set a lineup."

        logging.debug("Setting lineup: %s", ', '.join([ str(n) for n in numbers ]))

        self.lineup = [
            self.get_player_by_number(n)
            for n in numbers
        ]

    def set_pitcher(self, player: Player):
        self.pitcher = player

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
        fields = [
            'number',
            'name',
            'hand',
            'pos',
            'bt',
            'obt',
            'pd',
            'traits',
        ]
        rows = []
        for i, player in enumerate(self.lineup):
            row = [i+1]
            for f in fields:
                value = getattr(player, f)
                if isinstance(value, Enum):
                    row.append(value.name)
                elif type(value) is list:
                    row.append(' '.join([ v.name for v in value ]))
                else:
                    row.append(value)
            rows.append(row)

        print(tabulate(
            rows,
            headers= ['ORDER'] + [ f.upper() for f in fields ],
            tablefmt='fancy_grid',
        ))

    def print_bullpen(self):
        fields = [
            'number',
            'name',
            'hand',
            'pos',
            'bt',
            'obt',
            'pd',
            'traits',
        ]
        rows = []
        for player in self.bullpen:
            row = []
            for f in fields:
                value = getattr(player, f)
                if isinstance(value, Enum):
                    row.append(value.name)
                elif type(value) is list:
                    row.append(' '.join([ v.name for v in value ]))
                else:
                    row.append(value)
            rows.append(row)

        print(tabulate(
            rows,
            headers= [ f.upper() for f in fields ],
            tablefmt='fancy_grid',
        ))


class Inning:
    def __init__(self, number: int, top: bool):
        self.number = number
        self.top    = top

        self.batting  = None
        self.fielding = None
        self.outs     = 0
        self.runs     = 0

    @property
    def name(self):
        half_name = "top" if self.top else "bottom"
        return f"{half_name} of the {self.number}"


class Game:
    def __init__(self, teams=None):
        self.teams   = teams or []
        self.innings = []

    @property
    def inning(self):
        return self.innings[-1]

    def clean_row(self, n, row):
        return {
            'bt'    : int(row['BT']),
            'hand'  : Handedness[row['Handedness']],
            'name'  : row['Name'],
            'number': n,
            'obt'   : int(row['OBT']),
            'pd'    : PitcherDice[row['PD']] if row['PD'] else PitcherDice['-d4'],
            'pos'   : Positions[row['Position']],
            'traits': [ Traits[t] for t in row['Traits'].split() ],
        }

    def get_team_from_roster(self, filename) -> Team:
        logging.debug("Loading roster file: %s", filename)

        with open(filename) as fh:
            reader = csv.DictReader(fh)
            roster = [ self.clean_row(n+1, row) for n, row in enumerate(reader) ]

        players = [ Player(**row) for row in roster ]
        team_name = filename.split('roster__')[-1].split('.')[0].replace('_', ' ').title()
        logging.debug("Loaded team '%s' from roster file: %s", team_name, filename)
        return Team(team_name, players=players)

    def play_at_bat(self):
        batter = game.inning.batting.lineup[0]
        # throw the pitch
        pitcher = game.inning.fielding.pitcher
        pd = pitcher.pd.name
        pitch_value = roll(pd)
        logging.info("Pitcher %s threw %s.", pitcher.name, pitch_value)
        # TODO
        self.inning.outs += 1
        import time
        time.sleep(1)

    def play_inning(self):
        print()
        print(f"Inning: {self.inning.name}")
        print("Now batting:", self.inning.batting.name)
        print()
        while self.inning.outs < 3:
            self.play_at_bat()
            print('outs', self.inning.outs)

    def play(self):
        inning_number = 1

        inning = Inning(inning_number, True)
        inning.batting  = self.teams[0]
        inning.fielding = self.teams[1]

        self.innings.append(inning)

        while self.inning.number < 4:
            # TODO go in to extra innings
            self.play_inning()

            # TODO create an InningHalf class
            #      maybe just use halfs instead of innings?

            # flip the inning half
            top = not self.inning.top

            # TODO remove this assert
            assert self.inning.top is not top

            # advance inning if we finished the bottom of an inning
            if top:
                inning_number += 1

            # TODO this sucks
            new_batting, new_fielding = inning.fielding, inning.batting

            inning = Inning(inning_number, top)
            inning.batting  = new_batting
            inning.fielding = new_fielding

            self.innings.append(inning)


if __name__ == '__main__':
    roster_filename_a = sys.argv[1]
    roster_filename_b = sys.argv[2]

    use_defaults = True

    game = Game()
    game.teams.append(game.get_team_from_roster(roster_filename_a))
    game.teams.append(game.get_team_from_roster(roster_filename_b))

    if roster_filename_a == roster_filename_b:
        game.teams[1].name = "The Dopplegangers"

    for team in game.teams:
        team.set_lineup()
        print()
        print(team.name)
        print()
        print("Lineup:")
        team.print_lineup()
        print()
        if not use_defaults:
            change_lineup = input("Change lineup? [y/N] ")
            if change_lineup.lower() in ('y', 'yes'):
                # TODO
                pass
        print("Bullpen:")
        team.print_bullpen()
        starting_pitcher = team.starting_pitchers[0]
        team.set_pitcher(starting_pitcher)
        print()
        print(f"Starting pitcher: {team.pitcher.name}")
        print()
        if not use_defaults:
            change_pitcher = input("Change starting pitcher? [y/N] ")
            if change_pitcher.lower() in ('y', 'yes'):
                # TODO
                pass

    # play ball!
    game.play()
