from termcolor import colored

from enums import Hand, Positions


field = r'''
                  ___________________
            _____/                   \_____
        ___/                               \___
     __/                                       \__
   _/                     CF                      \_
 _/                                                 \_
/                                                     \
\           LF                           RF           /
  \                                                 /
    \                     R2                      /
      \              SS  .   .  2B              /
        \              .       .              /
          \      3B  .    PPP    .  1B      /
            \      R3      -      R1      /
              \      .           .      /
                \      .       .      /
                  \      .   .      /
                    \     BBB     /
                      \   CCC   /
                        \     /
                          \_/

'''

positions = {
    'BBB': (0, 'L'),
    'R1' : (1, 'R'),
    'R2' : (2, 'R'),
    'R3' : (3, 'R'),

    'PPP': (1, 'R'),
    'CCC': (2, 'R'),
    '1B' : (3, 'R'),
    '2B' : (4, 'R'),
    '3B' : (5, 'R'),
    'SS' : (6, 'R'),
    'LF' : (7, 'R'),
    'CF' : (8, 'R'),
    'RF' : (9, 'R'),
}

def color_field(field):
    # color field green
    field = field.replace('\\', colored('\\', 'light_green'))
    field = field.replace('/', colored('/', 'light_green'))
    field = field.replace('_', colored('_', 'light_green'))
    field = field.replace('.', colored('.', 'yellow'))
    return field

def print_field(game, field):
    field = color_field(field)
    assert 'PPP' in field

    # DRAW FIELDERS
    # draw pitcher
    player = game.inning.half.fielding.pitcher
    if player.hand == Hand.R:
        sub = f"{player.number:>3}"
    else:
        sub = f"{player.number:<3}"
    field = field.replace('PPP', colored(sub, game.inning.half.fielding.color))

    # draw fielders
    for player in game.inning.half.fielding.lineup:
        #print(player.name, player.pos.name, player.number)
        if player.pos.name == 'C':
            pos = 'CCC'
            if game.inning.half.batting.up_to_bat.hand == Hand.R:
                sub = f"{player.number:>3}"
            else:
                sub = f"{player.number:<3}"
        else:
            pos = player.pos.name
            sub = f"{player.number:>2}"
        field = field.replace(pos, colored(sub, game.inning.half.fielding.color))

    # DRAW BATTING TEAM
    # draw batter
    player = game.inning.half.batting.up_to_bat
    #print('batter:', player.name, player.number)
    if player.hand == Hand.R:
        sub = f"{player.number:<3}"
    else:
        sub = f"{player.number:>3}"
    field = field.replace('BBB', colored(sub, game.inning.half.batting.color))

    # draw runners
    #print('runners:')
    for base_number, player in enumerate(game.bases):
        base_number += 1
        pos = f"R{base_number}"
        if player:
            #print(player.name, player.number)
            sub = f"{player.number:>2}"
            field = field.replace(pos, colored(sub, game.inning.half.batting.color))
        else:
            sub = f"{'o':>2}"
            field = field.replace(pos, colored(sub, 'white'))

    print(field)


if __name__ == '__main__':
    field = color_field(field)

    for pos, info in positions.items():
        number, hand = info
        if len(pos) == 2:
            sub = f"{number:>2}"
        else:
            if pos == 'BBB':
                if hand == 'R':
                    sub = f"{number:<3}"
                else:
                    sub = f"{number:>3}"
            elif pos == 'CCC':
                batter_hand = positions['BBB'][1]
                if batter_hand == 'R':
                    sub = f"{number:>3}"
                else:
                    sub = f"{number:<3}"
            else:
                if hand == 'R':
                    sub = f"{number:>3}"
                else:
                    sub = f"{number:<3}"
        field = field.replace(pos, colored(sub, 'light_red'))

    print(field)
