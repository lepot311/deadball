import pytest

import game


def make_position_player(n):
    return game.Player(
        number = n,
        name   = "Testy McTesterton",
        pos    = "P",
        hand   = "R",
        bt     = "20",
        obt    = "30",
        traits = "K+ CN-",
    )

def make_pitcher(n):
    player = make_position_player(n)
    player.pd = 'd8'
    return player

@pytest.fixture
def player():
    return make_position_player(1)

@pytest.fixture
def empty_team():
    return game.Team("The Testers")

@pytest.fixture
def team():
    t = game.Team("The Testers")
    for n in range(30):
        player = make_position_player(n+1)
        t.add_player(player)
        if n < 9:
            t.lineup.append(player)
    for n in range(10):
        player = make_pitcher(n+11)
        t.add_player(player)
        if n == 11:
            t.pitcher = player
    return t
