from events import *


def hit_table(n):
    if 1 <= n <= 2:
        return [ Single() ]
    elif n == 3:
        return [ Single(), DefChance(Positions['1B']) ]
    elif n == 4:
        return [ Single(), DefChance(Positions['2B']) ]
    elif n == 5:
        return [ Single(), DefChance(Positions['3B']) ]
    elif n == 6:
        return [ Single(), DefChance(Positions['SS']) ]
    elif 7 <= n <= 9:
        return [ Single() ]
    elif 10 <= n <= 14:
        return [ Single(), RunnersAdvance(2) ]
    elif n == 15:
        return [ Double(), DefChance(Positions['LF']) ]
    elif n == 16:
        return [ Double(), DefChance(Positions['CF']) ]
    elif n == 17:
        return [ Double(), DefChance(Positions['RF']) ]
    elif n == 18:
        return [ Double(), RunnersAdvance(3) ]
    if 19 <= n <= 20:
        return [ HomeRun() ]

def swing_result_table(bt, obt, mss):
    if mss == 1 or mss == 99:
        return 'Oddity'
        # Roll 2d10 on Oddities Table.
    elif 2 <= mss <=5:
        return 'Critical Hit'
        # Roll d20 on Hit Table. Increase hit by one level—single to double, double to triple, etc.
    elif 6 <= mss <= bt:
        return 'Ordinary Hit'
        # Roll d20 on Hit Table.
    elif bt+1 <= mss <= obt:
        return 'Walk'
        # Batter advances to first.
    elif obt+1 <= mss <= obt+5:
        return 'Possible Error'
        # Roll d12 on Defense Table for fielder making the play.
    elif obt+6 <= mss <= 49:
        return 'Productive Out'
        # On a ball in the outfield or to the right of the infield, runners at second and third advance.
        # On a ball anywhere in the infield, a runner at first advances to second and the batter is out.
    elif 50 <= mss <= 69:
        return 'Productive Out'
        # On a ball in outfield or to the right of infield, runners at second and third advance.
        # On a ball anywhere in the infield, a runner at first is out and the
        # batter is safe at first on a fielder's choice.
    elif 70 <= mss <= 100:
        return 'Out'
        # Runners at second and third cannot advance on fly ball. On a ball
        # anywhere in the infield, both the runner at first and the batter are out.
    elif mss >= 100:
        return 'Out'
        # Out. Runners cannot advance on fly ball. Possible triple play.
