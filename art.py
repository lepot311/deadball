from termcolor import colored


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

batting = {
    'BBB': (0, 'L'),
    'R1' : (1, 'R'),
    'R2' : (2, 'R'),
    'R3' : (3, 'R'),
}

fielding = {
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

if __name__ == '__main__':
    # color field green
    field = field.replace('\\', colored('\\', 'light_green'))
    field = field.replace('/', colored('/', 'light_green'))
    field = field.replace('_', colored('_', 'light_green'))
    field = field.replace('.', colored('.', 'light_yellow'))

    for pos, info in batting.items():
        number, hand = info
        if len(pos) == 2:
            sub = f"{number:>2}"
        else:
            if pos == 'BBB':
                if hand == 'R':
                    sub = f"{number:<3}"
                else:
                    sub = f"{number:>3}"
            else:
                if hand == 'R':
                    sub = f"{number:>3}"
                else:
                    sub = f"{number:<3}"
        field = field.replace(pos, colored(sub, 'light_red'))

    for pos, info in fielding.items():
        number, hand = info
        if len(pos) == 2:
            sub = f"{number:>2}"
        else:
            if pos == 'CCC':
                batter_hand = batting['BBB'][1]
                if batter_hand == 'R':
                    sub = f"{number:>3}"
                else:
                    sub = f"{number:<3}"
            else:
                if hand == 'R':
                    sub = f"{number:>3}"
                else:
                    sub = f"{number:<3}"
        field = field.replace(pos, colored(sub, 'light_blue'))

    print(field)
