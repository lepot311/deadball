import pytest

import game


def make_player(n):
    return game.Player(
        number = n,
        name   = "Testy McTesterton",
        pos    = "P",
        hand   = "R",
        bt     = "20",
        obt    = "30",
        traits = "K+ CN-",
        pd     = "d8",
    )

@pytest.fixture
def player():
    return make_player(1)

@pytest.fixture
def empty_team():
    return game.Team("The Testers")

@pytest.fixture
def team():
    t = game.Team("The Testers")
    for n in range(40):
        player = make_player(n+1)
        t.players.add(player)
        if n < 9:
            t.lineup.append(player)
    return t
