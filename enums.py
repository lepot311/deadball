from enum import Enum


Hand = Enum('Hand', ['L', 'R', 'S'])

PitcherDice = Enum('PitcherDice', [
    '-d4',
     'd4',
     'd8',
    'd12',
    'd20',
])

Positions = Enum('Positions', [
    'SP',
    'RP',
    'CP',
    'C',
    '1B',
    '2B',
    '3B',
    'SS',
    'LF',
    'CF',
    'RF',
    'DH',
])

Traits = Enum('Traits', [
    'C+',
    'C-',
    'CN+',
    'CN-',
    'CND-',
    'D+',
    'D-',
    'GB+',
    'K+',
    'P+',
    'P++',
    'P-',
    'P--',
    'S+',
    'S-',
    'ST+',
    'T+',
])

InningHalfName = Enum('InningHalfName', ['TOP', 'BOTTOM'])

pos_pitchers = (
    Positions.SP,
    Positions.RP,
    Positions.CP,
)
