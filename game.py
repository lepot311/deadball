import csv
import sys

from enums import Handedness, PitcherDice, Positions, Traits


# CONFIGURATION
N_INNINGS = 9


class BallPlayer:
    def __init__(self, name, pos, hand, bt, obt, traits=None, pd=None):
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

def clean_row(row):
    return {
        'bt'    : int(row['BT']),
        'hand'  : Handedness[row['Handedness']],
        'name'  : row['Name'],
        'obt'   : int(row['OBT']),
        'pd'    : PitcherDice[row['PD']] if row['PD'] else None,
        'pos'   : Positions[row['Position']],
        'traits': [ Traits[t] for t in row['Traits'].split() ],
    }

def load_roster(filename):
    with open(roster_filename) as fh:
        reader = csv.DictReader(fh)
        return [ clean_row(row) for row in reader ]


# load roster
roster_filename = sys.argv[1]
roster = load_roster(roster_filename)

# init team
team_name = roster_filename.split('roster__')[-1].split('.')[0].replace('_', ' ').title()

print()
print(team_name)
print("=" * len(team_name))

team = [ BallPlayer(**row) for row in roster ]
for player in team:
    print()
    print(player)
