from collections import UserList
import csv
from enum import Enum
import logging
import random
import sys

from tabulate import tabulate

from enums import Handedness, PitcherDice, Positions, Traits, InningHalfName, pos_pitchers


logging.basicConfig(filename='debug.log', level=logging.DEBUG)

# CONFIGURATION
N_INNINGS = 9


def roll(kind: str) -> int:
    # drop negative sign
    kind = kind.strip('-')
    count, n_sides = kind.split('d')
    count   = int(count) if count else 1
    n_sides = int(n_sides)
    result = 0
    for n in range(count):
        result += random.randrange(1, n_sides+1)
    logging.debug("Rolled %s -> %s", kind, result)
    return result


class BaseQueue(UserList):
    def __init__(self, game):
        self.game = game

        self.data = [ None ] * 3

    def clear(self):
        self.data = [ None ] * 3

    def get_player_at_base(self, n):
        assert 0 < n < 4, "Can only get base 1, 2, or 3."
        return self.data[n-1]

    def base_is_empty(self, n):
        return self.get_player_at_base(n) is None

    def check_for_runs(self):
        logging.debug("Runners: %s", self.data)
        if len(self.data) > 3:
            for p in self.data[3:]:
                if p:
                    self.game.runner_reached_home()
            self.data = self.data[:3]
        logging.debug("Runners after cleanup: %s", self.data)

    def advance_batter(self, n):
        if n >= 1:
            self.data.insert(0, self.game.inning.half.batting.up_to_bat)
            n_extra_bases = n-1
            for n in range(n_extra_bases):
                self.data.insert(0, None)
        self.check_for_runs()


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
            {self.name}
            {'-'*len(self.name)}
            Position: {self.pos.name} Handed: {self.hand.name}
            BT: {self.bt} OBT: {self.obt} {'PD:' if self.pd else ''} {self.pd.name if self.pd else ''}
            {'Traits:' if self.traits else ''} {' '.join([t.name for t in self.traits]) if self.traits else ''}
            '''.split('\n')
        ]).strip()


class Team:
    def __init__(self, name, players=None):
        self.name     = name
        self._players = set(players) if players else set()

        self.game      = None
        self._retired  = set()
        self._batter_n = -1
        self.lineup    = []
        self.bullpen   = { p for p in self.players if p.pos in pos_pitchers }
        self.pitcher   = None

        logging.debug("Inited team %s with %s ball players.", self.name, len(self.players))

    @property
    def halfs_at_bat(self):
        result = []
        for inning in self.game.innings:
            for half in inning.halfs:
                if half.batting == self:
                    result.append(half)
        return result


    @property
    def runs(self):
        return sum([ half.runs for half in self.halfs_at_bat ])

    @property
    def hits(self):
        return sum([ half.hits for half in self.halfs_at_bat ])

    @property
    def errors(self):
        return sum([ half.errors for half in self.halfs_at_bat ])

    @property
    def players(self):
        return self._players

    @property
    def up_to_bat(self):
        # TODO: you _could_ use a collections.deque here and rotate it
        return self.lineup[self._batter_n % 9]

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
        logging.debug("Added player %s to team %s", player.name, self)
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


class AtBat:
    def __init__(self, half):
        self.half = half

    def play(self):
        batter  = self.half.batting.up_to_bat
        pitcher = self.half.fielding.pitcher
        print()
        print("Now batting:")
        print(batter)
        # throw the pitch
        # TODO add mods
        pitch_value_multiplier = -1 if '-' in pitcher.pd.name else 1
        pitch_value = roll(pitcher.pd.name) * pitch_value_multiplier
        logging.info("Pitcher %s threw %s.", pitcher.name, pitch_value)

        # batter swings
        swing_value = roll('d100')
        logging.info("Batter %s swung %s.", batter.name, swing_value)

        mss = swing_value + pitch_value

        logging.debug("MSS=%s", mss)

        # TODO
        import time
        time.sleep(1)

        # TODO modify swing value

        # TODO implement swing result tables

        # TODO check rules to see if roll should be <= bt or < bt
        if swing_value <= batter.bt:
            logging.debug("HIT!")
            print()
            print("HIT!")
            print()
            # TODO every hit is a single for now
            self.game.single()
            self.half.hits += 1
        else:
            # TODO check out table
            self.half.outs += 1


class InningHalf:
    def __init__(self, inning, name: InningHalfName):
        self.inning = inning
        self.name   = name

        self.outs    = 0
        self.runs    = 0
        self.hits    = 0
        self.errors  = 0
        self.at_bats = []

        if self.name is InningHalfName.TOP:
            self.batting, self.fielding = self.inning.game.teams
        else:
            self.fielding, self.batting = self.inning.game.teams

    @property
    def at_bat(self):
        return self.at_bats[-1]

    def make_next_at_bat(self):
        self.batting._batter_n += 1
        self.at_bats.append(AtBat(self))

    def play(self):
        self.inning.game.print_scoreboard()

        logging.debug(f"Starting half: {self}")
        while self.outs < 3:
            # select next batter
            self.make_next_at_bat()
            self.at_bat.play()
            logging.debug("Outs: %s", self.outs)
        logging.debug(f"Ending half: {self}")

    def __str__(self):
        return f"{self.name.name} of the {self.inning.number}"


class Inning:
    def __init__(self, game, number: int):
        self.game   = game
        self.number = number

        self.halfs = []

    @property
    def half(self):
        return self.halfs[-1]

    @property
    def is_over(self):
        return (len(self.halfs) == 2) and (self.halfs[1].outs == 3)

    def make_next_half(self):
        if not self.halfs:
            half = InningHalf(self, InningHalfName.TOP)
        elif len(self.halfs) == 1:
            half = InningHalf(self, InningHalfName.BOTTOM)

        self.halfs.append(half)

    def play(self):
        while len(self.halfs) < 2:
            self.make_next_half()
            print()
            print(self.half)
            print()
            self.half.play()


class Game:
    def __init__(self, teams=None):
        self.teams   = teams or []
        self.innings = []

        self._n_inning = 0
        self.bases = BaseQueue(self)

    @property
    def inning(self):
        return self.innings[-1]

    @property
    def away(self):
        return self.teams[0]

    @property
    def home(self):
        return self.teams[1]

    def single(self):
        self.bases.advance_batter(1)

    def double(self):
        self.bases.advance_batter(2)

    def runner_reached_home(self):
        self.inning.half.runs += 1

    def clean_row(self, n, row):
        return {
            'number': n,
            'name'  : row['Name'],
            'hand'  : Handedness[row['Handedness']],
            'bt'    : int(row['BT']) if row['BT'] else None,
            'obt'   : int(row['OBT']) if row['OBT'] else None,
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

    def make_next_inning(self):
        self._n_inning += 1
        inning = Inning(self, self._n_inning)
        self.innings.append(inning)

    def print_scoreboard(self):
        n_innings = max(self._n_inning, N_INNINGS)
        # TODO clean up: merge these
        halfs_away = self.away.halfs_at_bat

        runs_away = []
        for n in range(n_innings):
            try:
                runs = halfs_away[n].runs
            except IndexError:
                runs = None
            runs_away.append(runs)


        halfs_home = []
        for inning in self.innings:
            for half in inning.halfs:
                if half.batting == self.home:
                    halfs_home.append(half)

        runs_home = []
        for n in range(n_innings):
            try:
                runs = halfs_home[n].runs
            except IndexError:
                runs = None
            runs_home.append(runs)

        rows = [
            ['Visitors', self.away.name] + runs_away + ['', self.away.runs, self.away.hits, self.away.errors],
            ['Home',     self.home.name] + runs_home + ['', self.home.runs, self.home.hits, self.home.errors],
        ]

        print(tabulate(
            rows,
            headers=['', 'Team'] + [ n+1 for n in range(n_innings) ] + ['', 'R', 'H', 'E'],
            tablefmt='fancy_grid',
        ))

    def play(self):
        while self._n_inning < N_INNINGS:
            self.make_next_inning()

            if not self.inning.is_over:
                # TODO go in to extra innings
                self.inning.play()


if __name__ == '__main__':
    roster_filename_a = sys.argv[1]
    roster_filename_b = sys.argv[2]

    use_defaults = True

    game = Game()
    team_away = game.get_team_from_roster(roster_filename_a)
    team_home = game.get_team_from_roster(roster_filename_b)
    team_away.game = game
    team_home.game = game
    game.teams = [team_away, team_home]

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
        starting_pitcher = random.choice(team.starting_pitchers)
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
    game.print_scoreboard()
